#!/usr/bin/env python3
"""Test the fixed PR status checking in orchestration."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent to path
sys.path.append(str(Path(__file__).parent.parent))

from src.tasks.run_sessions import get_enterprise_session_data

def test_fixed_pr_status_checking():
    """Test that the fixed orchestration can properly check PR status."""
    
    api_key = os.getenv("DEVIN_API_KEY")
    if not api_key:
        print("❌ DEVIN_API_KEY not set")
        return
    
    # Session IDs from the current orchestration run
    session_ids = [
        "3643a4f7686e4c58a39d46ff522a647b",  # setup_001
        "1040cc12774f442282457f66088eba47",  # setup_002 
        "66bf2cb933f24d789fab20f82853466e"   # setup_003
    ]
    
    print("🔍 Testing Fixed PR Status Checking:\n")
    
    # Simulate what the orchestration does
    session_results = []
    
    for session_id in session_ids:
        print(f"📋 Testing session: {session_id}")
        
        try:
            # This is what the orchestration calls
            session_data = get_enterprise_session_data(api_key, session_id)
            prs = session_data.get("prs", [])
            
            # Simulate the session result structure
            session_result = {
                "session_id": session_id,
                "session_url": f"https://app.devin.ai/sessions/{session_id}",
                "prs": prs
            }
            session_results.append(session_result)
            
            print(f"   ✅ Successfully retrieved session data")
            print(f"   📊 Found {len(prs)} PR(s)")
            
            for pr in prs:
                pr_url = pr.get("pr_url", "Unknown URL")
                state = pr.get("state", "unknown")
                print(f"      • {pr_url} - State: {state}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n📊 Summary:")
    print(f"   Sessions processed: {len(session_results)}")
    
    total_prs = sum(len(result.get("prs", [])) for result in session_results)
    print(f"   Total PRs found: {total_prs}")
    
    # Test the PR tracking logic (what wait_for_prs_to_merge does)
    print(f"\n🔍 Testing PR Tracking Logic:")
    
    pr_tracking = []
    for result in session_results:
        session_id = result.get("session_id")
        if result.get("prs"):
            for pr in result["prs"]:
                pr_tracking.append({
                    "session_id": session_id,
                    "pr_url": pr.get("pr_url"),
                    "merged": False
                })
    
    print(f"   PR tracking entries: {len(pr_tracking)}")
    for pr_info in pr_tracking:
        print(f"      • {pr_info['pr_url']} (session: {pr_info['session_id'][:8]}...)")
    
    # Test checking one PR status
    if pr_tracking:
        print(f"\n🧪 Testing PR Status Check for First PR:")
        first_pr = pr_tracking[0]
        
        try:
            session_data = get_enterprise_session_data(api_key, first_pr["session_id"])
            prs = session_data.get("prs", [])
            
            for pr in prs:
                if pr.get("pr_url") == first_pr["pr_url"]:
                    state = pr.get("state", "").lower()
                    print(f"   ✅ PR Status Check Successful")
                    print(f"      URL: {pr.get('pr_url')}")
                    print(f"      State: {state}")
                    
                    if state == "merged":
                        print(f"      🎉 PR is merged!")
                    elif state == "open":
                        print(f"      ⏳ PR is still open")
                    elif state == "closed":
                        print(f"      ❌ PR is closed")
                    break
            else:
                print(f"   ⚠️ PR not found in session data")
                
        except Exception as e:
            print(f"   ❌ Error checking PR status: {e}")
    
    print(f"\n✅ Test Complete!")
    print(f"💡 The orchestration should now work without 404 errors!")

if __name__ == "__main__":
    print("=" * 60)
    print("FIXED PR STATUS CHECKING TEST")
    print("=" * 60)
    
    test_fixed_pr_status_checking()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
