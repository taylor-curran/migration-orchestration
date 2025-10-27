#!/usr/bin/env python3
"""Test script to diagnose PR status checking issues."""

import os
import httpx
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent to path
sys.path.append(str(Path(__file__).parent.parent))

def test_session_endpoints():
    """Test different Devin API endpoints to find the right one for PR status."""
    
    api_key = os.getenv("DEVIN_API_KEY")
    if not api_key:
        print("❌ DEVIN_API_KEY not set")
        return
    
    # Session IDs from the terminal output
    session_ids = [
        "3643a4f7686e4c58a39d46ff522a647b",  # setup_001
        "1040cc12774f442282457f66088eba47",  # setup_002 
        "66bf2cb933f24d789fab20f82853466e"   # setup_003
    ]
    
    headers = {"Authorization": f"Bearer {api_key}"}
    
    print("🔍 Testing Different API Endpoints for Session Data:\n")
    
    for session_id in session_ids:
        print(f"\n📋 Session: {session_id}")
        print("=" * 60)
        
        # Test different possible endpoints
        endpoints = [
            # Fixed enterprise endpoint with devin- prefix
            f"https://api.devin.ai/beta/v2/enterprise/sessions/devin-{session_id}",
            # Original failing endpoint (without prefix)
            f"https://api.devin.ai/beta/v2/enterprise/sessions/{session_id}",
            # Try v1 endpoint
            f"https://api.devin.ai/v1/sessions/{session_id}",
            # Try without enterprise
            f"https://api.devin.ai/beta/v2/sessions/{session_id}",
            # Try beta/v1
            f"https://api.devin.ai/beta/v1/sessions/{session_id}",
            # Standard v2 endpoint
            f"https://api.devin.ai/v2/sessions/{session_id}"
        ]
        
        for endpoint in endpoints:
            try:
                with httpx.Client(timeout=httpx.Timeout(10.0)) as client:
                    response = client.get(endpoint, headers=headers)
                    
                    if response.status_code == 200:
                        print(f"✅ SUCCESS: {endpoint}")
                        data = response.json()
                        
                        # Check what data we can get
                        print(f"   - Has PRs field: {'prs' in data}")
                        print(f"   - Has structured_output: {'structured_output' in data}")
                        print(f"   - Has session_analysis: {'session_analysis' in data}")
                        print(f"   - Status: {data.get('status', 'N/A')}")
                        
                        # If PRs exist, show them
                        if 'prs' in data and data['prs']:
                            print(f"   - PRs found: {len(data['prs'])}")
                            for pr in data['prs']:
                                print(f"     • {pr.get('pr_url', 'Unknown URL')} - State: {pr.get('state', 'Unknown')}")
                        
                        # Found working endpoint, no need to test others
                        break
                    else:
                        print(f"❌ {response.status_code}: {endpoint[:50]}...")
                        
            except httpx.HTTPError as e:
                print(f"❌ Error: {endpoint[:50]}... - {str(e)[:50]}")
            except Exception as e:
                print(f"❌ Unexpected error: {endpoint[:50]}... - {str(e)[:50]}")
    
    print("\n" + "=" * 60)
    print("\n💡 Suggestions based on results:")
    print("1. If all endpoints return 404, sessions may have expired")
    print("2. If v1 works but v2 doesn't, update the API endpoint in run_sessions.py")
    print("3. If sessions don't have PR data, we may need a different approach")
    print("4. Consider using GitHub API directly to check PR status")

def test_github_pr_status():
    """Test checking PR status directly from GitHub."""
    
    print("\n🔍 Testing GitHub API for PR Status:\n")
    
    # Example PR URL from terminal output
    pr_url = "https://github.com/taylor-curran/target-springboot-cics/pull/58"
    
    # Parse the URL
    parts = pr_url.split("/")
    owner = parts[-4]
    repo = parts[-3]
    pr_number = parts[-1]
    
    print(f"Repository: {owner}/{repo}")
    print(f"PR Number: {pr_number}")
    
    # GitHub API endpoint
    api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    
    # GitHub token (optional but recommended for rate limits)
    github_token = os.getenv("GITHUB_TOKEN")
    headers = {}
    if github_token:
        headers["Authorization"] = f"token {github_token}"
        print("✅ Using GITHUB_TOKEN for authentication")
    else:
        print("⚠️ No GITHUB_TOKEN found, using unauthenticated requests (rate limited)")
    
    try:
        with httpx.Client(timeout=httpx.Timeout(10.0)) as client:
            response = client.get(api_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ Successfully retrieved PR data:")
                print(f"   - Title: {data.get('title', 'N/A')}")
                print(f"   - State: {data.get('state', 'N/A')}")
                print(f"   - Merged: {data.get('merged', False)}")
                print(f"   - Mergeable: {data.get('mergeable', 'N/A')}")
                print(f"   - Draft: {data.get('draft', False)}")
                print(f"   - Created: {data.get('created_at', 'N/A')}")
                
                # Check merge status
                if data.get('merged'):
                    print(f"   - Merged at: {data.get('merged_at', 'N/A')}")
                    print(f"   - Merged by: {data.get('merged_by', {}).get('login', 'N/A')}")
            else:
                print(f"❌ Failed to get PR data: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
    except Exception as e:
        print(f"❌ Error checking GitHub PR: {e}")
    
    print("\n💡 If GitHub API works, we could:")
    print("1. Store PR URLs when sessions create them")
    print("2. Check PR status directly from GitHub instead of Devin API")
    print("3. This would be more reliable and avoid session expiry issues")

if __name__ == "__main__":
    print("=" * 60)
    print("PR STATUS CHECK DIAGNOSTIC TEST")
    print("=" * 60)
    
    # Test Devin API endpoints
    test_session_endpoints()
    
    # Test GitHub API as alternative
    test_github_pr_status()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
