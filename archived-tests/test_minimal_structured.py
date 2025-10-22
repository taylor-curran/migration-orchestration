#!/usr/bin/env python3
"""
Ultra-minimal structured output - just a prioritized task list.

The simplest possible structure that still provides value.
"""

import os
import httpx
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


# ULTRA-MINIMAL SCHEMA - Just tasks
MINIMAL_SCHEMA = {
    "tasks": [
        "Task 1: Clear action with completion criteria",
        "Task 2: Another action with how to know it's done",
        "Task 3: etc...",
    ],
    "status": "X% complete - brief summary",
}


def create_minimal_session(api_key: str) -> str:
    """
    Create session with minimal structure - just a task list.
    """
    prompt = """
    !ask Analyze migration from taylor-curran/og-cics-cobol-app to taylor-curran/target-springboot-cics
    
    Provide a simple structured output with:
    - "tasks": List of 5 tasks that can be worked on IN PARALLEL (independent tasks that different developers could do simultaneously)
    - "status": Current migration percentage and one-line summary
    
    IMPORTANT: All 5 tasks should be independent - they should NOT depend on each other.
    
    Example format:
    {
        "tasks": [
            "Task 1: Create tests for CreditAgencyService - Done when all methods have unit tests with >80% coverage",
            "Task 2: Create tests for ErrorLoggingService - Done when all methods have unit tests with >80% coverage",
            "Task 3: Document API endpoints - Done when all REST endpoints have OpenAPI documentation",
            "Task 4: Add integration tests for repositories - Done when each repository has integration tests",
            "Task 5: Create migration guide - Done when README has clear migration status and instructions"
        ],
        "status": "14% complete - 4 of 29 programs migrated, core infrastructure in place"
    }
    
    Remember: These 5 tasks should be things that can be done SIMULTANEOUSLY by different people.
    Keep updating this structure as you analyze. Be specific and actionable.
    """

    url = "https://api.devin.ai/v1/sessions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    data = {"prompt": prompt, "title": "Minimal Migration Tasks", "idempotent": False}

    print("📝 Creating session with minimal schema (just tasks)...")

    with httpx.Client() as client:
        response = client.post(url, headers=headers, json=data)
        response.raise_for_status()

    result = response.json()
    session_id = result["session_id"]

    print(f"✅ Session: {session_id}")
    print(f"🔗 {result['url']}")

    return session_id


def check_and_display(api_key: str, session_id: str) -> bool:
    """
    Check for structured output and display if available.
    Returns True if data was found.
    """
    url = f"https://api.devin.ai/v1/sessions/{session_id}"
    headers = {"Authorization": f"Bearer {api_key}"}

    with httpx.Client() as client:
        response = client.get(url, headers=headers)
        if response.status_code != 200:
            return False

        data = response.json()
        structured = data.get("structured_output")

        if not structured:
            return False

        # Display results
        print("\n" + "=" * 60)
        print("📋 MIGRATION TASKS")
        print("=" * 60)

        # Status
        status = structured.get("status", "Unknown")
        print(f"\n📊 Status: {status}")

        # Tasks
        tasks = structured.get("tasks", [])
        if tasks:
            print(f"\n🎯 Next Actions ({len(tasks)} tasks):")
            print("-" * 40)
            for i, task in enumerate(tasks, 1):
                print(f"\n{i}. {task}")
        else:
            # Might have different structure
            if "next_steps" in structured:
                steps = structured["next_steps"]
                print(f"\n🎯 Found {len(steps)} next_steps (different schema)")
                for step in steps[:3]:
                    print(f"\n• {step.get('title', 'Untitled')}")
                    print(f"  {step.get('definition_of_done', 'No criteria')}")

        return True


def main():
    api_key = os.environ.get("DEVIN_API_KEY")
    if not api_key:
        print("❌ DEVIN_API_KEY not found")
        return

    print("\n" + "=" * 60)
    print("MINIMAL STRUCTURED OUTPUT TEST")
    print("=" * 60)

    # First check the existing session
    print("\n1️⃣ Checking existing session...")
    existing_id = "devin-32b7f51018564cde93ea0937b4eeca7a"

    if check_and_display(api_key, existing_id):
        print("\n✅ Retrieved data from existing session")
    else:
        print("⚠️ No structured data in existing session")

    # Option to create new minimal session
    print("\n" + "-" * 40)
    create_new = (
        input("\n2️⃣ Test new session with minimal schema? (y/n): ").lower() == "y"
    )

    if create_new:
        new_id = create_minimal_session(api_key)
        print("\n⏳ Session started - it will run in background")
        print("   Check progress at the URL above")
        print("   Run this script again later with the session ID to see results")
        print(f"\n   Session ID: {new_id}")


if __name__ == "__main__":
    main()
