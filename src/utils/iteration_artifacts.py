"""Artifacts for prompt iteration flows."""
from typing import List
from prefect.artifacts import create_markdown_artifact


def create_progress_artifact(prompt_history: List[str], session_ids: List[str], max_iterations: int):
    """Create a simple artifact showing prompt evolution progress."""
    
    md = "# 📈 Prompt Iteration Progress\n\n"
    md += f"**Total Iterations**: {len(session_ids)}\n"
    md += f"**Max Iterations**: {max_iterations}\n"
    md += f"**Unique Prompts**: {len(set(prompt_history))}\n\n"
    
    md += "## 🔄 Prompt Evolution\n\n"
    
    for i, prompt in enumerate(prompt_history):
        if i == 0:
            md += f"### 🎯 Initial Prompt\n"
        else:
            md += f"### 💡 Iteration {i} - Improved Prompt\n"
        
        md += f"```\n{prompt}\n```\n\n"
        
        if i < len(session_ids):
            session_id = session_ids[i]
            session_url = f"https://app.devin.ai/sessions/{session_id.replace('devin-', '')}"
            md += f"**Session**: [{session_id}]({session_url})\n\n"
    
    md += "---\n"
    
    # Better stop reason
    if len(session_ids) == max_iterations:
        stop_reason = "✅ Completed all iterations"
    else:
        stop_reason = "⚠️ Stopped early - No further improvements suggested"
    
    md += f"*Status: {stop_reason}*"
    
    create_markdown_artifact(
        key="prompt-iteration-progress",
        markdown=md,
        description="Prompt evolution through iterations"
    )
