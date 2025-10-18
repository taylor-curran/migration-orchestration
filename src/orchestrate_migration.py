from prefect import flow
from tasks.run_sessions import run_session_and_wait_for_analysis


@flow(log_prints=True)
def orchestrate_migration():
    run_session_and_wait_for_analysis(
        prompt="Create a simple Python function that calculates fibonacci numbers. Include docstring and type hints.",
        title="Fibonacci Function",
    )


if __name__ == "__main__":
    orchestrate_migration()
