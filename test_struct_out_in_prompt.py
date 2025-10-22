import os
import httpx
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

def create_session_with_structured_prompt(prompt: str, title: Optional[str] = None) -> str:
    """Create a new Devin session with structured output schema in the prompt."""
    
    api_key = os.environ.get("DEVIN_API_KEY")
    if not api_key:
        raise ValueError("DEVIN_API_KEY not found in environment")
    
    url = "https://api.devin.ai/v1/sessions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # Standard request without structured_output in body
    data = {
        "prompt": prompt,
        "title": title or "Orchestrated Session",
        "idempotent": False
    }
    
    print("📝 Sending structured output schema in prompt text")
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
    # Use exact phrasing from memory: "Please provide structured output in this exact JSON format"
    initial_prompt = """
Analyze migration from taylor-curran/og-cics-cobol-app to taylor-curran/target-springboot-cics

Please provide structured output in this exact JSON format:
{
    "tasks": [
        {
            "title": "Short descriptive title",
            "prompt": "Complete prompt for another agent including: context about what exists, what needs to be done, any constraints or requirements",
            "definition_of_done": "Clear criteria for completion that another agent can verify"
        }
    ],
    "status": "0% complete - starting",
    "context": "Migration analysis context"
}

Update the structured output immediately and continuously as you work:
- Identify exactly 3 parallel, independent tasks for the migration
- Update status field as you progress (e.g., "25% complete - analyzing source")
- Update context field with key findings about the migration
- Keep updating the structured output throughout your analysis
    """
    title = "Migration Analysis - Structured Schema Test"

    try:
        # Create session with structured schema in the prompt
        session_id = create_session_with_structured_prompt(initial_prompt, title)
        
        # Poll for structured output
        import time
        import json
        
        api_key = os.environ.get("DEVIN_API_KEY")
        url = f"https://api.devin.ai/v1/sessions/{session_id}"
        headers = {"Authorization": f"Bearer {api_key}"}
        
        print("\n📡 Polling for structured output...")
        max_polls = 12  # Check for 2 minutes  
        poll_interval = 10
        
        for i in range(max_polls):
            time.sleep(poll_interval)
            
            with httpx.Client() as client:
                response = client.get(url, headers=headers)
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
