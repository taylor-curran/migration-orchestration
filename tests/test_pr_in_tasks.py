#!/usr/bin/env python3
"""
Test that run_sessions.py returns PR info in its output.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.tasks.run_sessions import run_session_and_wait_for_analysis

# Load environment variables
load_dotenv()


def test_pr_in_return():
    """Test that PR info is included in the return value."""
    
    # Check API key
    api_key = os.getenv("DEVIN_API_KEY")
    if not api_key:
        print("❌ DEVIN_API_KEY not found!")
        return
    
    # Simple prompt
    prompt = """
    Repository: taylor-curran/prefect-fork
    
    Make a tiny change to README.md - add a comment or update a timestamp.
    Create a pull request with the change.
    
    Definition of done:
    - Small change made
    - PR created
    """
    
    print("🚀 Testing PR info in return statement...")
    print("📋 This will create a test PR in taylor-curran/prefect-fork\n")
    
    try:
        # Run the session function
        result = run_session_and_wait_for_analysis(
            prompt=prompt,
            title="Test: PR in Return Value",
            api_key=api_key,
            poll_interval=10
        )
        
        # Check if PRs are in the result
        print("\n✅ Session completed!")
        print(f"🔗 Session: {result['session_url']}")
        
        # Verify PR info is present
        if "prs" in result:
            prs = result["prs"]
            print(f"\n✅ PR info successfully returned in result!")
            print(f"   Found {len(prs)} PR(s) in return value")
            
            if prs:
                for pr in prs:
                    print(f"\n   📍 PR URL: {pr.get('pr_url')}")
                    print(f"      State: {pr.get('state')}")
            else:
                print("   ⚠️ PR list is empty (no PRs created)")
        else:
            print("\n❌ 'prs' key not found in result!")
            print(f"   Keys in result: {list(result.keys())}")
        
        # Also check other expected keys
        expected_keys = ["session_id", "session_url", "analysis", "prs", "execution_time"]
        for key in expected_keys:
            if key in result:
                print(f"✅ '{key}' present")
            else:
                print(f"⚠️ '{key}' missing")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    test_pr_in_return()
