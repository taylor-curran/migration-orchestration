#!/usr/bin/env python3
"""View all three artifact types."""

from prefect.artifacts import Artifact

session_id = "a2dfa695"

print("=" * 60)
print("📦 ARTIFACT FAMILY - CLEAN SEPARATION OF CONCERNS")
print("=" * 60)

# 1. Analysis artifact - Just timeline and issues
analysis = Artifact.get(f"analysis-{session_id}")
if analysis:
    print("\n1️⃣ ANALYSIS ARTIFACT (Timeline + Issues)")
    print("-" * 40)
    print(analysis.data[:800])
    print("...")

# 2. Improvements artifact - Prompt suggestions AND action items
improvements = Artifact.get(f"improvements-{session_id}")
if improvements:
    print("\n\n2️⃣ SESSION IMPROVEMENTS ARTIFACT")
    print("-" * 40)
    print(improvements.data[:900])
    print("...")

# 3. Knowledge artifact
knowledge = Artifact.get(f"knowledge-{session_id}")
if knowledge:
    print("\n\n3️⃣ KNOWLEDGE ARTIFACT (Future)")
    print("-" * 40)
    print(knowledge.data[:400])
    print("...")

print("\n" + "=" * 60)
print("✅ Clean separation:")
print("  • Analysis: What happened (issues & timeline)")
print("  • Improvements: How to do better (prompts & actions)")
print("  • Knowledge: What was learned (future API support)")
print("=" * 60)
