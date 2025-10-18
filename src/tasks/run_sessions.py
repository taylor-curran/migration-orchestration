#!/usr/bin/env python3
"""
Simple orchestrator for Devin API sessions with session analysis.

Workflow:
1. Create session with prompt
2. Wait for session to reach 'blocked' state
3. Send message to move to 'sleeping' state
4. Wait for session analysis to become available
"""

import os
import time
import httpx
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from prefect import task

load_dotenv()

# Default timeouts (in seconds)
DEFAULT_TIMEOUTS = {
    "blocked_wait": 2700,  # 45 minutes for session to reach blocked
    "sleeping_wait": 300,  # 5 minutes to switch to sleeping
    "analysis_wait": 420,  # 7 minutes for analysis to be ready
    "poll_interval": 20,  # Check every 20 seconds
}


def create_session(api_key: str, prompt: str, title: Optional[str] = None) -> str:
    """Create a new Devin session and return session_id."""

    url = "https://api.devin.ai/v1/sessions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    data = {
        "prompt": prompt,
        "title": title or "Orchestrated Session",
        "idempotent": False,
    }

    with httpx.Client() as client:
        response = client.post(url, headers=headers, json=data)
        response.raise_for_status()

    result = response.json()
    session_id = result["session_id"]

    print(f"✅ Session created: {session_id}")
    print(f"   View at: {result['url']}")

    return session_id


def get_session_status(api_key: str, session_id: str) -> Dict[str, Any]:
    """Get current session details including status."""

    url = f"https://api.devin.ai/v1/sessions/{session_id}"
    headers = {"Authorization": f"Bearer {api_key}"}

    with httpx.Client() as client:
        response = client.get(url, headers=headers)
        response.raise_for_status()

    return response.json()


def send_sleep_message(api_key: str, session_id: str) -> None:
    """Send 'sleep' message to end the session and trigger analysis."""

    url = f"https://api.devin.ai/v1/sessions/{session_id}/message"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    data = {"message": "sleep"}

    with httpx.Client() as client:
        response = client.post(url, headers=headers, json=data)
        response.raise_for_status()

    print("📨 Sleep message sent - ending session")


def wait_for_status(
    api_key: str,
    session_id: str,
    target_statuses: list,
    timeout: int,
    poll_interval: int,
) -> str:
    """Wait for session to reach one of the target statuses."""

    start_time = time.time()

    while time.time() - start_time < timeout:
        details = get_session_status(api_key, session_id)
        status = details.get("status_enum")

        elapsed = int(time.time() - start_time)
        print(f"   Status: {status} (elapsed: {elapsed}s)")

        if status in target_statuses:
            return status

        time.sleep(poll_interval)

    raise TimeoutError(f"Session did not reach {target_statuses} within {timeout}s")


def get_session_analysis(api_key: str, session_id: str) -> Optional[Dict[str, Any]]:
    """Get session analysis from enterprise endpoint."""

    url = f"https://api.devin.ai/beta/v2/enterprise/sessions/{session_id}"
    headers = {"Authorization": f"Bearer {api_key}"}

    with httpx.Client() as client:
        response = client.get(url, headers=headers)
        response.raise_for_status()

    data = response.json()
    return data.get("session_analysis")


def wait_for_analysis(
    api_key: str, session_id: str, timeout: int, poll_interval: int
) -> Dict[str, Any]:
    """Wait for session analysis to become available."""

    start_time = time.time()

    while time.time() - start_time < timeout:
        analysis = get_session_analysis(api_key, session_id)

        elapsed = int(time.time() - start_time)

        if analysis:
            print(f"✅ Analysis available (elapsed: {elapsed}s)")
            return analysis

        print(f"   Analysis not ready (elapsed: {elapsed}s)")
        time.sleep(poll_interval)

    raise TimeoutError(f"Session analysis not available within {timeout}s")

@task
def run_session_and_wait_for_analysis(
    prompt: str,
    title: Optional[str] = None,
    api_key: Optional[str] = None,
    timeouts: Optional[Dict[str, int]] = None,
) -> Dict[str, Any]:
    """
    Main orchestration function that runs the complete workflow.

    Args:
        prompt: The task prompt for Devin
        title: Optional session title
        api_key: Devin API key (uses env var if not provided)
        timeouts: Optional timeout overrides

    Returns:
        Dict containing session_id and analysis data
    """

    # Setup
    if api_key is None:
        api_key = os.environ.get("DEVIN_API_KEY")
        if not api_key:
            raise ValueError("DEVIN_API_KEY not found in environment")

    config = DEFAULT_TIMEOUTS.copy()
    if timeouts:
        config.update(timeouts)

    print("\n🚀 Starting Devin Session Orchestration")
    print(f"📋 Prompt: {prompt[:100]}...")

    # Step 1: Create session
    print("\n[Step 1/4] Creating session...")
    session_id = create_session(api_key, prompt, title)

    # Step 2: Wait for blocked state
    print(f"\n[Step 2/4] Waiting for blocked state (max {config['blocked_wait']}s)...")
    status = wait_for_status(
        api_key,
        session_id,
        ["blocked", "finished", "expired"],  # Note: finished = sleeping
        config["blocked_wait"],
        config["poll_interval"],
    )

    if status != "blocked":
        print(f"⚠️  Session ended with status: {status}")
        if status == "finished":  # finished = sleeping
            # Already sleeping, skip to analysis
            print("   Session already sleeping, checking for analysis...")
        else:
            raise ValueError(f"Unexpected session status: {status}")
    else:
        # Step 3: Send sleep message to end session
        print("\n[Step 3/4] Sending sleep message to end session...")
        send_sleep_message(api_key, session_id)

        # Wait for sleeping state
        print(f"   Waiting for sleeping state (max {config['sleeping_wait']}s)...")
        status = wait_for_status(
            api_key,
            session_id,
            ["finished", "expired"],
            config["sleeping_wait"],
            config["poll_interval"],
        )

        if status != "finished":  # finished = sleeping
            raise ValueError(f"Session ended with status: {status}")

    # Step 4: Wait for session analysis
    print(
        f"\n[Step 4/4] Waiting for session analysis (max {config['analysis_wait']}s)..."
    )
    analysis = wait_for_analysis(
        api_key, session_id, config["analysis_wait"], config["poll_interval"]
    )

    print("\n✅ Orchestration complete!")

    return {
        "session_id": session_id,
        "session_url": f"https://app.devin.ai/sessions/{session_id.replace('devin-', '')}",
        "analysis": analysis,
        "suggested_prompt": analysis.get("suggested_prompt"),
    }


if __name__ == "__main__":
    # Example usage
    example_prompt = """
    Create a simple Python function that calculates fibonacci numbers.
    Include docstring and type hints.
    
    Definition of done:
    - Function is complete and working
    - Has proper documentation
    - Includes example usage
    """

    test_timeouts = {
        "blocked_wait": 360,  # 6 minutes for session to reach blocked
        "sleeping_wait": 300,  # 5 minutes to switch to sleeping
        "analysis_wait": 240,  # 4 minutes for analysis to be ready
        "poll_interval": 10,  # Check every 10 seconds
    }

    result = run_session_and_wait_for_analysis(
        prompt=example_prompt, title="Fibonacci Function", timeouts=test_timeouts
    )

    print("\n📊 Session Analysis Summary:")
    if result["analysis"]:
        if "issues" in result["analysis"]:
            print(f"   Issues found: {len(result['analysis']['issues'])}")
        if "action_items" in result["analysis"]:
            print(f"   Action items: {len(result['analysis']['action_items'])}")
        if "timeline" in result["analysis"]:
            print(f"   Timeline events: {len(result['analysis']['timeline'])}")

    print(f"\n🔗 Session URL: {result['session_url']}")
