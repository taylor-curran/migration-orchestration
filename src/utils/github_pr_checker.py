"""GitHub PR status checker utility."""

import os
import time
import httpx
from typing import List, Dict, Any, Optional
from prefect.logging import get_run_logger


def parse_pr_url(pr_url: str) -> Optional[Dict[str, str]]:
    """Parse a GitHub PR URL to extract owner, repo, and PR number.
    
    Args:
        pr_url: GitHub PR URL like https://github.com/owner/repo/pull/123
    
    Returns:
        Dict with owner, repo, and pr_number, or None if invalid
    """
    try:
        parts = pr_url.strip().rstrip('/').split('/')
        if len(parts) >= 7 and parts[-2] == 'pull':
            return {
                'owner': parts[-4],
                'repo': parts[-3],
                'pr_number': parts[-1]
            }
    except:
        pass
    return None


def get_pr_status_from_github(pr_url: str) -> Dict[str, Any]:
    """Get PR status directly from GitHub API.
    
    Args:
        pr_url: GitHub PR URL
    
    Returns:
        Dict with PR status information
    """
    parsed = parse_pr_url(pr_url)
    if not parsed:
        return {'error': f'Invalid PR URL: {pr_url}'}
    
    api_url = f"https://api.github.com/repos/{parsed['owner']}/{parsed['repo']}/pulls/{parsed['pr_number']}"
    
    # Use GitHub token if available for better rate limits
    headers = {'Accept': 'application/vnd.github.v3+json'}
    github_token = os.getenv('GITHUB_TOKEN')
    if github_token:
        headers['Authorization'] = f'token {github_token}'
    
    try:
        with httpx.Client(timeout=httpx.Timeout(10.0)) as client:
            response = client.get(api_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'pr_url': pr_url,
                    'title': data.get('title', 'Unknown'),
                    'state': data.get('state', 'unknown'),  # 'open' or 'closed'
                    'merged': data.get('merged', False),
                    'mergeable': data.get('mergeable'),
                    'draft': data.get('draft', False),
                    'created_at': data.get('created_at'),
                    'merged_at': data.get('merged_at'),
                    'error': None
                }
            else:
                return {
                    'pr_url': pr_url,
                    'error': f'GitHub API returned {response.status_code}'
                }
                
    except Exception as e:
        return {
            'pr_url': pr_url,
            'error': f'Failed to check PR: {str(e)}'
        }


def wait_for_prs_to_merge_github(
    pr_urls: List[str],
    poll_interval: int = 30,
    max_wait_minutes: int = 60
) -> bool:
    """Wait for GitHub PRs to be merged using GitHub API.
    
    Args:
        pr_urls: List of GitHub PR URLs to monitor
        poll_interval: Seconds between checks
        max_wait_minutes: Maximum time to wait
    
    Returns:
        True if all PRs are merged, False if timeout
    """
    logger = get_run_logger()
    
    if not pr_urls:
        logger.info("📭 No PRs to wait for")
        return True
    
    # Track PR status
    pr_tracking = [{'url': url, 'merged': False} for url in pr_urls]
    
    logger.info(f"⏳ Waiting for {len(pr_urls)} PR(s) to be merged...")
    for pr in pr_tracking:
        logger.info(f"   • {pr['url']}")
    
    # Check for GitHub token
    if not os.getenv('GITHUB_TOKEN'):
        logger.warning("⚠️ No GITHUB_TOKEN found - API rate limits may apply")
        logger.info("   Set GITHUB_TOKEN environment variable for better rate limits")
    
    start_time = time.time()
    max_wait_seconds = max_wait_minutes * 60
    
    while True:
        # Check each PR status
        all_merged = True
        
        for pr_info in pr_tracking:
            if pr_info['merged']:
                continue  # Already merged
            
            status = get_pr_status_from_github(pr_info['url'])
            
            if status.get('error'):
                logger.warning(f"   ⚠️ Error checking {pr_info['url']}: {status['error']}")
                all_merged = False
            elif status.get('merged'):
                pr_info['merged'] = True
                logger.info(f"   ✅ PR merged: {pr_info['url']}")
            elif status.get('state') == 'closed':
                logger.warning(f"   ⚠️ PR closed without merging: {pr_info['url']}")
                pr_info['merged'] = True  # Consider it "done"
            else:
                all_merged = False
        
        if all_merged:
            logger.info("🎉 All PRs have been merged!")
            return True
        
        # Check timeout
        elapsed = time.time() - start_time
        if elapsed >= max_wait_seconds:
            logger.warning(f"⏱️ Timeout after {max_wait_minutes} minutes")
            unmerged = [pr['url'] for pr in pr_tracking if not pr['merged']]
            if unmerged:
                logger.warning(f"   Unmerged PRs: {', '.join(unmerged)}")
            return False
        
        # Show progress
        merged_count = sum(1 for pr in pr_tracking if pr['merged'])
        wait_minutes = int(elapsed / 60)
        logger.info(f"   Progress: {merged_count}/{len(pr_tracking)} merged (waiting {wait_minutes} minutes)")
        
        # Wait before next check
        time.sleep(poll_interval)


def extract_pr_urls_from_results(session_results: List[Dict[str, Any]]) -> List[str]:
    """Extract all PR URLs from session results.
    
    Args:
        session_results: List of session result dictionaries
    
    Returns:
        List of PR URLs
    """
    pr_urls = []
    for result in session_results:
        if result.get('prs'):
            for pr in result['prs']:
                if pr.get('pr_url'):
                    pr_urls.append(pr['pr_url'])
    return pr_urls
