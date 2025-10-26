#!/usr/bin/env python3
"""
Migration Orchestration Flow v2
Simplified implementation following SCRIPT-PLAN-DIAGRAM.md

Core Loop:
1. Load migration plan (or build initial)
2. Find ready tasks (dependencies met, status=pending)
3. Run parallel work sessions
4. Update plan with results (each session submits PR)
5. Check if complete, loop if needed
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from prefect import flow, task
from prefect.logging import get_run_logger
from tasks.run_sessions import run_session_until_blocked, generate_analysis
from utils.parallel_detector import ParallelDetector

# For now, these are hard-coded paths. Later we'll make them configurable
SOURCE_REPO = "taylor-curran/og-cics-cobol-app"
TARGET_REPO = "taylor-curran/target-springboot-cics"
MIGRATION_PLAN_PATH = Path("../target-springboot-cics/migration_plan.py")


@task(name="Load Migration Plan")
def load_migration_plan(plan_path: Path) -> Dict[str, Any]:
    """Load the migration plan from the target repository."""
    logger = get_run_logger()
    
    if not plan_path.exists():
        logger.warning(f"Migration plan not found at {plan_path}")
        return None
    
    logger.info(f"📖 Loading migration plan from: {plan_path}")
    
    # Import the Python file dynamically
    import importlib.util
    spec = importlib.util.spec_from_file_location("migration_plan", plan_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    if hasattr(module, "migration_plan"):
        plan = module.migration_plan
        tasks = plan.get("tasks", [])
        logger.info(f"✅ Loaded {len(tasks)} tasks from migration plan")
        return plan
    else:
        logger.error("Migration plan file doesn't contain 'migration_plan' variable")
        return None


@task(name="Build Initial Plan")
def build_initial_plan(source_repo: str, target_repo: str) -> Dict[str, Any]:
    """Build initial migration plan using a Devin session."""
    logger = get_run_logger()
    logger.info("🏗️ Building initial migration plan...")
    
    # Load the prompt template and substitute parameters
    prompt_path = Path(__file__).parent / "prompts" / "prompt_create_migration_plan_graph.md"
    with open(prompt_path) as f:
        prompt_template = f.read()
    
    # Replace placeholders
    prompt = prompt_template.replace("[SOURCE_REPO]", source_repo)
    prompt = prompt_template.replace("[TARGET_REPO]", target_repo)
    
    # Add instruction to save as migration_plan.py at root
    prompt += "\n\nIMPORTANT: Save the migration plan as `migration_plan.py` at the root of the target repository."
    
    # Run session to build the plan
    session_result = run_session_until_blocked(
        prompt=prompt,
        title=f"Build Migration Plan: {source_repo} → {target_repo}",
    )
    
    # Generate analysis (this will trigger sleep and get the plan)
    analysis_result = generate_analysis(session_result)
    
    logger.info(f"✅ Initial plan built. Session: {analysis_result['session_url']}")
    return analysis_result


@task(name="Find Ready Tasks")
def find_ready_tasks(plan: Dict[str, Any], max_parallel: int = 3) -> List[Dict[str, Any]]:
    """Find tasks that are ready to run (dependencies met, status=pending)."""
    logger = get_run_logger()
    
    tasks = plan.get("tasks", [])
    ready_tasks = []
    
    # Build a map of task statuses
    task_status = {t["id"]: t.get("status", "pending") for t in tasks}
    
    for task in tasks:
        if task.get("status", "pending") != "pending":
            continue  # Skip completed or in-progress tasks
            
        # Check if all dependencies are completed
        dependencies = task.get("depends_on", [])
        if all(task_status.get(dep) == "completed" for dep in dependencies):
            ready_tasks.append(task)
    
    logger.info(f"🔍 Found {len(ready_tasks)} ready tasks")
    
    # Use ParallelDetector to find which ready tasks can run in parallel
    if len(ready_tasks) > 1:
        detector = ParallelDetector(ready_tasks)
        parallel_groups = detector.detect_parallel_groups()
        
        # Take the first parallel group if available
        if parallel_groups:
            first_group = parallel_groups[0]
            parallel_task_ids = first_group.task_ids[:max_parallel]  # Limit parallelism
            ready_tasks = [t for t in ready_tasks if t["id"] in parallel_task_ids]
            logger.info(f"🔀 Selected {len(ready_tasks)} tasks that can run in parallel")
        else:
            # No parallel groups found, just take first task
            ready_tasks = ready_tasks[:1]
    else:
        # Only one ready task or none
        ready_tasks = ready_tasks[:1]
    
    for task in ready_tasks:
        logger.info(f"   • {task['id']}: {task['title']}")
    
    return ready_tasks


@task(name="Generate Task Prompt")
def generate_task_prompt(task: Dict[str, Any], plan: Dict[str, Any]) -> str:
    """Generate a detailed prompt for a specific task."""
    logger = get_run_logger()
    
    # Build context about the migration
    metadata = plan.get("metadata", {})
    source_repo = metadata.get("source_repo", SOURCE_REPO)
    target_repo = metadata.get("target_repo", TARGET_REPO)
    
    prompt = f"""
# Migration Task: {task['title']}

## Repositories
- **Source**: {source_repo}
- **Target**: {target_repo}

## Task Details
- **ID**: {task['id']}
- **Description**: {task['content']}
- **Action**: {task['action']}

## Definition of Done
{task['definition_of_done']}

## Validation Mechanism
{task['validation_mechanism']}

## Deliverables
{json.dumps(task.get('deliverables', []), indent=2)}

## Instructions
1. Complete the task as described above
2. Ensure all validation mechanisms pass
3. Create all specified deliverables
4. Update `migration_plan.py` at the root of the repository:
   - Change this task's status from "pending" to "completed"
   - Add any relevant notes or findings to the task
5. Submit a pull request with your changes

The migration plan must be updated to reflect completion of this task.
"""
    
    return prompt


@task(name="Run Work Session")
def run_work_session(task: Dict[str, Any], prompt: str) -> Dict[str, Any]:
    """Run a single work session for a task."""
    logger = get_run_logger()
    logger.info(f"🚀 Starting work session for: {task['id']} - {task['title']}")
    
    # Run the session
    session_result = run_session_until_blocked(
        prompt=prompt,
        title=f"{task['id']}: {task['title']}",
    )
    
    # Generate analysis
    analysis_result = generate_analysis(session_result)
    
    # Add task info to result
    analysis_result["task_id"] = task["id"]
    analysis_result["task_title"] = task["title"]
    
    logger.info(f"✅ Completed work session: {analysis_result['session_url']}")
    
    return analysis_result


@task(name="Update Migration Plan")
def update_migration_plan(plan: Dict[str, Any], completed_tasks: List[str], plan_path: Path) -> Dict[str, Any]:
    """Update the migration plan with completed task statuses."""
    logger = get_run_logger()
    
    # Update task statuses
    tasks = plan.get("tasks", [])
    for task in tasks:
        if task["id"] in completed_tasks:
            task["status"] = "completed"
            logger.info(f"   ✓ Marked {task['id']} as completed")
    
    # Count statistics
    total_tasks = len(tasks)
    completed = sum(1 for t in tasks if t.get("status") == "completed")
    in_progress = sum(1 for t in tasks if t.get("status") == "in_progress")
    pending = sum(1 for t in tasks if t.get("status") == "pending")
    
    logger.info(f"📊 Progress: {completed}/{total_tasks} completed, {in_progress} in progress, {pending} pending")
    
    # Save updated plan (in a real scenario, this would be part of a PR)
    # For now, we'll just log that it should be updated
    logger.warning("⚠️ Migration plan updates should be submitted via PR by Devin sessions")
    
    return plan


@flow(name="Migration Orchestration", log_prints=False)
def orchestrate_migration(
    source_repo: str = SOURCE_REPO,
    target_repo: str = TARGET_REPO,
    max_iterations: int = 10,
    max_parallel_sessions: int = 3,
) -> Dict[str, Any]:
    """
    Main orchestration flow for migration.
    
    Args:
        source_repo: Source repository to migrate from
        target_repo: Target repository to migrate to
        max_iterations: Maximum number of iteration loops
        max_parallel_sessions: Maximum parallel Devin sessions
    """
    logger = get_run_logger()
    logger.info("🎯 Starting Migration Orchestration")
    logger.info(f"   Source: {source_repo}")
    logger.info(f"   Target: {target_repo}")
    
    plan_path = Path(f"../{target_repo.split('/')[-1]}/migration_plan.py")
    
    # Step 1: Load or Build Initial Plan
    logger.info("\n" + "="*50)
    logger.info("PHASE 1: Load/Build Migration Plan")
    logger.info("="*50)
    
    plan = load_migration_plan(plan_path)
    
    if plan is None:
        logger.info("No existing plan found. Building initial plan...")
        build_result = build_initial_plan(source_repo, target_repo)
        # After building, try to load it again
        plan = load_migration_plan(plan_path)
        if plan is None:
            logger.error("Failed to build or load initial plan")
            return {"status": "failed", "reason": "Could not create initial plan"}
    
    # Main orchestration loop
    for iteration in range(max_iterations):
        logger.info("\n" + "="*50)
        logger.info(f"ITERATION {iteration + 1}/{max_iterations}")
        logger.info("="*50)
        
        # Step 2: Find Ready Tasks
        logger.info("\n📋 Finding ready tasks...")
        ready_tasks = find_ready_tasks(plan, max_parallel=max_parallel_sessions)
        
        if not ready_tasks:
            # Check if all tasks are complete
            tasks = plan.get("tasks", [])
            if all(t.get("status") == "completed" for t in tasks):
                logger.info("🎉 All tasks completed! Migration finished.")
                return {"status": "completed", "iterations": iteration + 1, "plan": plan}
            else:
                logger.info("⚠️ No ready tasks found, but not all tasks are complete.")
                logger.info("   This might indicate circular dependencies or blocked tasks.")
                return {"status": "blocked", "iterations": iteration + 1, "plan": plan}
        
        # Step 3: Run Parallel Work Sessions
        logger.info(f"\n🚀 Running {len(ready_tasks)} work sessions in parallel...")
        
        # Generate prompts for each task
        prompts = [generate_task_prompt(task, plan) for task in ready_tasks]
        
        # Submit all sessions in parallel using Prefect
        session_futures = []
        for task, prompt in zip(ready_tasks, prompts):
            future = run_work_session.submit(task, prompt)
            session_futures.append(future)
        
        # Wait for all sessions to complete
        session_results = [future.result() for future in session_futures]
        
        # Step 4: Update Plan with Results
        logger.info("\n📝 Updating migration plan with results...")
        completed_task_ids = [r["task_id"] for r in session_results]
        plan = update_migration_plan(plan, completed_task_ids, plan_path)
        
        # Log session URLs for reference
        logger.info("\n🔗 Completed Sessions:")
        for result in session_results:
            logger.info(f"   • {result['task_id']}: {result['session_url']}")
    
    # Reached max iterations
    logger.warning(f"⚠️ Reached maximum iterations ({max_iterations})")
    return {"status": "max_iterations", "iterations": max_iterations, "plan": plan}


if __name__ == "__main__":
    # Run a simple test orchestration
    result = orchestrate_migration(
        max_iterations=2,  # Just 2 iterations for testing
        max_parallel_sessions=2,  # Max 2 parallel sessions
    )
    
    print("\n" + "="*50)
    print("ORCHESTRATION COMPLETE")
    print("="*50)
    print(f"Status: {result['status']}")
    print(f"Iterations: {result.get('iterations', 0)}")
