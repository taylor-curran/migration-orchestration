"""
Artifact utilities for the migration orchestration project.
Provides helper functions for creating various types of Prefect artifacts.
"""

from prefect.artifacts import create_link_artifact, create_markdown_artifact
from typing import Optional, Dict, Any


def create_session_link_artifact(
    session_id: str, session_url: str, title: Optional[str] = None
) -> str:
    """
    Create a link artifact for a Devin session.

    Args:
        session_id: The Devin session ID
        session_url: The URL to the Devin session
        title: Optional title for the session

    Returns:
        The artifact ID
    """
    description = (
        f"## Devin Session: {title or 'Untitled'}\n\nSession ID: `{session_id}`"
    )

    artifact_id = create_link_artifact(
        key=f"session-url-{session_id}",
        link=session_url,
        link_text=session_url,
        description=description,
    )

    return artifact_id


def create_timeline_artifact(
    session_id: str, session_url: str, analysis: Dict[str, Any]
) -> str:
    """
    Create main analysis artifact with issues and timeline.

    Args:
        session_id: The Devin session ID
        session_url: The URL to the Devin session
        analysis: The analysis data from Devin

    Returns:
        The artifact ID
    """
    issues_count = len(analysis.get("issues", []))
    timeline = analysis.get("timeline", [])

    md = f"""# 📊 Analysis

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

    # List ALL events chronologically with smart emojis
    for event in timeline:
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
            elif any(word in title.lower() for word in ["unnecessary"]):
                emoji = "🐌"
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
                word in title.lower() for word in ["pass", "implement", "improve", "increase"]
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
        key=f"analysis-{session_id}",
        markdown=md,
        description=f"Session analysis for {session_id}",
    )

    return artifact_id


def create_improvements_artifact(session_id: str, analysis: Dict[str, Any]) -> str:
    """
    Create artifact for session improvements including prompt suggestions and action items.

    Args:
        session_id: The Devin session ID
        analysis: The analysis data from Devin

    Returns:
        The artifact ID
    """
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
        key=f"improvements-{session_id}",
        markdown=md,
        description=f"Session improvements for {session_id}",
    )

    return artifact_id


def create_orchestration_summary_artifact(
    session_id: str,
    session_url: str,
    analysis: dict,
    execution_time: float,
    title: Optional[str] = None,
) -> str:
    """
    Create a comprehensive summary artifact for the entire orchestration.

    Args:
        session_id: The Devin session ID
        session_url: The URL to the Devin session
        analysis: The analysis data from Devin
        execution_time: Total execution time in seconds
        title: Optional title for the session

    Returns:
        The artifact ID
    """
    markdown_content = f"# Orchestration Summary\n\n"
    markdown_content += f"**Session**: {title or 'Untitled'}\n"
    markdown_content += f"**Session ID**: `{session_id}`\n"
    markdown_content += f"**Execution Time**: {execution_time:.1f} seconds\n"
    markdown_content += f"**Session URL**: [View Session]({session_url})\n\n"

    # Quick stats
    issues_count = len(analysis.get("issues", []))
    action_items_count = len(analysis.get("action_items", []))
    timeline_count = len(analysis.get("timeline", []))

    markdown_content += "## Quick Stats\n\n"
    markdown_content += f"- **Issues Found**: {issues_count}\n"
    markdown_content += f"- **Action Items**: {action_items_count}\n"
    markdown_content += f"- **Timeline Events**: {timeline_count}\n"
    markdown_content += f"- **Has Suggested Prompt**: {'Yes' if analysis.get('suggested_prompt') else 'No'}\n\n"

    # Status
    status = "✅ Completed With Analysis" if analysis else "⚠️ Completed (No Analysis)"
    markdown_content += f"## Status\n\n{status}\n"

    artifact_id = create_markdown_artifact(
        key=f"orchestration-summary-{session_id}",
        markdown=markdown_content,
        description=f"Complete orchestration summary for session {session_id}",
    )

    return artifact_id
