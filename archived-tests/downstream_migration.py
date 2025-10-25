from prefect import flow, task
from prefect.logging import get_run_logger
from tasks.run_sessions import run_session_and_wait_for_analysis
from typing import Optional, Dict, Any, List
import json
from concurrent.futures import ThreadPoolExecutor, as_completed


@task
def run_downstream_session(
    task_data: Dict[str, Any], task_index: int
) -> Dict[str, Any]:
    """Run a single downstream session for a specific task."""
    logger = get_run_logger()

    task_title = task_data.get("title", f"Task {task_index + 1}")
    task_prompt = task_data.get("prompt", "")
    definition_of_done = task_data.get("definition_of_done", "")

    # Combine prompt with definition of done for the downstream session
    full_prompt = f"{task_prompt}\n\nDefinition of Done:\n{definition_of_done}"

    logger.info(f"🚀 Starting downstream session {task_index + 1}: {task_title}")

    # Run the downstream session
    result = run_session_and_wait_for_analysis(
        prompt=full_prompt, title=f"Downstream Task {task_index + 1}: {task_title}"
    )

    logger.info(f"✅ Completed downstream session {task_index + 1}: {task_title}")

    return {
        "task_index": task_index,
        "task_title": task_title,
        "session_result": result,
    }


@flow(log_prints=False)
def orchestrate_migration(
    initial_prompt: str,
    title: str,
    structured_output_schema: Optional[Dict[str, Any]] = None,
    run_downstream: bool = True,
    max_downstream_sessions: Optional[int] = None,
):
    """
    Orchestrate a migration analysis with optional structured output and downstream sessions.

    Args:
        initial_prompt: The task prompt for Devin
        title: Session title
        structured_output_schema: Optional schema fields to include in request body
        run_downstream: Whether to run downstream sessions based on tasks in structured output
        max_downstream_sessions: Maximum number of downstream sessions to run (None = all tasks)

    Returns:
        Dict containing initial session result and downstream session results
    """
    logger = get_run_logger()

    # Step 1: Run initial analysis session
    logger.info("📋 Starting initial analysis session...")
    initial_result = run_session_and_wait_for_analysis(
        prompt=initial_prompt,
        title=title,
        structured_output_schema=structured_output_schema,
    )

    # Check if we got structured output
    structured_output = initial_result.get("structured_output")

    if not structured_output:
        logger.warning("⚠️ No structured output received from initial session")
        return {"initial_session": initial_result, "downstream_sessions": []}

    logger.info("✅ Structured output received from initial session")

    # Step 2: Extract tasks from structured output
    tasks = structured_output.get("tasks", [])

    if not tasks:
        logger.warning("⚠️ No tasks found in structured output")
        return {"initial_session": initial_result, "downstream_sessions": []}

    logger.info(f"📊 Found {len(tasks)} tasks in structured output")

    # Limit tasks if max_downstream_sessions is specified
    if max_downstream_sessions is not None:
        if len(tasks) > max_downstream_sessions:
            logger.info(f"🔢 Limiting to {max_downstream_sessions} downstream sessions")
        tasks = tasks[:max_downstream_sessions]

    # Step 3: Run downstream sessions if enabled
    downstream_results = []

    if run_downstream:
        logger.info(f"🎯 Running {len(tasks)} downstream sessions in parallel...")

        # Submit all tasks for parallel execution
        futures = []
        for i, task_data in enumerate(tasks):
            logger.info(f"   Task {i + 1}: {task_data.get('title', 'Untitled')}")
            future = run_downstream_session.submit(task_data, i)
            futures.append(future)

        # Wait for all tasks to complete
        for future in futures:
            result = future.result()
            downstream_results.append(result)
            logger.info(f"   ✓ Task {result['task_index'] + 1} completed")

        logger.info(f"✅ All {len(downstream_results)} downstream sessions completed")
    else:
        logger.info("⏭️ Skipping downstream sessions (run_downstream=False)")

    return {
        "initial_session": initial_result,
        "structured_output": structured_output,
        "downstream_sessions": downstream_results,
        "num_tasks": len(tasks),
    }


if __name__ == "__main__":
    # Define the structured output schema - these fields will be added directly to the request body
    structured_output_schema = {
        "tasks": [
            {
                "title": "Example task title",
                "prompt": "Example task prompt for another agent",
                "definition_of_done": "Example completion criteria",
            }
        ],
        "status": "0% complete - starting analysis",
        "context": "Initial migration context",
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

    # Run the orchestration with the structured output schema and downstream sessions
    result = orchestrate_migration(
        initial_prompt=initial_prompt,
        title=title,
        structured_output_schema=structured_output_schema,
        run_downstream=True,  # Enable downstream session execution
        max_downstream_sessions=3,  # Parameterized limit for downstream sessions
    )

    # Print results summary
    print("\n" + "=" * 60)
    print("📊 ORCHESTRATION RESULTS SUMMARY")
    print("=" * 60)

    # Print structured output if available
    if result and result.get("structured_output"):
        print("\n📋 Structured Output Retrieved:")
        print(json.dumps(result["structured_output"], indent=2))

    # Print downstream session results
    if result.get("downstream_sessions"):
        print(
            f"\n🎯 Downstream Sessions Completed: {len(result['downstream_sessions'])}"
        )
        for session in result["downstream_sessions"]:
            print(f"   - Task {session['task_index'] + 1}: {session['task_title']}")
            print(f"     Session ID: {session['session_result']['session_id']}")
            print(f"     URL: {session['session_result']['session_url']}")
    else:
        print("\n⚠️ No downstream sessions were run")

    print("\n" + "=" * 60)
