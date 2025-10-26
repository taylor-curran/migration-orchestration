#!/usr/bin/env python3
"""
Simple Parallel Runner v2 - Now with smart parallelization!
Optionally uses ParallelDetector to find optimal parallel groups.
"""

# TODO: I've barely looked at this file here..

import sys
from pathlib import Path
from typing import Dict, List, Any
from prefect import flow, task
from prefect.logging import get_run_logger

# Add parent to path
sys.path.append(str(Path(__file__).parent.parent))
from src.tasks.run_sessions import run_session_and_wait_for_analysis
from src.utils.parallel_detector import ParallelDetector


def load_plan(repo_path: str) -> Dict[str, Any]:
    """Load migration_plan.py from the target repo."""
    plan_path = Path(repo_path) / "migration_plan.py"
    
    if not plan_path.exists():
        print(f"❌ No migration plan found at: {plan_path}")
        print("   Run the initial plan builder first!")
        sys.exit(1)
    
    import importlib.util
    spec = importlib.util.spec_from_file_location("migration_plan", plan_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    return module.migration_plan


def find_ready_tasks(plan: Dict[str, Any], max_parallel: int = 3) -> List[Dict[str, Any]]:
    """
    Find tasks ready to run using ParallelDetector for deterministic grouping.
    
    Args:
        plan: Migration plan dict
        max_parallel: Max number of parallel sessions
    """
    tasks = plan.get("tasks", [])
    ready = []
    
    # Build status map
    status_map = {t["id"]: t.get("status", "not-complete") for t in tasks}
    
    # Find all ready tasks
    for task in tasks:
        if task.get("status", "not-complete") != "not-complete":
            continue
        deps = task.get("depends_on", [])
        if all(status_map.get(dep) == "complete" for dep in deps):
            ready.append(task)
    
    if not ready:
        return []
    
    # Always use ParallelDetector for deterministic grouping
    if len(ready) == 1:
        # Only one task ready, no need for detection
        return ready
    
    # Multiple tasks ready - find truly parallel groups
    detector = ParallelDetector(ready)
    parallel_groups = detector.detect_parallel_groups()
    
    if parallel_groups and len(parallel_groups) > 0:
        # Take the first group (same level, truly independent)
        first_group_ids = parallel_groups[0].task_ids[:max_parallel]
        selected = [t for t in ready if t["id"] in first_group_ids]
    else:
        # No parallel groups found (tasks have interdependencies)
        # Run just the first task to be safe
        selected = ready[:1]
    
    return selected


def create_task_prompt(task: Dict[str, Any], target_repo: str, parallel_tasks: List[Dict[str, Any]]) -> str:
    """Create a prompt for a specific task with parallel execution context."""
    
    # Build parallel context
    other_tasks = [t for t in parallel_tasks if t['id'] != task['id']]
    parallel_context = ""
    if other_tasks:
        parallel_context = "\n## ⚡ Parallel Execution Context\n"
        parallel_context += f"Running alongside {len(other_tasks)} other task(s):\n"
        for t in other_tasks:
            parallel_context += f"• {t['id']}: {t['title']}\n"
        parallel_context += "\n**Coordination Notes:**\n"
        parallel_context += "• Avoid modifying the same files as parallel tasks\n"
        parallel_context += "• Use unique test data/fixtures to prevent conflicts\n"
        parallel_context += "• Be mindful of shared resources (DB connections, API limits)\n"
    
    return f"""
# Task: {task['title']}

**Repository**: {target_repo}
**Task ID**: {task['id']}
{parallel_context}
## Your Mission
{task['action']}

## Definition of Done
{task['definition_of_done']}

## Validation
{task['validation_mechanism']}

## IMPORTANT: Create a Pull Request
When complete:
1. Implement all required changes
2. Update migration_plan.py to change this task's status from "not-complete" to "complete"
3. Submit a PR with clear description of what was done
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


@flow(name="Deterministic Parallel Runner")
def run_parallel_sessions(
    target_repo: str = "../target-springboot-cics",
    max_parallel: int = 3
):
    """
    Load plan, find ready tasks with deterministic grouping, run in parallel.
    
    Args:
        target_repo: Path to target repository
        max_parallel: Max parallel sessions
    """
    logger = get_run_logger()
    
    # Step 1: Load plan
    logger.info("📖 Loading migration plan...")
    plan = load_plan(target_repo)
    total_tasks = len(plan.get("tasks", []))
    completed = sum(1 for t in plan["tasks"] if t.get("status") == "complete")
    logger.info(f"   Progress: {completed}/{total_tasks} tasks completed")
    
    # Step 2: Find ready tasks (always uses ParallelDetector)
    logger.info(f"\n🔍 Finding ready tasks (deterministic grouping)...")
    ready_tasks = find_ready_tasks(plan, max_parallel)
    
    if not ready_tasks:
        logger.warning("   No tasks ready!")
        logger.info("   Check if waiting for PR merges or all tasks completed")
        return
    
    logger.info(f"   Selected {len(ready_tasks)} tasks to run in parallel")
    
    # Step 3: Show efficiency analysis if multiple tasks
    if len(ready_tasks) > 1:
        detector = ParallelDetector(ready_tasks)
        analysis = detector.get_execution_plan()
        logger.info(f"   Parallel efficiency: {analysis.efficiency_gain:.1f}% faster than serial")
    
    # Step 4: Show what we're running
    logger.info("\n📋 Tasks to run:")
    for task in ready_tasks:
        deps = task.get("depends_on", [])
        dep_str = f" (depends on: {', '.join(deps)})" if deps else " (no dependencies)"
        logger.info(f"   • {task['id']}: {task['title']}{dep_str}")
    
    # Step 5: Create prompts (with parallel context)
    prompts = [create_task_prompt(task, target_repo, ready_tasks) for task in ready_tasks]
    
    # Step 6: Run in parallel
    logger.info("\n🚀 Starting parallel sessions...")
    futures = []
    for task, prompt in zip(ready_tasks, prompts):
        future = run_parallel_session.submit(task, prompt)
        futures.append(future)
    
    # Step 7: Collect results
    results = [f.result() for f in futures]
    
    # Step 8: Summary
    logger.info("\n✅ Sessions complete!")
    logger.info("\n📊 Results:")
    for i, result in enumerate(results):
        task = ready_tasks[i]
        logger.info(f"   {task['id']}: {result['session_url']}")
    
    logger.info("\n⏸️ NEXT STEPS:")
    logger.info("   1. Review PRs from these sessions")
    logger.info("   2. Merge PRs to update statuses")
    logger.info("   3. Run again for next batch")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run parallel migration sessions with deterministic grouping")
    parser.add_argument("--max", type=int, default=3, 
                       help="Max parallel sessions (default: 3)")
    parser.add_argument("--repo", type=str, default="../target-springboot-cics",
                       help="Path to target repository (default: ../target-springboot-cics)")
    args = parser.parse_args()
    
    run_parallel_sessions(
        target_repo=args.repo,
        max_parallel=args.max
    )
