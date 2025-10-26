#!/usr/bin/env python3
"""
Super Simple Parallel Session Runner
Just loads a plan, finds ready tasks, and runs them in parallel.
That's it. No loops, no updates, no complexity.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any
from prefect import flow, task
from prefect.logging import get_run_logger

# Add parent to path to import from tasks
sys.path.append(str(Path(__file__).parent.parent))
from src.tasks.run_sessions import run_session_and_wait_for_analysis


def load_plan(repo_path: str) -> Dict[str, Any]:
    """Load migration_plan.py from the target repo."""
    plan_path = Path(repo_path) / "migration_plan.py"
    
    if not plan_path.exists():
        print(f"❌ No migration plan found at: {plan_path}")
        print("   Run the initial plan builder first!")
        sys.exit(1)
    
    # Import the plan
    import importlib.util
    spec = importlib.util.spec_from_file_location("migration_plan", plan_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    return module.migration_plan


def find_ready_tasks(plan: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Find tasks that are ready to run (dependencies completed, status pending)."""
    tasks = plan.get("tasks", [])
    ready = []
    
    # Build status map
    status_map = {t["id"]: t.get("status", "pending") for t in tasks}
    
    for task in tasks:
        # Skip if not pending
        if task.get("status", "pending") != "pending":
            continue
            
        # Check if all dependencies are completed
        deps = task.get("depends_on", [])
        if all(status_map.get(dep) == "completed" for dep in deps):
            ready.append(task)
    
    return ready


def create_task_prompt(task: Dict[str, Any], target_repo: str) -> str:
    """Create a prompt for a specific task."""
    return f"""
# Task: {task['title']}

**Repository**: {target_repo}
**Task ID**: {task['id']}

## Your Mission
{task['action']}

## Definition of Done
{task['definition_of_done']}

## Validation
{task['validation_mechanism']}

## IMPORTANT: Create a Pull Request
When complete, create a PR that:
1. Implements the required changes
2. Updates migration_plan.py to mark this task as "completed"
"""


@task
def run_parallel_session(task_dict: Dict[str, Any], prompt: str) -> Dict[str, Any]:
    """Run a single session (wrapped for parallel execution)."""
    logger = get_run_logger()
    logger.info(f"🚀 Starting: {task_dict['id']} - {task_dict['title']}")
    
    result = run_session_and_wait_for_analysis(
        prompt=prompt,
        title=f"{task_dict['id']}: {task_dict['title']}"
    )
    
    logger.info(f"✅ Completed: {result['session_url']}")
    return result


@flow(name="Simple Parallel Runner")
def run_parallel_sessions(
    target_repo: str = "../target-springboot-cics",
    max_parallel: int = 3
):
    """
    Super simple: Load plan, find ready tasks, run them in parallel.
    
    Args:
        target_repo: Path to target repository with migration_plan.py
        max_parallel: Max number of parallel sessions
    """
    logger = get_run_logger()
    
    # Step 1: Load the plan
    logger.info("📖 Loading migration plan...")
    plan = load_plan(target_repo)
    logger.info(f"   Found {len(plan.get('tasks', []))} total tasks")
    
    # Step 2: Find ready tasks
    logger.info("\n🔍 Finding ready tasks...")
    ready_tasks = find_ready_tasks(plan)
    logger.info(f"   Found {len(ready_tasks)} ready tasks")
    
    if not ready_tasks:
        logger.warning("   No tasks ready to run!")
        logger.info("   Either all done or waiting for PR merges")
        return
    
    # Step 3: Limit to max_parallel
    if len(ready_tasks) > max_parallel:
        logger.info(f"   Limiting to {max_parallel} parallel sessions")
        ready_tasks = ready_tasks[:max_parallel]
    
    # Show what we're running
    logger.info("\n📋 Tasks to run in parallel:")
    for task in ready_tasks:
        logger.info(f"   • {task['id']}: {task['title']}")
    
    # Step 4: Create prompts
    prompts = [create_task_prompt(task, target_repo) for task in ready_tasks]
    
    # Step 5: Run in parallel using Prefect
    logger.info("\n🚀 Starting parallel sessions...")
    futures = []
    for task, prompt in zip(ready_tasks, prompts):
        future = run_parallel_session.submit(task, prompt)
        futures.append(future)
    
    # Step 6: Wait for all to complete
    results = [f.result() for f in futures]
    
    # Step 7: Show results
    logger.info("\n✅ All sessions complete!")
    logger.info("\n📊 Session Links:")
    for i, result in enumerate(results):
        task = ready_tasks[i]
        logger.info(f"   {task['id']}: {result['session_url']}")
    
    logger.info("\n⏸️ NEXT STEPS:")
    logger.info("   1. Review the PRs from these sessions")
    logger.info("   2. Merge them to update task statuses")
    logger.info("   3. Run this script again for the next batch")


if __name__ == "__main__":
    # Run it!
    run_parallel_sessions()
