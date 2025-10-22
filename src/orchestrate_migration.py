from asyncio import Task, taskgroups
from prefect import flow
from tasks.run_sessions import run_session_and_wait_for_analysis
from typing import Optional, Dict, Any

@flow(log_prints=True)
def orchestrate_migration(
    initial_prompt: str, 
    title: str,
    structured_output_schema: Optional[Dict[str, Any]] = None
):
    """
    Orchestrate a migration analysis with optional structured output.
    
    Args:
        initial_prompt: The task prompt for Devin
        title: Session title
        structured_output_schema: Optional schema fields to include in request body
    """
    result = run_session_and_wait_for_analysis(
        prompt=initial_prompt,
        title=title,
        structured_output_schema=structured_output_schema,
    )
    return result


if __name__ == "__main__":
    # Define the structured output schema - these fields will be added directly to the request body
    structured_output_schema = {
        "tasks": [
            {
                "title": "Example task title",
                "prompt": "Example task prompt for another agent",
                "definition_of_done": "Example completion criteria"
            }
        ],
        "status": "0% complete - starting analysis",
        "context": "Initial migration context"
    }
    
    # The prompt references the structured output fields that are already in the request body
    initial_prompt = """
!ask Analyze migration from taylor-curran/og-cics-cobol-app to taylor-curran/target-springboot-cics

IMPORTANT: Update the structured output immediately and continuously as you analyze.

The structured output has been initialized with template fields. Update them with your analysis:
- Identify exactly 3 parallel, independent tasks for the migration
- Replace the example tasks with specific, actionable migration tasks
- Update the status field as you progress (e.g., "25% complete - analyzing repository structure")
- Update the context field with key findings about the migration

Requirements for the tasks:
- The 3 tasks must be completely independent (can be done in parallel)
- Each task.prompt should be self-contained - assume the agent hasn't seen the repos before
- Include specific file paths, method names, or other details the downstream agent will need
- Each task.definition_of_done should include clear acceptance criteria, often including passing tests

DO NOT FORGET TO UPDATE STRUCTURED OUTPUT BEFORE FINISHING YOUR WORK
    """
    
    title = "Migration Analysis - Parallel Tasks with Structured Output 2"

    # Run the orchestration with the structured output schema
    result = orchestrate_migration(
        initial_prompt=initial_prompt, 
        title=title,
        structured_output_schema=structured_output_schema
    )
    
    # Print the structured output if available
    if result and result.get("structured_output"):
        import json
        print("\n📋 Structured Output Retrieved:")
        print(json.dumps(result["structured_output"], indent=2))
