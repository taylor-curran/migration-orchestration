import os
import httpx
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

def create_session_with_schema_fields(prompt: str, title: Optional[str] = None) -> str:
    """Create a new Devin session with schema fields added directly to request body."""
    
    api_key = os.environ.get("DEVIN_API_KEY")
    if not api_key:
        raise ValueError("DEVIN_API_KEY not found in environment")
    
    url = "https://api.devin.ai/v1/sessions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # Add schema fields DIRECTLY to the request body (not nested)
    data = {
        "prompt": prompt,
        "title": title or "Orchestrated Session",
        "idempotent": False,
        # Schema fields added directly to body
        "tasks": [
            {
                "title": "Example task title",
                "prompt": "Example task prompt",
                "definition_of_done": "Example completion criteria"
            }
        ],
        "status": "0% complete - starting",
        "context": "Initial migration context"
    }
    
    print("🧪 Adding schema fields directly to request body (not nested)")
    print(f"📤 Request data keys: {list(data.keys())}")
    
    with httpx.Client() as client:
        response = client.post(url, headers=headers, json=data)
        response.raise_for_status()
    
    result = response.json()
    session_id = result["session_id"]
    
    print(f"✅ Session created: {session_id}")
    print(f"   View at: {result['url']}")
    
    return session_id


if __name__ == "__main__":
    # Tell Devin to use structured output (schema is in request body)
    initial_prompt = """
Analyze migration from taylor-curran/og-cics-cobol-app to taylor-curran/target-springboot-cics

IMPORTANT: Please update the structured output field immediately when you start and continuously as you analyze.
The structured output format has been provided in the request. Update these fields:
- tasks: Array of 3 parallel migration tasks
- status: Your progress percentage and current activity  
- context: Key findings about the migration

Make sure to update the structured output multiple times as you work.
    """
    title = "Migration Analysis - Body Fields + Explicit Prompt"

    try:
        # Create session with schema fields directly in request body
        session_id = create_session_with_schema_fields(initial_prompt, title)
        
        import time
        import json
        
        api_key = os.environ.get("DEVIN_API_KEY")
        base_url = f"https://api.devin.ai/v1/sessions/{session_id}"
        headers = {"Authorization": f"Bearer {api_key}"}
        
        # Step 1: Wait for session to reach 'blocked' state
        print("\n⏳ Waiting for session to reach blocked state...")
        max_wait = 30  # Wait up to 5 minutes for quick test (30 * 10 seconds)
        poll_interval = 10
        
        for i in range(max_wait):
            time.sleep(poll_interval)
            
            with httpx.Client() as client:
                response = client.get(base_url, headers=headers)
                session_data = response.json()
                status = session_data.get("status_enum", "unknown")
                
                elapsed_min = (i + 1) * poll_interval / 60
                print(f"   [{i+1}/{max_wait}] Status: {status} (elapsed: {elapsed_min:.1f} min)")
                
                if status == "blocked":
                    print(f"   ✅ Session reached blocked state after {elapsed_min:.1f} minutes")
                    break
                elif status in ["finished", "expired"]:
                    print(f"   ⚠️ Session ended early with status: {status} after {elapsed_min:.1f} minutes")
                    break
        
        # Step 2: Send sleep message if blocked
        if status == "blocked":
            print("\n📨 Sending sleep message to end session...")
            message_url = f"{base_url}/message"
            with httpx.Client() as client:
                response = client.post(message_url, 
                                      headers={**headers, "Content-Type": "application/json"},
                                      json={"message": "sleep"})
                response.raise_for_status()
                print("   ✅ Sleep message sent")
            
            # Wait for session to finish
            time.sleep(10)
        
        # Step 3: Now poll for structured output
        print("\n📡 Polling for structured output (after session ended)...")
        max_polls = 12  # Check for 2 minutes
        
        for i in range(max_polls):
            time.sleep(poll_interval)
            
            with httpx.Client() as client:
                response = client.get(base_url, headers=headers)
                session_data = response.json()
                
                status = session_data.get("status_enum", "unknown")
                structured_output = session_data.get("structured_output")
                
                print(f"   [{i+1}/{max_polls}] Status: {status}", end="")
                
                if structured_output:
                    print(" - ✅ Structured output found!")
                    print("\n📄 Structured Output:")
                    print(json.dumps(structured_output, indent=2))
                    break
                else:
                    print(" - No structured output yet")
        else:
            print("\n❌ No structured output found after polling")
                
        print(f"\n🔗 Session URL: https://app.devin.ai/sessions/{session_id.replace('devin-', '')}")
        
    except httpx.HTTPStatusError as e:
        print(f"❌ API Error: {e.response.status_code}")
        print(f"   Response: {e.response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
