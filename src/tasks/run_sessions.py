#!/usr/bin/env python3
"""
Devin API session management with structured output tracking.

Two-Phase Workflow:
Phase 1 - Session Working (run_session_until_blocked):
  1. Create session with prompt (and optional structured output schema)
  2. Monitor session status until 'blocked' state
  3. Track when structured output first appears

Phase 2 - Analysis Generation (generate_analysis):
  1. Send sleep message to trigger analysis
  2. Wait for session to reach sleeping state
  3. Collect analysis and final structured output
  4. Create artifacts (timeline, improvements, quick stats, structured output)
"""

import os
import time
import httpx
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from prefect import task
from prefect.logging import get_run_logger
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from utils.artifacts import (
    create_session_link_artifact,
    create_timeline_artifact,
    create_improvements_artifact,
    create_session_quick_stats_artifact,
    create_structured_output_artifact,
)

load_dotenv()

# Default poll interval (in seconds)
DEFAULT_POLL_INTERVAL = 10  # Check every 10 seconds


def create_session(
    api_key: str,
    prompt: str,
    title: Optional[str] = None,
    structured_output_schema: Optional[Dict[str, Any]] = None,
) -> str:
    """Create a new Devin session and return session_id.

    Args:
        api_key: Devin API key
        prompt: The task prompt for Devin
        title: Optional session title
        structured_output_schema: Optional schema fields to add directly to request body

    Returns:
        Session ID
    """
    logger = get_run_logger()

    url = "https://api.devin.ai/v1/sessions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    data = {
        "prompt": prompt,
        "title": title or "Orchestrated Session",
        "idempotent": False,
    }

    # Merge structured output schema fields directly into request body
    if structured_output_schema:
        data.update(structured_output_schema)
        logger.debug(
            f"Added schema fields to request: {list(structured_output_schema.keys())}"
        )

    with httpx.Client() as client:
        response = client.post(url, headers=headers, json=data)
        response.raise_for_status()

    result = response.json()
    session_id = result["session_id"]

    logger.info(f"✅ Session created: {session_id}")
    logger.info(f"   View at: {result['url']}")

    create_session_link_artifact(session_id, result["url"], title)

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
    logger = get_run_logger()

    url = f"https://api.devin.ai/v1/sessions/{session_id}/message"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"message": "sleep"}

    with httpx.Client() as client:
        response = client.post(url, headers=headers, json=data)
        response.raise_for_status()

    logger.info("💤 Sleep message sent - session ending and analysis triggered")


def wait_for_status(
    api_key: str,
    session_id: str,
    target_statuses: list,
    poll_interval: int = DEFAULT_POLL_INTERVAL,
    check_structured_output: bool = False,
) -> str:
    """Wait for session to reach one of the target statuses.

    Optionally also checks for structured output to see when it first appears.
    """

    start_time = time.time()
    logger = get_run_logger()
    first_structured_output_time = None
    previous_status = None

    # Status transition messages for better observability
    status_messages = {
        "planning": "📝 Planning phase",
        "working": "⚙️ Working on implementation",
        "blocked": "🛑 Blocked - waiting for input",
        "finished": "💤 Sleeping",
        "expired": "⏱️ Session expired",
    }

    while True:
        details = get_session_status(api_key, session_id)
        status = details.get("status_enum")

        elapsed = int(time.time() - start_time)

        # Log status transitions with meaningful messages
        if status != previous_status:
            # First status or transition
            if previous_status is None:
                logger.info(
                    f"   Initial status: {status_messages.get(status, status)} (at {elapsed}s)"
                )
            else:
                # Log important transitions
                if previous_status == "planning" and status == "working":
                    logger.info(
                        f"✅ Planning complete! Devin is now working on implementation (at {elapsed}s)"
                    )
                elif previous_status == "working" and status == "blocked":
                    logger.info(
                        f"🏁 Work phase complete! Session is now blocked (at {elapsed}s)"
                    )
                else:
                    logger.info(
                        f"   Status changed: {status_messages.get(previous_status, previous_status)} → {status_messages.get(status, status)} (at {elapsed}s)"
                    )
            previous_status = status
        else:
            # Still same status, use debug
            logger.debug(f"   Status: {status} (elapsed: {elapsed}s)")

        # Check for structured output if requested
        if check_structured_output and not first_structured_output_time:
            structured_output = details.get("structured_output")
            if structured_output:
                first_structured_output_time = elapsed
                logger.info(
                    f"🎯 STRUCTURED OUTPUT FIRST APPEARED at {elapsed}s after session start!"
                )
                logger.info(f"   Session status: {status}")
                logger.debug(
                    f"   Output preview: {json.dumps(structured_output, indent=2)[:300]}..."
                )

        if status in target_statuses:
            return status

        time.sleep(poll_interval)


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
    api_key: str, session_id: str, poll_interval: int = DEFAULT_POLL_INTERVAL
) -> Dict[str, Any]:
    """Wait for session analysis to become available."""

    start_time = time.time()
    logger = get_run_logger()

    while True:
        analysis = get_session_analysis(api_key, session_id)
        elapsed = int(time.time() - start_time)

        if analysis:
            logger.info(f"✅ Analysis available (elapsed: {elapsed}s)")
            return analysis

        logger.debug(f"   Analysis not ready (elapsed: {elapsed}s)")
        time.sleep(poll_interval)


def get_structured_output(api_key: str, session_id: str) -> Optional[Dict[str, Any]]:
    """Get structured output from session if available."""

    url = f"https://api.devin.ai/v1/sessions/{session_id}"
    headers = {"Authorization": f"Bearer {api_key}"}

    with httpx.Client() as client:
        response = client.get(url, headers=headers)
        response.raise_for_status()

    session_data = response.json()
    return session_data.get("structured_output")


@task(name="Devin Working")
def run_session_until_blocked(
    prompt: str,
    title: Optional[str] = None,
    api_key: Optional[str] = None,
    poll_interval: int = DEFAULT_POLL_INTERVAL,
    structured_output_schema: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Task 1: Create and run a Devin session until it reaches blocked state.

    This task handles the active work phase of the session.

    Args:
        prompt: The task prompt for Devin
        title: Optional session title
        api_key: Devin API key (uses env var if not provided)
        poll_interval: Polling interval in seconds (default: 10)
        structured_output_schema: Optional schema fields to add to request body

    Returns:
        Dict containing session_id, status, and timing information
    """
    logger = get_run_logger()
    start_time = time.time()

    # Setup
    if api_key is None:
        api_key = os.environ.get("DEVIN_API_KEY")
        if not api_key:
            raise ValueError("DEVIN_API_KEY not found in environment")

    logger.info("🚀 Starting Session Work Phase")
    logger.info(f"📋 Prompt: {prompt[:100]}...")

    # Step 1: Create session
    logger.info("[Step 1/2] Creating session...")
    session_id = create_session(api_key, prompt, title, structured_output_schema)

    # Step 2: Wait for blocked state (and check for structured output if schema provided)
    logger.info("[Step 2/2] Waiting for blocked or finished state...")

    # Enable structured output checking if schema was provided
    if structured_output_schema:
        logger.info("   📊 Also checking for when structured output appears...")

    status = wait_for_status(
        api_key,
        session_id,
        ["blocked", "finished", "expired"],  # Note: finished = sleeping
        poll_interval=poll_interval,
        check_structured_output=(structured_output_schema is not None),
    )

    logger.info(f"✅ Session reached {status} state")

    # Return session info and status
    session_url = f"https://app.devin.ai/sessions/{session_id.replace('devin-', '')}"
    execution_time = time.time() - start_time

    return {
        "session_id": session_id,
        "session_url": session_url,
        "status": status,
        "execution_time": execution_time,
        "api_key": api_key,  # Pass through for next task
        "poll_interval": poll_interval,  # Pass through for next task
        "has_schema": structured_output_schema
        is not None,  # Pass through for next task
        "title": title,  # Pass through for artifacts
    }


@task(name="Devin Session Analysis")
def generate_analysis(
    session_info: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Task 2: Send sleep message and wait for analysis generation.

    This task handles the analysis generation phase after the session has completed its work.

    Args:
        session_info: Output from run_session_until_blocked task containing session details

    Returns:
        Dict containing analysis and structured output
    """
    logger = get_run_logger()
    start_time = time.time()

    # Extract info from previous task
    session_id = session_info["session_id"]
    session_url = session_info["session_url"]
    status = session_info["status"]
    api_key = session_info["api_key"]
    poll_interval = session_info["poll_interval"]
    has_schema = session_info["has_schema"]
    title = session_info.get("title")

    logger.info("📊 Starting Analysis Generation Phase")
    logger.info(f"   Session: {session_id}")
    logger.info(f"   Current status: {status}")

    # Handle different statuses
    if status != "blocked":
        logger.warning(f"⚠️  Session ended with status: {status}")
        if status == "finished":  # finished = sleeping
            # Already sleeping, skip to analysis
            logger.info("   Session already sleeping, checking for analysis...")
        else:
            raise ValueError(f"Unexpected session status: {status}")
    else:
        # Step 1: Send sleep message to end session
        logger.info("[Step 1/3] Sending sleep message to trigger analysis...")
        send_sleep_message(api_key, session_id)

        # Step 2: Wait for sleeping state
        logger.info("[Step 2/3] Waiting for sleeping state...")
        status = wait_for_status(
            api_key,
            session_id,
            ["finished", "expired"],
            poll_interval=poll_interval,
        )

        if status != "finished":  # finished = sleeping
            raise ValueError(f"Session ended with status: {status}")

    # Step 3: Wait for session analysis and get final structured output
    logger.info("[Step 3/3] Waiting for session analysis...")
    analysis = wait_for_analysis(api_key, session_id, poll_interval=poll_interval)

    # Get final structured output if schema was provided
    structured_output = None
    if has_schema:
        logger.info("   Getting final structured output...")
        structured_output = get_structured_output(api_key, session_id)
        if structured_output:
            logger.info("   ✅ Final structured output retrieved")
        else:
            logger.warning("   ⚠️  No structured output available at session end")

    logger.info("✅ Analysis generation complete!")

    # Create artifacts with all the session analysis details
    if analysis:
        logger.info("📄 Creating artifacts...")

        # Create timeline artifact (issues and timeline)
        create_timeline_artifact(session_id, session_url, analysis)

        # Create improvements artifact (prompt suggestions and action items)
        create_improvements_artifact(session_id, analysis)

        # Create session quick stats artifact
        execution_time = time.time() - start_time
        create_session_quick_stats_artifact(
            session_id=session_id,
            session_url=session_url,
            analysis=analysis,
            execution_time=execution_time,
            title=title,
        )

        # Create structured output artifact if available
        if structured_output:
            create_structured_output_artifact(session_id, structured_output)
            logger.info("✅ Structured output artifact created")

        logger.info("✅ Artifacts created successfully")

    # Extract the improved prompt from nested structure
    # API returns: {"suggested_prompt": {"suggested_prompt": "...", "original_prompt": "...", ...}}
    suggested_prompt_data = analysis.get("suggested_prompt") if analysis else None
    improved_prompt = None
    if suggested_prompt_data and isinstance(suggested_prompt_data, dict):
        improved_prompt = suggested_prompt_data.get("suggested_prompt")

    return {
        "session_id": session_id,
        "session_url": session_url,
        "analysis": analysis,
        "suggested_prompt": improved_prompt,  # Now returns the actual improved prompt text
        "suggested_prompt_data": suggested_prompt_data,  # Full data including original and improved
        "structured_output": structured_output,  # Structured output from the session
        "execution_time": execution_time,
    }


@task(name="Run Session with Analysis")
def run_session_and_wait_for_analysis(
    prompt: str,
    title: Optional[str] = None,
    api_key: Optional[str] = None,
    poll_interval: int = DEFAULT_POLL_INTERVAL,
    structured_output_schema: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Main orchestration task that runs a Devin session by coordinating two sub-tasks.

    This task orchestrates:
    1. run_session_until_blocked - Creates and runs session until blocked
    2. generate_analysis - Sends sleep message and collects analysis

    Args:
        prompt: The task prompt for Devin
        title: Optional session title
        api_key: Devin API key (uses env var if not provided)
        poll_interval: Polling interval in seconds (default: 10)
        structured_output_schema: Optional schema fields to add to request body

    Returns:
        Dict containing session_id, session_url, analysis, suggested_prompt, and structured_output
    """
    logger = get_run_logger()

    logger.info("🎯 Orchestrating Devin Session with Two-Phase Execution")

    # Phase 1: Run session until blocked
    logger.info("── Phase 1: Session Working ──")
    session_info = run_session_until_blocked(
        prompt=prompt,
        title=title,
        api_key=api_key,
        poll_interval=poll_interval,
        structured_output_schema=structured_output_schema,
    )

    # Phase 2: Generate analysis
    logger.info("── Phase 2: Analysis Generation ──")
    result = generate_analysis(session_info)

    logger.info("✅ Full orchestration complete!")

    return result


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

    result = run_session_and_wait_for_analysis(
        prompt=example_prompt, title="Fibonacci Function", poll_interval=10
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
