#!/usr/bin/env python3
"""
Test extracting recommendations from existing session analysis data.

This approach works with sessions that don't have structured output,
by extracting recommendations from:
- Action items
- Issues detected
- Suggested prompts
- Timeline events
"""

import os
import httpx
import json
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()


def extract_recommendations_from_analysis(
    analysis: Dict[str, Any],
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Extract actionable recommendations from session analysis.

    Converts action items, issues, and other analysis data into
    structured recommendations.
    """
    recommendations = {
        "immediate_actions": [],
        "migration_fixes": [],
        "improvements": [],
        "next_session_approach": [],
    }

    # Extract from action items
    action_items = analysis.get("action_items", [])
    for item in action_items:
        if isinstance(item, dict):
            action_type = item.get("type", "general")
            action_text = item.get("action_item", "")
            issue_ref = item.get("issue_id", "")

            # Categorize by type
            rec = {
                "type": action_type,
                "action": action_text,
                "related_issue": issue_ref,
            }

            if action_type in ["machine_setup", "external"]:
                rec["category"] = "immediate"
                recommendations["immediate_actions"].append(rec)
            elif action_type == "knowledge":
                rec["category"] = "improvement"
                recommendations["improvements"].append(rec)
            else:
                rec["category"] = "migration"
                recommendations["migration_fixes"].append(rec)

    # Extract from issues
    issues = analysis.get("issues", [])
    for idx, issue in enumerate(issues, 1):
        if isinstance(issue, dict):
            impact = issue.get("impact", "unknown")
            label = issue.get("label", "Issue")
            description = issue.get("issue", "")

            # Create fix recommendation for each issue
            fix = {
                "issue_id": idx,
                "issue_label": label,
                "issue_impact": impact,
                "issue_description": description,
                "recommended_fix": f"Address {label}: {description}",
            }

            # High impact issues need immediate attention
            if impact == "high":
                fix["priority"] = "critical"
                recommendations["immediate_actions"].append(
                    {
                        "type": "critical_fix",
                        "action": f"Fix high-impact issue: {label}",
                        "details": description,
                    }
                )
            else:
                fix["priority"] = impact
                recommendations["migration_fixes"].append(fix)

    # Extract from suggested prompt
    suggested = analysis.get("suggested_prompt")
    if suggested and isinstance(suggested, dict):
        improved_prompt = suggested.get("suggested_prompt", "")
        feedback = suggested.get("feedback_items", [])

        if improved_prompt:
            recommendations["next_session_approach"].append(
                {
                    "type": "prompt_improvement",
                    "improved_prompt": improved_prompt,
                    "feedback_reasons": feedback,
                }
            )

    # Analyze timeline for patterns
    timeline = analysis.get("timeline", [])
    failed_attempts = []
    successful_patterns = []

    for event in timeline:
        if isinstance(event, dict):
            title = event.get("title", "").lower()
            desc = event.get("description", "")

            # Look for failures or issues
            if any(word in title for word in ["error", "fail", "issue"]):
                if not any(word in title for word in ["fixed", "resolved"]):
                    failed_attempts.append(
                        {"event": event.get("title", ""), "description": desc}
                    )
            # Look for successes
            elif any(word in title for word in ["success", "complete", "fixed"]):
                successful_patterns.append(
                    {"event": event.get("title", ""), "description": desc}
                )

    # Add pattern-based recommendations
    if failed_attempts:
        recommendations["improvements"].append(
            {
                "type": "avoid_patterns",
                "description": "Patterns to avoid based on failed attempts",
                "patterns": failed_attempts,
            }
        )

    if successful_patterns:
        recommendations["improvements"].append(
            {
                "type": "success_patterns",
                "description": "Successful patterns to replicate",
                "patterns": successful_patterns,
            }
        )

    return recommendations


def display_recommendations(recommendations: Dict[str, List[Dict[str, Any]]]):
    """
    Display extracted recommendations in a user-friendly format.
    """
    print("\n" + "=" * 60)
    print("📋 EXTRACTED RECOMMENDATIONS")
    print("=" * 60)

    # Immediate actions
    immediate = recommendations.get("immediate_actions", [])
    if immediate:
        print("\n🚨 IMMEDIATE ACTIONS REQUIRED:")
        for idx, action in enumerate(immediate, 1):
            print(f"\n{idx}. {action.get('action', 'No description')}")
            if action.get("details"):
                print(f"   Details: {action['details']}")
            if action.get("type"):
                print(f"   Type: {action['type']}")

    # Migration fixes
    fixes = recommendations.get("migration_fixes", [])
    if fixes:
        print("\n🔧 MIGRATION FIXES NEEDED:")
        for fix in fixes:
            if fix.get("issue_label"):
                print(
                    f"\n• {fix['issue_label']} ({fix.get('issue_impact', 'unknown')} priority)"
                )
                print(f"  Issue: {fix.get('issue_description', '')}")
            elif fix.get("action"):
                print(f"\n• {fix['action']}")
                print(f"  Type: {fix.get('type', 'general')}")

    # Improvements
    improvements = recommendations.get("improvements", [])
    if improvements:
        print("\n💡 SUGGESTED IMPROVEMENTS:")
        for imp in improvements:
            print(f"\n• {imp.get('description', imp.get('action', 'Improvement'))}")
            if imp.get("type"):
                print(f"  Type: {imp['type']}")
            if imp.get("patterns"):
                for pattern in imp["patterns"][:3]:  # Show first 3
                    print(f"  - {pattern.get('event', pattern)}")

    # Next session approach
    next_approach = recommendations.get("next_session_approach", [])
    if next_approach:
        print("\n🎯 RECOMMENDED APPROACH FOR NEXT SESSION:")
        for approach in next_approach:
            if approach.get("improved_prompt"):
                print("\nUse this improved prompt:")
                print("-" * 40)
                # Show first 500 chars of improved prompt
                prompt = approach["improved_prompt"]
                if len(prompt) > 500:
                    print(prompt[:500] + "...")
                else:
                    print(prompt)
                print("-" * 40)

                if approach.get("feedback_reasons"):
                    print("\nWhy this approach is better:")
                    for feedback in approach["feedback_reasons"]:
                        if isinstance(feedback, dict):
                            print(f"  • {feedback.get('summary', feedback)}")


def main():
    """
    Main test function.
    """
    api_key = os.environ.get("DEVIN_API_KEY")
    if not api_key:
        print("❌ DEVIN_API_KEY not found")
        return

    # Test with the specific session
    session_id = "devin-32b7f51018564cde93ea0937b4eeca7a"

    print(f"\n🔍 Extracting recommendations from session: {session_id}")
    print("=" * 60)

    # Get enterprise analysis
    url = f"https://api.devin.ai/beta/v2/enterprise/sessions/{session_id}"
    headers = {"Authorization": f"Bearer {api_key}"}

    with httpx.Client() as client:
        response = client.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            analysis = data.get("session_analysis")

            if analysis:
                print("✅ Session analysis retrieved")

                # Quick stats
                print(f"\n📊 Analysis contains:")
                print(f"  • {len(analysis.get('action_items', []))} action items")
                print(f"  • {len(analysis.get('issues', []))} issues")
                print(f"  • {len(analysis.get('timeline', []))} timeline events")
                print(
                    f"  • Suggested prompt: {'Yes' if analysis.get('suggested_prompt') else 'No'}"
                )

                # Extract recommendations
                recommendations = extract_recommendations_from_analysis(analysis)

                # Display recommendations
                display_recommendations(recommendations)

                # Count total recommendations
                total = sum(len(v) for v in recommendations.values())
                print(f"\n📊 Total recommendations extracted: {total}")

                # Save to JSON for further processing
                output_file = f"recommendations_{session_id}.json"
                with open(output_file, "w") as f:
                    json.dump(
                        {
                            "session_id": session_id,
                            "recommendations": recommendations,
                            "original_analysis": analysis,
                        },
                        f,
                        indent=2,
                    )
                print(f"\n💾 Full data saved to: {output_file}")

            else:
                print("⚠️ No analysis available for this session")
        else:
            print(f"❌ Failed to get session: {response.status_code}")
            print(response.text)


if __name__ == "__main__":
    main()
