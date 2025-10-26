#!/usr/bin/env python3
"""
Test flow for fetching and displaying Devin session analysis.
This test retrieves analysis from specific sessions and creates rich artifacts.
"""

import os
import json
import httpx
from prefect import flow, task
from prefect.logging import get_run_logger
from prefect.artifacts import create_markdown_artifact, create_link_artifact
from dotenv import load_dotenv
from typing import Dict, Any, Optional
import time

load_dotenv()


def fetch_session_analysis(api_key: str, session_id: str) -> Optional[Dict[str, Any]]:
    """Fetch session analysis from the Devin API."""
    url = f"https://api.devin.ai/beta/v2/enterprise/sessions/{session_id}"
    headers = {"Authorization": f"Bearer {api_key}"}

    with httpx.Client() as client:
        response = client.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get("session_analysis")


def create_timeline_artifact(
    session_id: str, session_url: str, analysis: Dict[str, Any]
) -> str:
    """Create main analysis artifact with timeline."""

    issues_count = len(analysis.get("issues", []))
    timeline = analysis.get("timeline", [])

    md = f"""
# 📊 Analysis

## 🐛 ISSUES DETECTED

"""

    if issues_count > 0:
        for issue in analysis["issues"]:
            if isinstance(issue, dict):
                impact = issue.get("impact", "unknown")
                label = issue.get("label", "Issue")
                description = issue.get("issue", "No description")

                # Format like Devin UI: "Communication issue (medium)"
                if impact == "high":
                    severity_text = "(high)"
                    severity_emoji = "🚨"
                elif impact == "medium":
                    severity_text = "(medium)"
                    severity_emoji = "⚠️"
                elif impact == "low":
                    severity_text = "(low)"
                    severity_emoji = "🟡"
                else:
                    severity_text = "(unknown)"
                    severity_emoji = "⚪"

                md += f"### {severity_emoji} {label} {severity_text}\n\n"
                md += f"{description}\n\n"
    else:
        md += "✅ **No issues detected**\n\n"

    md += "## 📅 TIMELINE\n\n"

    # List ALL events chronologically with emojis
    for i, event in enumerate(timeline, 1):
        if isinstance(event, dict):
            title = event.get("title", "")
            desc = event.get("description", "")

            # Pick emoji based on keywords - default to green dot like Devin UI
            emoji = "🟢"  # Default for non-issue items

            # Check for specific keywords - most specific first
            if any(
                word in title.lower() for word in ["error", "fail", "issue"]
            ) and not any(word in title.lower() for word in ["fixed", "resolved"]):
                emoji = "❌"  # Only use error emoji if NOT fixed/resolved
            elif any(word in title.lower() for word in ["asks", "user"]):
                emoji = "👤"
            elif any(word in title.lower() for word in ["select", "choose", "plan"]):
                emoji = "🎯"
            elif any(
                word in title.lower()
                for word in ["analyze", "analysis", "research", "deep"]
            ):
                emoji = "📚"
            elif any(word in title.lower() for word in ["knowledge"]):
                emoji = "✨"
            elif any(word in title.lower() for word in ["document", "guide"]):
                emoji = "📝"
            elif any(word in title.lower() for word in ["setup", "config"]):
                emoji = "⚙️"
            elif "install" in title.lower():
                emoji = "⬇️"
            elif any(word in title.lower() for word in ["pr ", "pull request", "push"]):
                emoji = "📗"
            elif any(word in title.lower() for word in ["test"]) and any(
                word in title.lower() for word in ["pass"]
            ):
                emoji = "📋"  # Tests passing
            elif any(
                word in title.lower()
                for word in ["success", "complete", "finish", "resolved", "fixed"]
            ):
                emoji = "✅"  # Generic success - check last

            md += f"{emoji} **{title}**\n"
            if desc:
                md += f"   > {desc}\n\n"
            else:
                md += "\n"

    # Add session link at the bottom
    md += "\n---\n\n"
    md += f"🔗 [View Full Session]({session_url})\n"

    artifact_id = create_markdown_artifact(
        key=f"analysis-{session_id[:8]}",
        markdown=md,
        description=f"Session analysis for {session_id[:8]}",
    )
    return artifact_id


def create_improvements_artifact(session_id: str, analysis: Dict[str, Any]) -> str:
    """Create artifact for session improvements including prompt suggestions and action items."""

    md = "# 🚀 Session Improvements\n\n"

    # Add prompt improvements section
    suggestion = analysis.get("suggested_prompt")
    if suggestion:
        md += "## 💡 Prompt Optimization\n\n"

        if isinstance(suggestion, dict):
            original = suggestion.get("original_prompt", "")
            improved = suggestion.get("suggested_prompt", "")

            md += "### 📝 Original Prompt\n"
            md += f"```\n{original}\n```\n\n"

            md += "### ✨ Improved Prompt\n"
            md += f"```\n{improved}\n```\n\n"

            # Add feedback items if they exist
            feedback_items = suggestion.get("feedback_items", [])
            if feedback_items:
                md += "### 🎯 Why These Changes?\n\n"
                for item in feedback_items:
                    if isinstance(item, dict):
                        summary = item.get("summary", "")
                        details = item.get("details", "")
                        md += f"🔸 **{summary}**\n"
                        if details:
                            md += f"   _{details}_\n\n"
        else:
            # Simple string suggestion
            md += f"```\n{suggestion}\n```\n\n"

    # Add action items section
    action_items = analysis.get("action_items", [])
    if action_items:
        md += "\n## 🎬 Action Items\n\n"
        for item in action_items:
            if isinstance(item, dict):
                item_type = item.get("type", "general")
                action = item.get("action_item", "")
                issue_ref = item.get("issue_id", "")

                # Pick emoji based on action type
                type_emoji = "📌"
                if item_type == "machine_setup":
                    type_emoji = "🖥️"
                elif item_type == "knowledge":
                    type_emoji = "🧠"
                elif item_type == "external":
                    type_emoji = "📁"
                elif item_type == "process":
                    type_emoji = "🔄"

                md += f"{type_emoji} **{item_type.replace('_', ' ').title()}**"
                if issue_ref:
                    # Convert issue ID to ordinal text
                    issue_num = str(issue_ref)
                    if issue_num == "1":
                        issue_text = "first issue"
                    elif issue_num == "2":
                        issue_text = "second issue"
                    elif issue_num == "3":
                        issue_text = "third issue"
                    else:
                        issue_text = f"issue {issue_num}"
                    md += f" ({issue_text})"
                md += f"\n\n> {action}\n\n"

    # If neither suggestions nor action items exist, provide a default message
    if not suggestion and not action_items:
        md += "*No specific improvements identified for this session.*\n"

    artifact_id = create_markdown_artifact(
        key=f"improvements-{session_id[:8]}",
        markdown=md,
        description=f"Session improvements for {session_id[:8]}",
    )
    return artifact_id


@task(name="process-session")
def process_session(session_url: str) -> Dict[str, Any]:
    """Process a single session."""
    logger = get_run_logger()

    # Extract session ID from URL
    session_id = session_url.split("/")[-1]
    full_session_id = f"devin-{session_id}"
    short_id = session_id[:8]

    logger.info(f"Fetching {short_id}...")

    # Get API key and fetch
    api_key = os.environ.get("DEVIN_API_KEY")
    analysis = fetch_session_analysis(api_key, full_session_id)

    if analysis:
        logger.info(f"✅ Got analysis - {len(analysis.get('issues', []))} issues")

        # Create two artifacts
        timeline_id = create_timeline_artifact(session_id, session_url, analysis)
        improvements_id = create_improvements_artifact(session_id, analysis)

        return {
            "session_id": short_id,
            "has_analysis": True,
            "timeline_artifact": timeline_id,
            "improvements_artifact": improvements_id,
        }
    else:
        logger.warning(f"⚠️ No analysis for {short_id}")
        return {"session_id": short_id, "has_analysis": False}


@flow(name="test-artifact-flow", log_prints=True)
def test_artifact_flow():
    """Simple test flow."""
    logger = get_run_logger()

    # The two test sessions
    session_urls = [
        "https://app.devin.ai/sessions/a2dfa695140f4f4697c357f74839dd9a",
        "https://app.devin.ai/sessions/b4e5ec62741a40f2a48c6a71ce36d32a",
    ]

    logger.info("Starting test...")

    # Process each session
    for url in session_urls:
        result = process_session(url)
        logger.info(f"Result: {result}")

    logger.info("Test complete!")


if __name__ == "__main__":
    test_artifact_flow()
