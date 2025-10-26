# Archived Test Files

This directory contains test scripts used during the development of the artifact system for Devin session analysis.

## Files:

- **test_flow.py** - Main test flow for fetching and creating artifacts from Devin sessions
- **test_fetch_artifacts.py** - Tests for fetching and reading artifacts from Prefect
- **test_artifact_contents.py** - Tests for viewing artifact family contents
- **test_view_artifacts.py** - Tests for viewing the two-artifact system
- **test_view_improved.py** - Quick view of improved artifact format
- **test_refactored.py** - Tests for the refactored production artifact functions

## Purpose:

These files were used to iteratively develop and test:
- Artifact formatting improvements
- Separation of analysis vs improvements artifacts
- Smart emoji system for timeline events
- Improved issue formatting matching Devin UI
- Action item formatting with ordinal references

The learnings from these tests have been incorporated into the production code in `src/utils/artifacts.py`.
