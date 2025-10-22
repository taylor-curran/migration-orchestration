#!/usr/bin/env python3
"""
Test file for Devin API structured output functionality.
Tests sessions that request agents to deliver structured output.
"""

import os
import time
import httpx
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from prefect import flow
from prefect.logging import get_run_logger
import json

load_dotenv()

# Import the existing session runner
from src.tasks.run_sessions import (
    create_session,
    get_session_status,
    send_sleep_message,
    wait_for_status,
    wait_for_analysis,
)


def get_structured_output(api_key: str, session_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve structured output from a session.
    This checks the 'structured_output' field in the session details.
    """
    url = f"https://api.devin.ai/v1/sessions/{session_id}"
    headers = {"Authorization": f"Bearer {api_key}"}

    with httpx.Client() as client:
        response = client.get(url, headers=headers)
        response.raise_for_status()

    data = response.json()
    return data.get("structured_output")


def poll_for_structured_output(
    api_key: str, session_id: str, max_polls: int = 60, poll_interval: int = 10
) -> Optional[Dict[str, Any]]:
    """
    Poll for structured output updates during session execution.
    Returns the latest structured output or None if not available.
    """
    logger = get_run_logger()
    structured_output = None

    for i in range(max_polls):
        current_output = get_structured_output(api_key, session_id)
        if current_output and current_output != structured_output:
            structured_output = current_output
            logger.info(f"📊 Structured output updated (poll {i + 1}):")
            logger.info(json.dumps(structured_output, indent=2))

        time.sleep(poll_interval)

    return structured_output


def create_session_with_structured_output(
    api_key: str, prompt: str, title: str, structured_schema: Dict[str, Any]
) -> str:
    """
    Create a session that requests structured output.
    Include the schema in the prompt for the agent to follow.
    """
    # Format the prompt to include structured output instructions
    formatted_prompt = f"""{prompt}

Please provide structured output in this exact JSON format:
{json.dumps(structured_schema, indent=2)}

Update the structured output as you work. Keep it simple and direct.
"""

    return create_session(api_key, formatted_prompt, title)


@flow(log_prints=True)
def test_migration_analysis_structured():
    """
    Test migration analysis with structured output.
    """
    logger = get_run_logger()
    api_key = os.environ.get("DEVIN_API_KEY")
    if not api_key:
        raise ValueError("DEVIN_API_KEY not found in environment")

    # SIMPLIFIED: Focus on what's essential for next agent
    migration_schema = {
        "completed": ["list of what's been migrated"],
        "remaining": ["list of what still needs migration"],
        "next_action": "specific next step to take",
        "blockers": ["any blocking issues"],
    }

    # Create the prompt with structured output request
    prompt = """!ask Carefully analyze the status of migration by comparing the source 
taylor-curran/og-cics-cobol-app repo to the target repo taylor-curran/target-springboot-cics
Determine the most advantageous next steps to take to make solid progress on the migration.

Focus on:
1. What has been completed
2. What remains to be done
3. Any blockers or issues
4. Specific actionable next steps with clear rationale"""

    logger.info("🚀 Starting Migration Analysis Test with Structured Output")

    # Create session with structured output
    session_id = create_session_with_structured_output(
        api_key, prompt, "Migration Analysis - Structured Output Test", migration_schema
    )

    logger.info(f"✅ Session created: {session_id}")

    # Start polling for structured output in parallel
    structured_output = None
    poll_count = 0
    max_polls = 90  # 30 minutes with 20-second intervals

    logger.info("📊 Starting to poll for structured output...")

    # Wait for session to reach blocked state while polling for output
    start_time = time.time()
    timeout = 2700  # 45 minutes

    while time.time() - start_time < timeout:
        # Check session status
        details = get_session_status(api_key, session_id)
        status = details.get("status_enum")

        # Get structured output
        current_output = get_structured_output(api_key, session_id)
        if current_output and current_output != structured_output:
            structured_output = current_output
            poll_count += 1
            logger.info(f"📊 Structured output update #{poll_count}:")
            logger.info(json.dumps(structured_output, indent=2))

        elapsed = int(time.time() - start_time)
        logger.debug(f"Status: {status} (elapsed: {elapsed}s)")

        if status in ["blocked", "finished", "expired"]:
            logger.info(f"✅ Session reached {status} state")
            break

        time.sleep(20)  # Poll every 20 seconds

    # Send sleep message if blocked
    if status == "blocked":
        logger.info("📨 Sending sleep message...")
        send_sleep_message(api_key, session_id)

    # Get final structured output
    final_output = get_structured_output(api_key, session_id)

    # Also get session analysis
    logger.info("⏳ Waiting for session analysis...")
    try:
        analysis = wait_for_analysis(api_key, session_id, 420, 20)
        logger.info("✅ Session analysis received")
    except TimeoutError:
        logger.warning("⚠️ Session analysis timeout")
        analysis = None

    # Return results
    result = {
        "session_id": session_id,
        "session_url": f"https://app.devin.ai/sessions/{session_id.replace('devin-', '')}",
        "structured_output": final_output,
        "structured_output_updates": poll_count,
        "analysis": analysis,
    }

    logger.info("\n📊 Test Results:")
    logger.info(f"Session ID: {result['session_id']}")
    logger.info(f"Session URL: {result['session_url']}")
    logger.info(f"Structured output updates received: {poll_count}")

    if final_output:
        logger.info("\n✅ Final Structured Output:")
        logger.info(json.dumps(final_output, indent=2))
    else:
        logger.warning("⚠️ No structured output received")

    return result


@flow(log_prints=True)
def test_pr_review_structured():
    """
    Test PR review with structured output format.
    """
    logger = get_run_logger()
    api_key = os.environ.get("DEVIN_API_KEY")
    if not api_key:
        raise ValueError("DEVIN_API_KEY not found in environment")

    # SIMPLIFIED: Just the essentials
    pr_review_schema = {
        "critical_issues": ["list of must-fix issues"],
        "improvements": ["suggested improvements"],
        "ready_to_merge": True,
    }

    prompt = """Review the migration orchestration code in src/ directory and provide a code review.
Look for:
- Code quality issues
- Potential bugs
- Performance concerns
- Best practices violations
- Suggestions for improvement"""

    logger.info("🚀 Starting PR Review Test with Structured Output")

    session_id = create_session_with_structured_output(
        api_key, prompt, "PR Review - Structured Output Test", pr_review_schema
    )

    # Similar polling logic as above
    structured_output = None
    start_time = time.time()
    timeout = 900  # 15 minutes for code review

    while time.time() - start_time < timeout:
        details = get_session_status(api_key, session_id)
        status = details.get("status_enum")

        current_output = get_structured_output(api_key, session_id)
        if current_output and current_output != structured_output:
            structured_output = current_output
            logger.info("📊 Structured output updated:")
            logger.info(json.dumps(structured_output, indent=2))

        if status in ["blocked", "finished", "expired"]:
            break

        time.sleep(15)

    if status == "blocked":
        send_sleep_message(api_key, session_id)

    return {
        "session_id": session_id,
        "session_url": f"https://app.devin.ai/sessions/{session_id.replace('devin-', '')}",
        "structured_output": structured_output,
    }


@flow(log_prints=True)
def test_progress_tracking_structured():
    """
    Test progress tracking with structured output.
    """
    logger = get_run_logger()
    api_key = os.environ.get("DEVIN_API_KEY")
    if not api_key:
        raise ValueError("DEVIN_API_KEY not found in environment")

    # SIMPLIFIED: Core progress info only
    progress_schema = {
        "status": "working | blocked | done",
        "percent_complete": 0,
        "current_task": "what I'm doing now",
    }

    prompt = """Analyze the test coverage of the migration orchestration codebase.
Identify:
1. Which components have tests
2. Which components lack tests  
3. Test coverage percentage estimate
4. Priority areas for new tests"""

    logger.info("🚀 Starting Progress Tracking Test with Structured Output")

    session_id = create_session_with_structured_output(
        api_key, prompt, "Test Coverage Analysis - Structured Output", progress_schema
    )

    # Track progress updates
    updates = []
    start_time = time.time()
    timeout = 600  # 10 minutes

    while time.time() - start_time < timeout:
        details = get_session_status(api_key, session_id)
        status = details.get("status_enum")

        current_output = get_structured_output(api_key, session_id)
        if current_output:
            updates.append(
                {"timestamp": time.time() - start_time, "output": current_output}
            )
            logger.info(f"📊 Progress update at {int(time.time() - start_time)}s:")
            logger.info(json.dumps(current_output, indent=2))

        if status in ["blocked", "finished", "expired"]:
            break

        time.sleep(10)

    if status == "blocked":
        send_sleep_message(api_key, session_id)

    return {
        "session_id": session_id,
        "session_url": f"https://app.devin.ai/sessions/{session_id.replace('devin-', '')}",
        "progress_updates": updates,
        "total_updates": len(updates),
    }


@flow(log_prints=True)
def test_simple_structured():
    """
    Ultra-simple structured output test.
    """
    logger = get_run_logger()
    api_key = os.environ.get("DEVIN_API_KEY")
    if not api_key:
        raise ValueError("DEVIN_API_KEY not found in environment")

    # Super simple schema
    simple_schema = {"finding": "what I discovered", "next_step": "what to do next"}

    prompt = (
        """Look at the README.md file in this project and tell me what it's about."""
    )

    logger.info("🚀 Starting Simple Structured Output Test")

    session_id = create_session_with_structured_output(
        api_key, prompt, "Simple Structured Output Test", simple_schema
    )

    # Wait and poll for output
    structured_output = None
    start_time = time.time()
    timeout = 300  # 5 minutes

    while time.time() - start_time < timeout:
        details = get_session_status(api_key, session_id)
        status = details.get("status_enum")

        current_output = get_structured_output(api_key, session_id)
        if current_output:
            structured_output = current_output
            logger.info("📊 Structured output received:")
            logger.info(json.dumps(structured_output, indent=2))

        if status in ["blocked", "finished", "expired"]:
            break

        time.sleep(10)

    if status == "blocked":
        send_sleep_message(api_key, session_id)

    return {"session_id": session_id, "structured_output": structured_output}


if __name__ == "__main__":
    import sys

    # Check for command line argument to choose test
    if len(sys.argv) > 1 and sys.argv[1] == "simple":
        # Run just the simple test
        print("\n" + "=" * 60)
        print("SIMPLE STRUCTURED OUTPUT TEST")
        print("=" * 60)
        result = test_simple_structured()
        print("\n✅ Test Complete")
        print(
            f"Structured output: {'Received' if result.get('structured_output') else 'Not received'}"
        )

    elif len(sys.argv) > 1 and sys.argv[1] == "migration":
        # Run just the migration test
        print("\n" + "=" * 60)
        print("MIGRATION ANALYSIS STRUCTURED OUTPUT TEST")
        print("=" * 60)
        migration_result = test_migration_analysis_structured()
        print("\n✅ Test Complete")
        print(
            f"Structured output: {'Received' if migration_result.get('structured_output') else 'Not received'}"
        )

    else:
        # Run all tests
        print("\n" + "=" * 60)
        print("DEVIN API STRUCTURED OUTPUT TESTS")
        print("=" * 60)

        # Test 1: Migration Analysis
        print("\n📋 Test 1: Migration Analysis with Structured Output")
        print("-" * 60)
        migration_result = test_migration_analysis_structured()

        # Test 2: PR Review
        print("\n📋 Test 2: PR Review with Structured Output")
        print("-" * 60)
        pr_result = test_pr_review_structured()

        # Test 3: Progress Tracking
        print("\n📋 Test 3: Progress Tracking with Structured Output")
        print("-" * 60)
        progress_result = test_progress_tracking_structured()

        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(
            f"✅ Migration Analysis: {'Structured output received' if migration_result.get('structured_output') else '❌ No output'}"
        )
        print(
            f"✅ PR Review: {'Structured output received' if pr_result.get('structured_output') else '❌ No output'}"
        )
        print(
            f"✅ Progress Tracking: {progress_result.get('total_updates', 0)} updates received"
        )
