#!/usr/bin/env python3
"""Quick test to show what's included in our artifact family."""

from prefect.artifacts import Artifact


def show_artifact_contents():
    """Display the complete artifact family contents."""
    session_id = "a2dfa695"

    print("=" * 60)
    print("📦 ARTIFACT FAMILY CONTENTS")
    print("=" * 60)

    # 1. Analysis artifact (includes timeline + action items)
    analysis_artifact = Artifact.get(f"analysis-{session_id}")
    if analysis_artifact:
        print("\n1️⃣ ANALYSIS ARTIFACT (includes Timeline + Action Items)")
        print("-" * 40)
        print(analysis_artifact.data[:800])  # Show first 800 chars
        print("... [truncated]")

    # 2. Suggestion artifact
    suggestion_artifact = Artifact.get(f"suggestion-{session_id}")
    if suggestion_artifact:
        print("\n\n2️⃣ SUGGESTION ARTIFACT (Prompt Improvements)")
        print("-" * 40)
        print(suggestion_artifact.data[:600])  # Show first 600 chars
        print("... [truncated]")

    print("\n\n" + "=" * 60)
    print("✅ ARTIFACT FAMILY INCLUDES:")
    print("=" * 60)
    print("""
    📊 Analysis Artifact:
       - 🐛 Issues detected (with impact levels)
       - 📅 Timeline events (with smart emojis)
       - 🎬 Action items (NEW! with type-specific emojis):
           🖥️ Machine Setup
           🧠 Knowledge items
           📁 External files/docs
           🔄 Process improvements
    
    💡 Suggestion Artifact:
       - 📝 Original prompt
       - ✨ Improved prompt
       - 🎯 Feedback items explaining changes
    
    🔗 Both can be fetched programmatically for reuse!
    """)


if __name__ == "__main__":
    show_artifact_contents()
