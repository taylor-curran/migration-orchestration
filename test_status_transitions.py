#!/usr/bin/env python3
"""
Quick test to see status transition logging.
"""

from prefect import flow
from src.tasks.run_sessions import run_session_until_blocked


@flow(name="Test Status Transitions", log_prints=True)
def test_status_transitions():
    """
    Test to observe the enhanced status transition logging.
    """

    test_prompt = """
    Create a simple Python function that adds two numbers.
    Include a docstring.
    
    Definition of done:
    - Function complete
    - Has docstring
    """

    # Run session and watch the status transitions
    result = run_session_until_blocked(
        prompt=test_prompt,
        title="Status Transition Test",
        poll_interval=5,  # Faster polling to see transitions sooner
    )

    print(f"\n✅ Session reached: {result['status']}")
    print(f"🔗 Session URL: {result['session_url']}")

    return result


if __name__ == "__main__":
    test_status_transitions()
