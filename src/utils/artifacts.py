"""
Artifact utilities for the migration orchestration project.
Provides helper functions for creating various types of Prefect artifacts.
"""

from prefect.artifacts import create_link_artifact, create_markdown_artifact
from typing import Optional


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


def create_analysis_artifact(session_id: str, analysis: dict) -> str:
    """
    Create a markdown artifact with session analysis details.

    Args:
        session_id: The Devin session ID
        analysis: The analysis data from Devin

    Returns:
        The artifact ID
    """
    # Build markdown content from analysis
    markdown_content = f"# Session Analysis: {session_id[:8]}...\n\n"

    if "issues" in analysis and analysis["issues"]:
        markdown_content += "## Issues Found\n\n"
        for i, issue in enumerate(analysis["issues"], 1):
            markdown_content += f"{i}. {issue}\n"
        markdown_content += "\n"

    if "action_items" in analysis and analysis["action_items"]:
        markdown_content += "## Action Items\n\n"
        for i, item in enumerate(analysis["action_items"], 1):
            markdown_content += f"- {item}\n"
        markdown_content += "\n"

    if "timeline" in analysis and analysis["timeline"]:
        markdown_content += (
            f"## Timeline\n\n{len(analysis['timeline'])} events recorded\n\n"
        )

    if "suggested_prompt" in analysis and analysis["suggested_prompt"]:
        markdown_content += "## Suggested Next Prompt\n\n"
        markdown_content += f"```\n{analysis['suggested_prompt']}\n```\n"

    artifact_id = create_markdown_artifact(
        key=f"devin-analysis-{session_id}",
        markdown=markdown_content,
        description=f"Analysis results for Devin session {session_id}",
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
    status = "✅ Completed Successfully" if analysis else "⚠️ Completed (No Analysis)"
    markdown_content += f"## Status\n\n{status}\n"

    artifact_id = create_markdown_artifact(
        key=f"orchestration-summary-{session_id}",
        markdown=markdown_content,
        description=f"Complete orchestration summary for session {session_id}",
    )

    return artifact_id
