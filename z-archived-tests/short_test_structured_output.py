#!/usr/bin/env python3
"""
Quick test for structured output with Devin API.
Simple, fast-completing task to verify structured output functionality.
"""

from prefect import flow
from tasks.run_sessions import run_session_and_wait_for_analysis
from typing import Optional, Dict, Any
import json


@flow(log_prints=True)
def test_quick_structured_output(
    prompt: str, title: str, structured_output_schema: Optional[Dict[str, Any]] = None
):
    """
    Run a quick test with structured output.

    Args:
        prompt: The task prompt for Devin
        title: Session title
        structured_output_schema: Schema fields to include in request body
    """
    result = run_session_and_wait_for_analysis(
        prompt=prompt,
        title=title,
        structured_output_schema=structured_output_schema,
    )
    return result


if __name__ == "__main__":
    # Simple schema for a quick analysis task
    structured_output_schema = {
        "result": {"fibonacci_10": None, "is_prime_17": None, "factorial_5": None},
        "status": "not_started",
        "completion_percentage": 0,
    }

    # Simple, fast-completing prompt that references the schema
    prompt = """
!ask Complete this quick math analysis task.

Please provide structured output in this exact JSON format by updating the fields in the request:

1. Calculate the 10th Fibonacci number and update result.fibonacci_10
2. Determine if 17 is prime and update result.is_prime_17 with true/false
3. Calculate 5! (factorial) and update result.factorial_5
4. Update status to "completed" when done
5. Update completion_percentage as you progress (0, 33, 66, 100)

This is a simple test - just calculate and update the structured output immediately.
"""

    title = "Quick Structured Output Test - Math"

    # Run the test
    print("🚀 Starting quick structured output test...")
    print(
        f"📋 Schema being sent in request body: {json.dumps(structured_output_schema, indent=2)}\n"
    )

    result = test_quick_structured_output(
        prompt=prompt, title=title, structured_output_schema=structured_output_schema
    )

    # Display results
    if result:
        print("\n✅ Session completed successfully")

        if result.get("structured_output"):
            print("\n📊 Structured Output Retrieved:")
            print(json.dumps(result["structured_output"], indent=2))
        else:
            print("\n⚠️ No structured output found in response")

        if result.get("session_analysis"):
            print("\n📝 Session Analysis:")
            print(json.dumps(result["session_analysis"], indent=2))
    else:
        print("\n❌ Test failed - no result returned")
