#!/usr/bin/env python3
"""Quick view of the improved artifact format."""

from prefect.artifacts import Artifact

# Get the latest analysis artifact
artifact = Artifact.get("analysis-a2dfa695")
if artifact:
    print(artifact.data)
else:
    print("No artifact found")
