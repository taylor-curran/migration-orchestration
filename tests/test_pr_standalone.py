#!/usr/bin/env python3
"""
Standalone test for PR info retrieval - no Prefect dependencies.
"""

import os
import sys
import time
import httpx
from pathlib import Path
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()


def create_session(api_key: str, prompt: str, title: str):
    """Create a Devin session."""
    url = "https://api.devin.ai/v1/sessions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "prompt": prompt,
        "title": title,
        "idempotent": False
    }
    
    with httpx.Client(timeout=httpx.Timeout(30.0)) as client:
        response = client.post(url, headers=headers, json=data)
        response.raise_for_status()
    
    result = response.json()
    return result["session_id"], result["url"]


def get_session_status(api_key: str, session_id: str):
    """Check session status."""
    url = f"https://api.devin.ai/v1/sessions/{session_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    with httpx.Client(timeout=httpx.Timeout(30.0)) as client:
        response = client.get(url, headers=headers)
        response.raise_for_status()
    
    return response.json()


def wait_for_blocked(api_key: str, session_id: str):
    """Wait for session to reach blocked state."""
    print("⏳ Waiting for session to complete work...")
    while True:
        status_data = get_session_status(api_key, session_id)
        status = status_data.get("status_enum")
        print(f"   Status: {status}")
        
        if status in ["blocked", "finished", "expired"]:
            return status
        
        time.sleep(10)


def send_sleep_message(api_key: str, session_id: str):
    """Send sleep message to end session."""
    url = f"https://api.devin.ai/v1/sessions/{session_id}/message"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"message": "sleep"}
    
    with httpx.Client(timeout=httpx.Timeout(30.0)) as client:
        response = client.post(url, headers=headers, json=data)
        response.raise_for_status()
    
    print("💤 Sleep message sent")


def get_pr_info(api_key: str, session_id: str):
    """Get PR info from enterprise API."""
    url = f"https://api.devin.ai/beta/v2/enterprise/sessions/{session_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    with httpx.Client(timeout=httpx.Timeout(30.0)) as client:
        response = client.get(url, headers=headers)
        response.raise_for_status()
    
    return response.json()


def main():
    # Check for API key
    api_key = os.getenv("DEVIN_API_KEY")
    if not api_key:
        print("❌ DEVIN_API_KEY not found in environment")
        sys.exit(1)
    
    # Simple prompt
    prompt = """
    Repository: taylor-curran/prefect-fork
    
    Make a small change to the readme.md - add a comment or update a section.
    Create a pull request with your changes.
    
    Definition of done:
    - Change made to README.md
    - Pull request created
    """
    
    print("🚀 Starting PR test session\n")
    
    try:
        # 1. Create session
        print("Step 1: Creating session...")
        session_id, session_url = create_session(
            api_key, 
            prompt, 
            "Test: PR Info Retrieval"
        )
        print(f"✅ Session created: {session_id}")
        print(f"🔗 View at: {session_url}\n")
        
        # 2. Wait for completion
        print("Step 2: Waiting for work completion...")
        final_status = wait_for_blocked(api_key, session_id)
        print(f"✅ Session reached {final_status} state\n")
        
        # 3. Send sleep if needed
        if final_status == "blocked":
            print("Step 3: Ending session...")
            send_sleep_message(api_key, session_id)
            time.sleep(5)  # Give it time to process
            print()
        
        # 4. Get PR info
        print("Step 4: Fetching PR information...")
        enterprise_data = get_pr_info(api_key, session_id)
        
        # Display PR info
        prs = enterprise_data.get("prs", [])
        if prs:
            print(f"\n🎉 Success! Found {len(prs)} PR(s):")
            for pr in prs:
                print(f"\n  📍 PR URL: {pr.get('pr_url')}")
                print(f"     State: {pr.get('state')}")
                
                # Extract PR number from URL if available
                pr_url = pr.get('pr_url', '')
                if '/pull/' in pr_url:
                    pr_num = pr_url.split('/pull/')[-1]
                    print(f"     Number: #{pr_num}")
        else:
            print("\n⚠️  No PRs found in session")
        
        # Also show some analysis if available
        if enterprise_data.get("session_analysis"):
            analysis = enterprise_data["session_analysis"]
            print(f"\n📊 Session Analysis:")
            if analysis.get("issues"):
                print(f"   Issues: {len(analysis['issues'])}")
            if analysis.get("action_items"):
                print(f"   Action items: {len(analysis['action_items'])}")
        
        print(f"\n✅ Test complete!")
        return enterprise_data
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
