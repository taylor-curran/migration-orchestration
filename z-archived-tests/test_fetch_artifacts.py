#!/usr/bin/env python3
"""Simple test to fetch and print suggested prompts from Prefect artifacts."""

from prefect.artifacts import Artifact
from dotenv import load_dotenv

load_dotenv()


def extract_suggested_prompt(session_id: str) -> str:
    """Extract the improved prompt from a suggestion artifact."""
    artifact_key = f"suggestion-{session_id}"
    artifact = Artifact.get(artifact_key)

    if artifact and artifact.type == "markdown":
        content = artifact.data

        # Find the improved prompt section
        if "## ✨ Improved Prompt" in content:
            start = content.find("## ✨ Improved Prompt")
            start = content.find("```", start) + 3
            end = content.find("```", start)

            if start > 2 and end > start:
                return content[start:end].strip()

    return None


def print_suggested_prompts():
    """Print suggested prompts for all sessions."""
    session_ids = ["a2dfa695", "b4e5ec62"]

    print("=" * 60)
    print("💡 FETCHING SUGGESTED PROMPTS FROM ARTIFACTS")
    print("=" * 60)

    for session_id in session_ids:
        prompt = extract_suggested_prompt(session_id)

        if prompt:
            print(f"\n📝 Session {session_id}:")
            print("-" * 40)
            print(prompt)
            print("-" * 40)
        else:
            print(f"\n❌ No suggestion found for session {session_id}")

    print("\n✅ Ready to use these prompts in new sessions!")


if __name__ == "__main__":
    print_suggested_prompts()
