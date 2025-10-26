#!/usr/bin/env python3
"""
Test file that properly handles the actual structured output format from Devin sessions.

The session has structured output with:
- next_steps: List of 5 prioritized steps with detailed definitions of done
- migration_analysis: Current status and comparison results
"""

import os
import httpx
import json
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from prefect import flow, task
from prefect.logging import get_run_logger

load_dotenv()


@task
def get_session_structured_output(
    api_key: str, session_id: str
) -> Optional[Dict[str, Any]]:
    """
    Get the structured output from a Devin session.
    """
    logger = get_run_logger()

    url = f"https://api.devin.ai/v1/sessions/{session_id}"
    headers = {"Authorization": f"Bearer {api_key}"}

    with httpx.Client() as client:
        response = client.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            structured = data.get("structured_output")
            if structured:
                logger.info("✅ Structured output retrieved")
                return structured
            else:
                logger.warning("⚠️ No structured output in session")
                return None
        else:
            logger.error(f"Failed to get session: {response.status_code}")
            return None


@task
def parse_next_steps(structured_output: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse the next_steps from structured output into actionable recommendations.
    """
    logger = get_run_logger()

    next_steps = structured_output.get("next_steps", [])
    recommendations = []

    logger.info(f"\n📋 NEXT STEPS TO COMPLETE ({len(next_steps)} total)")
    logger.info("=" * 60)

    for step in next_steps:
        step_num = step.get("step_number", 0)
        title = step.get("title", "Untitled")
        description = step.get("description", "")
        definition_of_done = step.get("definition_of_done", "")

        # Display step
        logger.info(f"\n📌 STEP {step_num}: {title}")
        logger.info(f"   {description}")
        logger.info(f"\n   ✅ Definition of Done:")
        logger.info(f"   {definition_of_done}")

        # Create recommendation
        recommendations.append(
            {
                "priority": step_num,  # Lower number = higher priority
                "title": title,
                "description": description,
                "definition_of_done": definition_of_done,
                "type": "migration_step",
            }
        )

    return recommendations


@task
def parse_migration_status(structured_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse the migration analysis from structured output.
    """
    logger = get_run_logger()

    analysis = structured_output.get("migration_analysis", {})

    if analysis:
        logger.info("\n📊 MIGRATION STATUS")
        logger.info("=" * 60)

        current_status = analysis.get("current_status", "Unknown")
        comparison = analysis.get("comparison_results", "")

        logger.info(f"\n🔍 Current Status:")
        logger.info(f"   {current_status}")

        logger.info(f"\n📈 Comparison Results:")
        logger.info(f"   {comparison}")

        # Extract percentage if present
        import re

        percentage_match = re.search(r"(\d+)%", current_status)
        percentage = int(percentage_match.group(1)) if percentage_match else 0

        # Extract counts
        migrated_match = re.search(r"(\d+) out of (\d+)", current_status)
        migrated = int(migrated_match.group(1)) if migrated_match else 0
        total = int(migrated_match.group(2)) if migrated_match else 0

        return {
            "percentage_complete": percentage,
            "programs_migrated": migrated,
            "total_programs": total,
            "current_status": current_status,
            "comparison": comparison,
        }

    return {}


@task
def combine_with_analysis_data(
    structured_output: Dict[str, Any], session_analysis: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Combine structured output with session analysis for comprehensive recommendations.
    """
    logger = get_run_logger()

    combined = {
        "next_steps": structured_output.get("next_steps", []),
        "migration_status": structured_output.get("migration_analysis", {}),
        "issues_to_address": [],
        "improvements": [],
        "environment_setup": [],
    }

    if session_analysis:
        # Add issues
        for issue in session_analysis.get("issues", []):
            combined["issues_to_address"].append(
                {
                    "impact": issue.get("impact"),
                    "label": issue.get("label"),
                    "description": issue.get("issue"),
                }
            )

        # Add action items
        for item in session_analysis.get("action_items", []):
            action_type = item.get("type", "")
            if action_type == "machine_setup":
                combined["environment_setup"].append(item.get("action_item"))
            else:
                combined["improvements"].append(item.get("action_item"))

        # Add improved prompt if available
        if session_analysis.get("suggested_prompt"):
            combined["improved_prompt"] = session_analysis["suggested_prompt"]

    return combined


@flow(log_prints=True)
def analyze_session_recommendations(session_id: str):
    """
    Main flow to analyze and extract all recommendations from a Devin session.
    """
    logger = get_run_logger()

    api_key = os.environ.get("DEVIN_API_KEY")
    if not api_key:
        raise ValueError("DEVIN_API_KEY not found")

    logger.info(f"🔍 Analyzing session: {session_id}")

    # Get structured output
    structured = get_session_structured_output(api_key, session_id)

    if structured:
        # Parse next steps
        recommendations = parse_next_steps(structured)

        # Parse migration status
        status = parse_migration_status(structured)

        # Get session analysis for additional context
        logger.info("\n📡 Fetching additional analysis data...")
        url = f"https://api.devin.ai/beta/v2/enterprise/sessions/{session_id}"
        headers = {"Authorization": f"Bearer {api_key}"}

        session_analysis = None
        with httpx.Client() as client:
            response = client.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                session_analysis = data.get("session_analysis")

        # Combine all data
        combined = combine_with_analysis_data(structured, session_analysis)

        # Final summary
        logger.info("\n" + "=" * 60)
        logger.info("📊 RECOMMENDATIONS SUMMARY")
        logger.info("=" * 60)

        logger.info(f"\n✅ Migration Progress: {status.get('percentage_complete', 0)}%")
        logger.info(
            f"   ({status.get('programs_migrated', 0)}/{status.get('total_programs', 0)} programs migrated)"
        )

        logger.info(f"\n📋 Next Steps: {len(recommendations)}")
        logger.info(f"🐛 Issues to Fix: {len(combined['issues_to_address'])}")
        logger.info(
            f"🔧 Environment Setup Needed: {len(combined['environment_setup'])}"
        )

        if combined.get("environment_setup"):
            logger.info("\n⚙️ ENVIRONMENT SETUP REQUIRED:")
            for setup in combined["environment_setup"]:
                logger.info(f"   • {setup}")

        # Save comprehensive results
        output = {
            "session_id": session_id,
            "migration_status": status,
            "recommendations": recommendations,
            "all_data": combined,
        }

        output_file = f"final_recommendations_{session_id}.json"
        with open(output_file, "w") as f:
            json.dump(output, f, indent=2)

        logger.info(f"\n💾 Complete recommendations saved to: {output_file}")

        return output
    else:
        logger.error("No structured output found")
        return None


if __name__ == "__main__":
    session_id = "devin-32b7f51018564cde93ea0937b4eeca7a"

    print("\n" + "=" * 60)
    print("FINAL RECOMMENDATIONS ANALYSIS")
    print("=" * 60)

    result = analyze_session_recommendations(session_id)

    if result:
        print("\n✅ Analysis complete! Check the output file for full details.")
