#!/usr/bin/env python3
"""
Test script to verify PR creation and info retrieval from Devin sessions.
Uses the enterprise API to get PR information.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import json
import httpx

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.tasks.run_sessions import run_session_until_blocked, wait_for_status

# Load environment variables
load_dotenv()


def send_sleep_message(api_key: str, session_id: str):
    """Send sleep message to end session (without Prefect context)."""
    url = f"https://api.devin.ai/v1/sessions/{session_id}/message"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"message": "sleep"}
    
    with httpx.Client(timeout=httpx.Timeout(30.0)) as client:
        response = client.post(url, headers=headers, json=data)
        response.raise_for_status()
    
    print("💤 Sleep message sent")


def get_full_enterprise_session(api_key: str, session_id: str):
    """Get full enterprise session data including PRs."""
    url = f"https://api.devin.ai/beta/v2/enterprise/sessions/{session_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    with httpx.Client(timeout=httpx.Timeout(30.0)) as client:
        response = client.get(url, headers=headers)
        response.raise_for_status()
    
    return response.json()


def test_pr_creation():
    """
    Test creating a PR and getting the PR URL from enterprise API.
    """
    
    # Simple prompt to create a PR
    prompt = """
    Repository: taylor-curran/prefect-fork
    
    Make a small change to the readme.md
    
    Definition of done:
    - Comment added to README.md
    - Pull request created
    """
    
    print("🚀 Testing PR creation and info retrieval")
    print("📋 Target repo: taylor-curran/prefect-fork\n")
    
    api_key = os.getenv("DEVIN_API_KEY")
    if not api_key:
        print("❌ DEVIN_API_KEY not found!")
        sys.exit(1)
    
    try:
        # Phase 1: Run session until blocked
        print("Phase 1: Running session...")
        session_info = run_session_until_blocked(
            prompt=prompt,
            title="Test: PR Info Retrieval",
            api_key=api_key,
            poll_interval=10
        )
        
        session_id = session_info["session_id"]
        print(f"✅ Session reached {session_info['status']} state")
        print(f"🔗 Session: {session_info['session_url']}")
        
        # Phase 2: Send sleep and wait for completion
        print("\nPhase 2: Ending session...")
        send_sleep_message(api_key, session_id)
        wait_for_status(api_key, session_id, ["finished", "expired"], poll_interval=10)
        
        # Phase 3: Get full enterprise session data
        print("\nPhase 3: Fetching PR information...")
        enterprise_data = get_full_enterprise_session(api_key, session_id)
        
        print(f"\n⏱️  Total time: {session_info['execution_time']:.1f}s")
        
        # Check for PRs in the response
        prs = enterprise_data.get("prs", [])
        if prs:
            print(f"\n🎉 Found {len(prs)} PR(s):")
            for pr in prs:
                print(f"  📍 URL: {pr.get('pr_url')}")
                print(f"     State: {pr.get('state')}")
        else:
            print("\n⚠️  No PRs found in session")
        
        # Also show session analysis if available
        if enterprise_data.get("session_analysis"):
            analysis = enterprise_data["session_analysis"]
            if analysis.get("issues"):
                print(f"\n📊 Issues found: {len(analysis['issues'])}")
            if analysis.get("action_items"):
                print(f"📝 Action items: {len(analysis['action_items'])}")
        
        return enterprise_data
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    test_pr_creation()
