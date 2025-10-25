"""
Pytest configuration and shared fixtures for all tests.
"""

import pytest
import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))
