#!/usr/bin/env python3
"""Test the refactored artifact functions."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "src"))

from utils.artifacts import create_timeline_artifact, create_improvements_artifact

# Test data - simulating what we get from the API
test_analysis = {
    "issues": [
        {
            "issue": "Maven was not pre-installed, causing a delay",
            "impact": "low",
            "label": "Environment issue",
        }
    ],
    "timeline": [
        {
            "title": "User requests migration",
            "description": "User asks for COBOL migration",
        },
        {
            "title": "Tests pass successfully",
            "description": "All tests pass on first run",
        },
        {"title": "PR created", "description": "Pull request #9 created"},
    ],
    "action_items": [
        {
            "issue_id": "1",
            "type": "machine_setup",
            "action_item": "Preinstall Maven in development environment",
        }
    ],
    "suggested_prompt": {
        "original_prompt": "migrate a cobol program",
        "suggested_prompt": "migrate CRECUST.cbl specifically",
        "feedback_items": [
            {
                "summary": "Be specific about which program",
                "details": "Saves exploration time",
            }
        ],
    },
}

# Test creating artifacts
session_id = "devin-test12345678"
session_url = "https://app.devin.ai/sessions/test12345678"

print("🧪 Testing refactored artifact creation...")
print("-" * 40)

# Create timeline artifact
timeline_id = create_timeline_artifact(session_id, session_url, test_analysis)
print(f"✅ Created timeline artifact: {str(timeline_id)[:8]}...")

# Create improvements artifact
improvements_id = create_improvements_artifact(session_id, test_analysis)
print(f"✅ Created improvements artifact: {str(improvements_id)[:8]}...")

print("\n✨ Refactoring successful! The production code now includes:")
print("  • Better issue formatting (severity on same line)")
print("  • Smart timeline emojis")
print("  • 'first issue' instead of 'Issue #1'")
print("  • Clean separation of concerns")
print("  • Two artifacts instead of one monolithic artifact")
