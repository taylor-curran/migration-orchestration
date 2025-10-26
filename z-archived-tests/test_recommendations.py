#!/usr/bin/env python3
"""
Test file for getting structured recommendations from Devin sessions.

This demonstrates how to:
1. Create sessions with structured output schema for recommendations
2. Retrieve the structured recommendations from sessions
3. Parse and display the recommendations in a useful format
"""

import os
import time
import httpx
import json
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from prefect import flow, task
from prefect.logging import get_run_logger

load_dotenv()


# Schema for structured recommendations output
RECOMMENDATIONS_SCHEMA = {
    "recommendations": [
        {
            "priority": "high/medium/low",
            "category": "architecture/code-quality/performance/security/testing/documentation",
            "title": "Short title of the recommendation",
            "description": "Detailed description of what should be done",
            "rationale": "Why this recommendation is important",
            "implementation_steps": ["Step 1 description", "Step 2 description"],
            "estimated_effort": "small/medium/large",
            "dependencies": ["List of other recommendations this depends on"],
            "files_affected": ["List of files that would be modified"],
        }
    ],
    "overall_assessment": {
        "migration_progress": "percentage (0-100)",
        "major_blockers": ["List of critical issues blocking progress"],
        "next_milestone": "Description of the next major milestone",
        "estimated_completion": "Rough estimate of time to completion",
    },
    "action_items": [
        {
            "type": "immediate/short-term/long-term",
            "description": "Specific action to take",
            "owner": "who should do this (user/devin/both)",
            "priority": "critical/high/medium/low",
        }
    ],
}


@task
def create_session_with_recommendations(
    api_key: str, base_prompt: str, title: Optional[str] = None
) -> str:
    """
    Create a Devin session with structured output for recommendations.

    Args:
        api_key: Devin API key
        base_prompt: The original task prompt
        title: Optional session title

    Returns:
        session_id: The created session ID
    """
    logger = get_run_logger()

    # Enhance the prompt with structured output schema
    enhanced_prompt = f"""
{base_prompt}

Please provide structured recommendations in the following JSON format throughout the session.
Update this structured output whenever you identify new recommendations or complete analysis:

{json.dumps(RECOMMENDATIONS_SCHEMA, indent=2)}

Key instructions for structured output:
- Update recommendations as you discover issues or opportunities
- Categorize each recommendation appropriately
- Provide clear implementation steps
- Estimate effort realistically
- Update overall_assessment with current migration status
- Add action_items for both immediate and future work
"""

    url = "https://api.devin.ai/v1/sessions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    data = {
        "prompt": enhanced_prompt,
        "title": title or "Migration Analysis with Recommendations",
        "idempotent": False,
    }

    with httpx.Client() as client:
        response = client.post(url, headers=headers, json=data)
        response.raise_for_status()

    result = response.json()
    session_id = result["session_id"]

    logger.info(f"✅ Session created with recommendations schema: {session_id}")
    logger.info(f"   View at: {result['url']}")

    return session_id


@task
def get_structured_recommendations(
    api_key: str, session_id: str
) -> Optional[Dict[str, Any]]:
    """
    Retrieve structured recommendations from a session.

    Args:
        api_key: Devin API key
        session_id: The session ID to get recommendations from

    Returns:
        Structured recommendations data or None if not available
    """
    logger = get_run_logger()

    # Get session details including structured output
    url = f"https://api.devin.ai/v1/sessions/{session_id}"
    headers = {"Authorization": f"Bearer {api_key}"}

    with httpx.Client() as client:
        response = client.get(url, headers=headers)
        response.raise_for_status()

    session_data = response.json()

    # Extract structured output
    structured_output = session_data.get("structured_output")

    if structured_output:
        logger.info("📊 Structured recommendations retrieved successfully")
        return structured_output
    else:
        logger.warning("⚠️ No structured output available yet")
        return None


@task
def poll_for_recommendations(
    api_key: str, session_id: str, max_attempts: int = 30, poll_interval: int = 20
) -> Optional[Dict[str, Any]]:
    """
    Poll session for structured recommendations until available.

    Args:
        api_key: Devin API key
        session_id: The session ID to poll
        max_attempts: Maximum number of polling attempts
        poll_interval: Seconds between polls

    Returns:
        Structured recommendations when available
    """
    logger = get_run_logger()
    logger.info(f"📡 Polling for recommendations (max {max_attempts} attempts)...")

    for attempt in range(max_attempts):
        recommendations = get_structured_recommendations(api_key, session_id)

        if recommendations:
            logger.info(f"✅ Recommendations available after {attempt + 1} attempts")
            return recommendations

        if attempt < max_attempts - 1:
            logger.debug(
                f"   Attempt {attempt + 1}/{max_attempts} - waiting {poll_interval}s..."
            )
            time.sleep(poll_interval)

    logger.warning(f"⚠️ No recommendations after {max_attempts} attempts")
    return None


@task
def parse_and_display_recommendations(
    recommendations: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Parse and display structured recommendations in a user-friendly format.

    Args:
        recommendations: The structured recommendations data

    Returns:
        Parsed recommendations with analysis
    """
    logger = get_run_logger()

    # Parse recommendations list
    rec_list = recommendations.get("recommendations", [])
    logger.info(f"\n📋 RECOMMENDATIONS ({len(rec_list)} total)")
    logger.info("=" * 50)

    # Group by priority
    high_priority = [r for r in rec_list if r.get("priority") == "high"]
    medium_priority = [r for r in rec_list if r.get("priority") == "medium"]
    low_priority = [r for r in rec_list if r.get("priority") == "low"]

    # Display high priority recommendations
    if high_priority:
        logger.info("\n🔴 HIGH PRIORITY:")
        for rec in high_priority:
            logger.info(f"  • {rec.get('title', 'Untitled')}")
            logger.info(f"    Category: {rec.get('category', 'general')}")
            logger.info(f"    {rec.get('description', '')}")
            if rec.get("implementation_steps"):
                logger.info("    Steps:")
                for step in rec["implementation_steps"]:
                    logger.info(f"      - {step}")

    # Display medium priority recommendations
    if medium_priority:
        logger.info("\n🟡 MEDIUM PRIORITY:")
        for rec in medium_priority:
            logger.info(f"  • {rec.get('title', 'Untitled')}")
            logger.info(f"    {rec.get('description', '')}")

    # Display low priority recommendations
    if low_priority:
        logger.info("\n🟢 LOW PRIORITY:")
        for rec in low_priority:
            logger.info(f"  • {rec.get('title', 'Untitled')}")

    # Display overall assessment
    assessment = recommendations.get("overall_assessment", {})
    if assessment:
        logger.info("\n📊 OVERALL ASSESSMENT")
        logger.info("=" * 50)
        logger.info(
            f"Migration Progress: {assessment.get('migration_progress', 'Unknown')}%"
        )
        logger.info(
            f"Next Milestone: {assessment.get('next_milestone', 'Not specified')}"
        )

        blockers = assessment.get("major_blockers", [])
        if blockers:
            logger.info("Major Blockers:")
            for blocker in blockers:
                logger.info(f"  ⚠️ {blocker}")

    # Display action items
    action_items = recommendations.get("action_items", [])
    if action_items:
        logger.info("\n🎯 ACTION ITEMS")
        logger.info("=" * 50)

        immediate = [a for a in action_items if a.get("type") == "immediate"]
        if immediate:
            logger.info("Immediate Actions:")
            for action in immediate:
                logger.info(f"  → {action.get('description', '')}")
                logger.info(f"    Owner: {action.get('owner', 'unassigned')}")

    # Return parsed structure
    return {
        "total_recommendations": len(rec_list),
        "by_priority": {
            "high": len(high_priority),
            "medium": len(medium_priority),
            "low": len(low_priority),
        },
        "categories": list(set(r.get("category", "general") for r in rec_list)),
        "has_blockers": len(assessment.get("major_blockers", [])) > 0,
        "progress": assessment.get("migration_progress", 0),
        "immediate_actions": len(immediate) if action_items else 0,
    }


@flow(log_prints=True)
def test_recommendations_workflow(
    session_id: Optional[str] = None, create_new: bool = False
):
    """
    Test workflow for getting recommendations from Devin sessions.

    Args:
        session_id: Existing session ID to check (optional)
        create_new: Whether to create a new session
    """
    logger = get_run_logger()
    api_key = os.environ.get("DEVIN_API_KEY")

    if not api_key:
        raise ValueError("DEVIN_API_KEY not found in environment")

    # Option 1: Check existing session for recommendations
    if session_id and not create_new:
        logger.info(f"🔍 Checking existing session: {session_id}")

        # Try to get recommendations immediately
        recommendations = get_structured_recommendations(api_key, session_id)

        if not recommendations:
            # Poll for recommendations
            recommendations = poll_for_recommendations(
                api_key, session_id, max_attempts=15, poll_interval=20
            )

        if recommendations:
            analysis = parse_and_display_recommendations(recommendations)
            logger.info("\n✅ Recommendations retrieved successfully!")
            logger.info(f"Summary: {analysis}")
            return recommendations
        else:
            logger.warning("❌ No recommendations available from this session")
            return None

    # Option 2: Create new session with recommendations schema
    elif create_new:
        logger.info("🚀 Creating new session with recommendations schema...")

        test_prompt = """
        !ask Carefully analyze the status of migration by comparing the source 
        taylor-curran/og-cics-cobol-app repo to the target repo taylor-curran/target-springboot-cics
        
        Provide detailed recommendations for:
        1. Most advantageous next steps to make solid progress
        2. Architecture improvements needed
        3. Code quality issues to address
        4. Testing strategy recommendations
        5. Documentation needs
        
        Focus on actionable, prioritized recommendations with clear implementation steps.
        """

        new_session_id = create_session_with_recommendations(
            api_key, test_prompt, "Migration Analysis with Structured Recommendations"
        )

        logger.info(f"📝 New session created: {new_session_id}")
        logger.info("⏳ Waiting for Devin to generate recommendations...")

        # Poll for recommendations
        recommendations = poll_for_recommendations(
            api_key,
            new_session_id,
            max_attempts=90,  # ~30 minutes
            poll_interval=20,
        )

        if recommendations:
            analysis = parse_and_display_recommendations(recommendations)
            logger.info("\n✅ Recommendations generated successfully!")
            logger.info(f"Summary: {analysis}")
            return recommendations
        else:
            logger.warning("⏰ Session is taking longer than expected")
            logger.info(
                f"Check status at: https://app.devin.ai/sessions/{new_session_id}"
            )
            return None

    else:
        logger.info("ℹ️ Please provide either a session_id or set create_new=True")
        return None


def test_get_session_data(api_key: str, session_id: str):
    """
    Test function to explore what data is available from a session.
    """
    print("\n🔍 Testing Session Data Retrieval")
    print("=" * 60)

    # Test 1: Get basic session details
    url = f"https://api.devin.ai/v1/sessions/{session_id}"
    headers = {"Authorization": f"Bearer {api_key}"}

    print(f"📡 Fetching session details for: {session_id}")

    with httpx.Client() as client:
        response = client.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("✅ Session details retrieved")

            # Check what fields are available
            print("\n📋 Available fields:")
            for key in data.keys():
                print(f"  • {key}")

            # Check for structured output
            if "structured_output" in data:
                print("\n✨ Structured output found!")
                print(json.dumps(data["structured_output"], indent=2))
            else:
                print("\n⚠️ No structured_output field found")

            # Check status
            if "status_enum" in data:
                print(f"\n📊 Session status: {data['status_enum']}")

            return data
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return None


def test_get_enterprise_analysis(api_key: str, session_id: str):
    """
    Test getting session analysis from enterprise endpoint.
    """
    print("\n🔍 Testing Enterprise Analysis Endpoint")
    print("=" * 60)

    url = f"https://api.devin.ai/beta/v2/enterprise/sessions/{session_id}"
    headers = {"Authorization": f"Bearer {api_key}"}

    print(f"📡 Fetching enterprise analysis for: {session_id}")

    with httpx.Client() as client:
        response = client.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("✅ Enterprise data retrieved")

            # Check what fields are available
            print("\n📋 Available fields:")
            for key in data.keys():
                print(f"  • {key}")

            # Check for session_analysis
            if "session_analysis" in data:
                print("\n📊 Session analysis found!")
                analysis = data["session_analysis"]

                # Show what's in the analysis
                if analysis:
                    print("Analysis contains:")
                    for key in analysis.keys():
                        print(f"  • {key}")
                        if key == "action_items" and analysis[key]:
                            print(f"    ({len(analysis[key])} items)")
                        elif key == "issues" and analysis[key]:
                            print(f"    ({len(analysis[key])} issues)")
                        elif key == "timeline" and analysis[key]:
                            print(f"    ({len(analysis[key])} events)")

            return data
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return None


if __name__ == "__main__":
    # Load API key
    api_key = os.environ.get("DEVIN_API_KEY")
    if not api_key:
        print("❌ DEVIN_API_KEY not found in environment")
        exit(1)

    # The specific session mentioned by the user
    session_id = "devin-32b7f51018564cde93ea0937b4eeca7a"

    print("\n" + "=" * 60)
    print(f"TESTING SESSION: {session_id}")
    print("=" * 60)

    # Test 1: Get basic session data and check for structured output
    session_data = test_get_session_data(api_key, session_id)

    # Test 2: Get enterprise analysis (action items, issues, timeline)
    enterprise_data = test_get_enterprise_analysis(api_key, session_id)

    # Test 3: Try the workflow to see if we can extract recommendations
    print("\n" + "=" * 60)
    print("TESTING RECOMMENDATIONS WORKFLOW")
    print("=" * 60)

    result = test_recommendations_workflow(session_id=session_id, create_new=False)

    # Analysis of what we found
    print("\n" + "=" * 60)
    print("ANALYSIS SUMMARY")
    print("=" * 60)

    if session_data and "structured_output" in session_data:
        print("✅ Session has structured output available")
    else:
        print("⚠️ No structured output in this session")
        print("   → This session may not have been created with a structured schema")

    if enterprise_data and enterprise_data.get("session_analysis"):
        analysis = enterprise_data["session_analysis"]
        if analysis.get("action_items"):
            print(f"✅ Found {len(analysis['action_items'])} action items")
            print("\n📝 Sample Action Items:")
            for i, item in enumerate(analysis["action_items"][:3], 1):
                print(
                    f"  {i}. {item.get('type', 'unknown')}: {item.get('action_item', '')[:100]}..."
                )

        if analysis.get("suggested_prompt"):
            print("\n✅ Found suggested prompt improvements")

        print("\n💡 RECOMMENDATION: Since this session doesn't have structured output,")
        print("   we can extract recommendations from:")
        print("   1. Action items - specific things to do")
        print("   2. Issues - problems to address")
        print("   3. Suggested prompt - improved approach")
        print("   4. Timeline events - understand what was attempted")
