from prefect import flow
from prefect.logging import get_run_logger
from tasks.run_sessions import run_session_and_wait_for_analysis
from utils.iteration_artifacts import create_progress_artifact
from typing import List, Optional


@flow(log_prints=False)
def iterate_on_prompt(
    initial_prompt: str = "Create a simple Python function that calculates fibonacci numbers. Include docstring and type hints.",
    base_title: str = "Prompt Iteration",
    iterations: int = 3,
) -> List[str]:
    """
    Iterate on a prompt using Devin's suggested improvements.

    Args:
        initial_prompt: The starting prompt to iterate on
        base_title: Base title for the sessions (will append iteration number)
        iterations: Number of iterations (max 10)

    Returns:
        List of session IDs from each iteration
    """
    logger = get_run_logger()

    # Validate iterations
    if iterations > 10:
        logger.warning(f"Iterations capped at 10 (requested: {iterations})")
        iterations = 10

    current_prompt = initial_prompt
    session_ids = []
    prompt_history = [initial_prompt]  # Track prompt evolution

    logger.info(f"🚀 Starting prompt iteration with {iterations} max iterations")
    logger.info(f"📝 Initial prompt: {current_prompt[:100]}...")

    for i in range(iterations):
        logger.info(f"\n--- Iteration {i + 1}/{iterations} ---")
        logger.info(f"📋 Current prompt:\n{current_prompt}\n")

        # Run session with current prompt
        result = run_session_and_wait_for_analysis(
            prompt=current_prompt,
            title=f"{base_title} - Iteration {i + 1}",
        )

        session_ids.append(result["session_id"])
        logger.info(f"✅ Session completed: {result['session_id']}")

        # Check for improved prompt
        improved_prompt = result.get("suggested_prompt")

        if improved_prompt and improved_prompt != current_prompt:
            logger.info(f"💡 Improved prompt found!")
            logger.info(f"📝 New prompt:\n{improved_prompt}\n")
            current_prompt = improved_prompt
            prompt_history.append(improved_prompt)
        else:
            logger.info(f"⚠️ No improved prompt suggested - stopping iteration")
            break

    logger.info(f"\n🎯 Completed {len(session_ids)} iterations")
    logger.info(f"📊 Session IDs: {session_ids}")

    # Create progress artifact
    create_progress_artifact(prompt_history, session_ids, iterations)

    return session_ids


if __name__ == "__main__":
    # Example usage with custom prompt and title
    custom_prompt = """
!ask Carefully analyze the status of migration by comparing the source @taylor-curran/og-cics-cobol-app repo to the target repo @taylor-curran/target-springboot-cics 

Determine the most advantageous next steps to take to make solid progress on the migration.

You only need to look in the following repos: taylor-curran/og-cics-cobol-app, taylor-curran/target-springboot-cics



make a list of the 5 next things that should be done each with a detailed definition of done

Note: You may not need any repos for this task.

    """.strip()

    custom_title = "Migration Analysis - Iteration"

    session_ids = iterate_on_prompt(
        initial_prompt=custom_prompt, base_title=custom_title, iterations=3
    )

    print(f"\nCompleted sessions: {session_ids}")
