#!/usr/bin/env python3
"""
Test script to retrieve structured output from a Devin session.
"""

import os
import sys
import httpx
import json
import re
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()


def extract_json_from_text(text: str) -> Optional[dict]:
    """Extract JSON from text, handling markdown code blocks."""
    # Try to find JSON in code blocks first
    json_patterns = [
        r'```json\s*\n(.*?)\n```',  # JSON code blocks
        r'```\s*\n(\{.*?\})\s*\n```',  # Generic code blocks with JSON
        r'```\s*\n(\[.*?\])\s*\n```',  # Generic code blocks with JSON arrays
        r'(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})',  # Nested JSON objects
        r'(\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\])',  # JSON arrays
    ]
    
    for pattern in json_patterns:
        matches = re.findall(pattern, text, re.DOTALL | re.MULTILINE)
        for match in matches:
            try:
                # Clean up the match
                cleaned = match.strip()
                result = json.loads(cleaned)
                # Only return if it's a dict or has meaningful content
                if isinstance(result, dict) and result:
                    return result
                elif isinstance(result, list) and result:
                    # If it's a list, wrap it in a dict
                    return {"data": result}
            except json.JSONDecodeError:
                continue
    
    # Try to parse the entire text as JSON
    try:
        result = json.loads(text.strip())
        if isinstance(result, dict):
            return result
        elif isinstance(result, list):
            return {"data": result}
    except json.JSONDecodeError:
        return None


def search_messages_for_structured_output(messages: list) -> Optional[dict]:
    """Search through messages for structured output."""
    structured_output_keywords = [
        "structured output",
        "structured_output",
        "json output",
        "migration status",
        "progress update",
        "final output",
        "result:",
        "status update",
        "here's the json",
        "json:",
        "output:"
    ]
    
    # Track best match
    best_match = None
    best_score = 0
    
    # Search from most recent messages first
    for message in reversed(messages):
        if message.get("type") == "devin_message":
            msg_text = message.get("message", "")
            msg_lower = msg_text.lower()
            
            # Calculate relevance score
            score = sum(1 for keyword in structured_output_keywords if keyword in msg_lower)
            
            # Try to extract JSON from messages with keywords or any message with JSON-like content
            if score > 0 or "```" in msg_text or "{" in msg_text:
                extracted = extract_json_from_text(msg_text)
                if extracted:
                    # Prefer messages with higher keyword match scores
                    if score > best_score:
                        best_match = extracted
                        best_score = score
                    elif best_match is None:
                        best_match = extracted
    
    return best_match


def download_and_check_attachments(session_data: dict, api_key: str) -> Optional[dict]:
    """Check for attachments that might contain structured output."""
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # Look for attachment references in messages
    for message in session_data.get("messages", []):
        msg_text = message.get("message", "")
        
        # Look for attachment URLs or references
        attachment_patterns = [
            r'https://api\.devin\.ai/v1/attachments/([^/]+)/([^\s]+\.json)',
            r'attachment/([^/]+)/([^\s]+\.json)',
            r'/v1/attachments/([^/]+)/([^\s]+)',
        ]
        
        for pattern in attachment_patterns:
            matches = re.findall(pattern, msg_text)
            for match in matches:
                if isinstance(match, tuple) and len(match) == 2:
                    uuid, filename = match
                    print(f"   📎 Found attachment: {filename}")
                    
                    # Try to download the attachment
                    attachment_url = f"https://api.devin.ai/v1/attachments/{uuid}/{filename}"
                    try:
                        with httpx.Client(follow_redirects=True) as client:
                            response = client.get(attachment_url, headers=headers)
                            if response.status_code == 200:
                                # Try to parse as JSON
                                try:
                                    content = response.json()
                                    print(f"   ✅ Successfully downloaded and parsed {filename}")
                                    return content
                                except json.JSONDecodeError:
                                    # Try to extract JSON from text content
                                    extracted = extract_json_from_text(response.text)
                                    if extracted:
                                        print(f"   ✅ Extracted JSON from {filename}")
                                        return extracted
                    except Exception as e:
                        print(f"   ⚠️ Could not download {filename}: {e}")
        
        # Also look for inline file content in messages
        if "```json" in msg_text or "output.json" in msg_text.lower():
            extracted = extract_json_from_text(msg_text)
            if extracted:
                print("   📋 Found inline JSON content in message")
                return extracted
    
    return None


def retrieve_structured_output(session_id: str, debug: bool = False) -> dict:
    """Retrieve structured output from a Devin session."""
    
    # Get API key
    api_key = os.environ.get("DEVIN_API_KEY")
    if not api_key:
        raise ValueError("DEVIN_API_KEY not found in environment")
    
    # Make API request to get session details
    url = f"https://api.devin.ai/v1/sessions/{session_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    print(f"📡 Retrieving structured output for session: {session_id}")
    
    with httpx.Client() as client:
        response = client.get(url, headers=headers)
        response.raise_for_status()
    
    session_data = response.json()
    
    if debug:
        print("\n🔍 DEBUG: Session data structure:")
        print(f"   - Status: {session_data.get('status')}")
        print(f"   - Status Enum: {session_data.get('status_enum')}")
        print(f"   - Messages Count: {len(session_data.get('messages', []))}")
        print(f"   - Has structured_output: {'Yes' if session_data.get('structured_output') else 'No'}")
        if session_data.get('structured_output'):
            print(f"   - Structured Output Type: {type(session_data.get('structured_output'))}")

    # Primary method: Check structured_output field
    structured_output = session_data.get("structured_output", {})
    
    if structured_output:
        print("✅ Structured output retrieved from primary field!")
        print(f"   Keys found: {list(structured_output.keys())}")
        return structured_output
    
    print("⚠️  No structured output in primary field, trying fallback methods...")
    
    # Fallback 1: Search messages for structured output
    messages = session_data.get("messages", [])
    if messages:
        print(f"   🔍 Searching through {len(messages)} messages...")
        if debug:
            # Show message types in debug mode
            msg_types = {}
            for msg in messages:
                msg_type = msg.get("type", "unknown")
                msg_types[msg_type] = msg_types.get(msg_type, 0) + 1
            print(f"      Message types: {msg_types}")
        
        from_messages = search_messages_for_structured_output(messages)
        if from_messages:
            print("✅ Structured output found in messages!")
            print(f"   Keys found: {list(from_messages.keys())}")
            return from_messages
    
    # Fallback 2: Check for attachment references
    print("   📁 Checking for file attachments...")
    from_attachments = download_and_check_attachments(session_data, api_key)
    if from_attachments:
        print("✅ Structured output found in attachments!")
        return from_attachments
    
    # Fallback 3: Try to extract any JSON from the last Devin message
    print("   🔎 Attempting to extract JSON from last Devin message...")
    for message in reversed(messages):
        if message.get("type") == "devin_message":
            extracted = extract_json_from_text(message.get("message", ""))
            if extracted:
                print("✅ JSON extracted from Devin message!")
                print(f"   Keys found: {list(extracted.keys())}")
                return extracted
            break
    
    print("❌ No structured output found in any location")
    return {}


def print_usage():
    """Print usage information."""
    print("""
📖 Usage: python test_structured_out_retrieval.py [SESSION_ID|URL] [OPTIONS]

Arguments:
  SESSION_ID    Devin session ID (with or without 'devin-' prefix)
  URL           Full Devin session URL from browser

Options:
  --debug, -d   Show debug information about session structure
  --help, -h    Show this help message

Examples:
  python test_structured_out_retrieval.py devin-a8d08bff86014907abe6576f7459cf88
  python test_structured_out_retrieval.py a8d08bff86014907abe6576f7459cf88
  python test_structured_out_retrieval.py https://app.devin.ai/sessions/a8d08bff86014907abe6576f7459cf88
  python test_structured_out_retrieval.py "https://app.devin.ai/sessions/a8d08bff86014907abe6576f7459cf88?tab=editor" --debug

Fallback Methods:
  1. Primary structured_output field (recommended)
  2. Search messages for JSON content with relevant keywords
  3. Download and parse file attachments
  4. Extract JSON from any Devin message
    """)

def main():
    # Check for help flag
    if "--help" in sys.argv or "-h" in sys.argv:
        print_usage()
        return
    
    # Check for debug flag
    debug = "--debug" in sys.argv or "-d" in sys.argv
    args = [arg for arg in sys.argv[1:] if arg not in ["--debug", "-d", "--help", "-h"]]
    
    # Get session ID from command line or use default
    if args:
        # Accept either full URL or just the session ID
        arg = args[0].strip()
        
        # Handle different URL formats
        if "devin.ai/sessions/" in arg:
            # Extract session ID from URL (handles both http and https)
            # Example: https://app.devin.ai/sessions/a8d08bff86014907abe6576f7459cf88
            parts = arg.split("/sessions/")
            if len(parts) > 1:
                session_id_part = parts[-1].split("?")[0].split("#")[0].strip()  # Remove query params or anchors
                session_id = "devin-" + session_id_part
            else:
                print(f"⚠️  Could not extract session ID from URL: {arg}")
                return
        elif arg.startswith("devin-"):
            # Already has the prefix
            session_id = arg
        else:
            # Just the session ID without prefix
            session_id = "devin-" + arg
    else:
        # Default hardcoded session ID from URL
        # https://app.devin.ai/sessions/a6fecde8a4c94038ade87d62c369b543
        session_id = "devin-a6fecde8a4c94038ade87d62c369b543"  # Need 'devin-' prefix for API
    
    print("🚀 Testing structured output retrieval")
    print(f"   Session: {session_id}")
    if debug and args:
        print(f"   Input: {args[0]}")
    print("-" * 50)
    
    try:
        structured_output = retrieve_structured_output(session_id, debug=debug)
        
        if structured_output:
            print("\n📄 Structured Output:")
            print(json.dumps(structured_output, indent=2))
        else:
            print("\n❌ No structured output found after checking all sources")
            print("\nChecked locations:")
            print("1. Primary structured_output field")
            print("2. Messages containing structured data")
            print("3. File attachments (if any)")
            print("4. JSON extraction from Devin messages")
            print("\nTips for getting structured output:")
            print("- Include a JSON schema in your prompt")
            print("- Ask Devin to 'update structured output' explicitly")
            print("- Request output in a specific JSON format")
            
    except httpx.HTTPStatusError as e:
        print(f"\n❌ API Error: {e.response.status_code}")
        print(f"   Response: {e.response.text}")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
    print()  # Extra newline for cleaner output
