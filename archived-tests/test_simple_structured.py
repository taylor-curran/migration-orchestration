#!/usr/bin/env python3
"""
Simplified structured output test - focusing only on essentials.

Key insight: Keep the schema simple so the agent focuses on analysis,
not on filling out a complex form.
"""

import os
import time
import httpx
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


# SIMPLIFIED SCHEMA - Just the essentials
SIMPLE_RECOMMENDATIONS_SCHEMA = {
    "next_actions": [
        {
            "what": "Clear description of what to do",
            "why": "Why this is important",
            "done_when": "How to know it's complete",
        }
    ],
    "current_state": "Brief summary of where we are in the migration",
    "blockers": ["List any major issues blocking progress"],
}


def create_session_with_simple_schema(
    api_key: str, base_prompt: str, title: str = "Migration Analysis"
) -> str:
    """
    Create a session with simplified structured output.
    """
    # Add simple schema to prompt
    enhanced_prompt = f"""
{base_prompt}

Throughout your analysis, maintain this simple structured output:

{json.dumps(SIMPLE_RECOMMENDATIONS_SCHEMA, indent=2)}

Keep updating this structure as you discover important information.
Focus on actionable next steps with clear completion criteria.
"""

    url = "https://api.devin.ai/v1/sessions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    data = {"prompt": enhanced_prompt, "title": title, "idempotent": False}

    print(f"📝 Creating session with simplified schema...")

    with httpx.Client() as client:
        response = client.post(url, headers=headers, json=data)
        response.raise_for_status()

    result = response.json()
    session_id = result["session_id"]

    print(f"✅ Session created: {session_id}")
    print(f"🔗 View at: {result['url']}")

    return session_id


def get_simple_recommendations(
    api_key: str, session_id: str
) -> Optional[Dict[str, Any]]:
    """
    Get structured output from session.
    """
    url = f"https://api.devin.ai/v1/sessions/{session_id}"
    headers = {"Authorization": f"Bearer {api_key}"}

    with httpx.Client() as client:
        response = client.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get("structured_output")
    return None


def display_simple_results(structured: Dict[str, Any]):
    """
    Display the simple structured results clearly.
    """
    print("\n" + "=" * 60)
    print("📊 ANALYSIS RESULTS")
    print("=" * 60)

    # Current state
    state = structured.get("current_state", "Unknown")
    print(f"\n📍 Current State:")
    print(f"   {state}")

    # Blockers
    blockers = structured.get("blockers", [])
    if blockers and any(b for b in blockers if b):  # Check for non-empty blockers
        print(f"\n⚠️ Blockers ({len(blockers)}):")
        for blocker in blockers:
            if blocker:  # Only show non-empty
                print(f"   • {blocker}")
    else:
        print(f"\n✅ No major blockers identified")

    # Next actions
    actions = structured.get("next_actions", [])
    print(f"\n🎯 Next Actions ({len(actions)} total):")
    print("-" * 40)

    for idx, action in enumerate(actions, 1):
        print(f"\n{idx}. WHAT: {action.get('what', 'No description')}")
        print(f"   WHY:  {action.get('why', 'No reason given')}")
        print(f"   DONE: {action.get('done_when', 'No completion criteria')}")


def test_existing_session(api_key: str, session_id: str):
    """
    Test retrieving data from an existing session.
    """
    print(f"\n🔍 Checking session: {session_id}")

    structured = get_simple_recommendations(api_key, session_id)

    if structured:
        print("✅ Structured output found")

        # Check if it matches our simple schema
        has_simple = all(key in structured for key in ["next_actions", "current_state"])

        if has_simple:
            print("   Using simple schema format")
            display_simple_results(structured)
        else:
            # Show what we got instead
            print("   Different schema detected:")
            if "next_steps" in structured:
                steps = structured.get("next_steps", [])
                print(f"\n   Found {len(steps)} next_steps")
                for i, step in enumerate(steps[:3], 1):  # Show first 3
                    print(f"   {i}. {step.get('title', 'Untitled')}")
                    print(f"      {step.get('description', '')[:100]}...")

            if "migration_analysis" in structured:
                analysis = structured["migration_analysis"]
                status = analysis.get("current_status", "")
                if status:
                    print(f"\n   Migration Status: {status[:150]}...")

        return structured
    else:
        print("⚠️ No structured output available")
        return None


def main():
    """
    Main test function.
    """
    api_key = os.environ.get("DEVIN_API_KEY")
    if not api_key:
        print("❌ DEVIN_API_KEY not found")
        return

    print("\n" + "=" * 60)
    print("SIMPLE STRUCTURED OUTPUT TEST")
    print("=" * 60)

    # Test 1: Check existing session
    existing_id = "devin-32b7f51018564cde93ea0937b4eeca7a"
    existing_data = test_existing_session(api_key, existing_id)

    # Test 2: Create new session with simple schema (optional)
    create_new = (
        input("\n\nCreate new session with simple schema? (y/n): ").lower() == "y"
    )

    if create_new:
        print("\n" + "=" * 60)
        print("CREATING NEW SESSION")
        print("=" * 60)

        simple_prompt = """
        !ask Analyze migration status: compare taylor-curran/og-cics-cobol-app 
        to taylor-curran/target-springboot-cics
        
        Focus on:
        1. What percentage is complete
        2. What should be done next (top 3-5 actions)
        3. What's blocking progress
        
        Be concise and action-oriented.
        """

        new_session_id = create_session_with_simple_schema(
            api_key, simple_prompt, "Simple Migration Analysis"
        )

        print("\n⏳ Session will run in background...")
        print("   Poll periodically to check for structured output")
        print(f"   Session: {new_session_id}")

        # Optional: Poll for a bit to see if we get quick results
        print("\n📡 Polling for structured output (30 seconds)...")
        for i in range(6):  # Poll for 30 seconds
            time.sleep(5)
            result = get_simple_recommendations(api_key, new_session_id)
            if result:
                print(f"✅ Got structured output after {(i + 1) * 5} seconds")
                display_simple_results(result)
                break
            else:
                print(f"   Attempt {i + 1}/6 - no data yet")

        if not result:
            print("\n⏰ Session still running - check later")
            print(
                f"   https://app.devin.ai/sessions/{new_session_id.replace('devin-', '')}"
            )


if __name__ == "__main__":
    main()
