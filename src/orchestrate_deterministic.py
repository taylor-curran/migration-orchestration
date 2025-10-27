#!/usr/bin/env python3
"""
Deterministic Migration Orchestrator

Loops through migration plan executing tasks in optimal parallel batches.
No AI needed - just graph analysis and smart scheduling.
"""

import os
import sys
import time
import httpx
from pathlib import Path
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from prefect import flow, task
from prefect.logging import get_run_logger

# Load environment variables
load_dotenv()

# Add parent to path
sys.path.append(str(Path(__file__).parent.parent))
from src.tasks.run_sessions import run_session_and_wait_for_pr, get_enterprise_session_data
from src.utils.parallel_detector import ParallelDetector, analyze_tasks


def load_migration_plan() -> Dict[str, Any]:
    """Load migration plan from migration_plan.py in the project root."""
    plan_path = Path(__file__).parent.parent / "migration_plan.py"
    
    if not plan_path.exists():
        raise FileNotFoundError(f"No migration plan found at: {plan_path}")
    
    import importlib.util
    spec = importlib.util.spec_from_file_location("migration_plan", plan_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    return module.migration_plan


def fetch_migration_plan_from_github(
    repo_owner: str = "taylor-curran",
    repo_name: str = "target-springboot-cics", 
    branch: str = "main",
    file_path: str = "migration_plan.py"
) -> Dict[str, Any]:
    """Fetch migration_plan.py from GitHub and load it."""
    logger = get_run_logger()
    
    # Construct raw GitHub URL
    raw_url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/{branch}/{file_path}"
    
    logger.info(f"📥 Fetching migration plan from GitHub: {raw_url}")
    
    try:
        # Download the file content (no timeout - be patient)
        with httpx.Client(timeout=None) as client:
            response = client.get(raw_url)
            response.raise_for_status()
            content = response.text
        
        # Save to local temp file
        temp_path = Path(__file__).parent.parent / "migration_plan_remote.py"
        temp_path.write_text(content)
        
        # Load the plan
        import importlib.util
        spec = importlib.util.spec_from_file_location("migration_plan_remote", temp_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        logger.info("✅ Successfully fetched and loaded migration plan from GitHub")
        return module.migration_plan
        
    except httpx.HTTPError as e:
        logger.error(f"❌ Failed to fetch migration plan from GitHub: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Failed to load migration plan: {e}")
        raise


def wait_for_prs_to_merge(
    session_results: List[Dict[str, Any]], 
    poll_interval: int = 30,
    max_wait_minutes: int = 60
) -> bool:
    """Wait for all PRs from the given sessions to be merged.
    
    Returns:
        True if all PRs are merged, False if timeout
    """
    logger = get_run_logger()
    api_key = os.getenv("DEVIN_API_KEY")
    
    if not api_key:
        raise ValueError("DEVIN_API_KEY environment variable not set")
    
    # Collect all PR info from sessions
    pr_tracking = []  # List of (session_id, pr_url, is_merged)
    
    for result in session_results:
        session_id = result.get("session_id")
        if not session_id:
            continue
            
        if result.get("prs"):
            for pr in result["prs"]:
                pr_tracking.append({
                    "session_id": session_id,
                    "pr_url": pr.get("pr_url"),
                    "merged": False
                })
    
    if not pr_tracking:
        logger.info("📭 No PRs to wait for")
        return True
    
    logger.info(f"⏳ Waiting for {len(pr_tracking)} PR(s) to be merged...")
    for pr in pr_tracking:
        logger.info(f"   • {pr['pr_url']}")
    
    start_time = time.time()
    max_wait_seconds = max_wait_minutes * 60
    
    while True:
        # Check each PR status
        all_merged = True
        
        for pr_info in pr_tracking:
            if pr_info["merged"]:
                continue  # Already merged
            
            # Get latest session data
            try:
                session_data = get_enterprise_session_data(api_key, pr_info["session_id"])
                prs = session_data.get("prs", [])
                
                # Find the PR and check its state
                for pr in prs:
                    if pr.get("pr_url") == pr_info["pr_url"]:
                        state = pr.get("state", "").lower()
                        if state == "merged":
                            pr_info["merged"] = True
                            logger.info(f"   ✅ PR merged: {pr_info['pr_url']}")
                        elif state == "closed":
                            logger.warning(f"   ⚠️ PR closed without merging: {pr_info['pr_url']}")
                            pr_info["merged"] = True  # Consider it "done"
                        else:
                            all_merged = False
                        break
                        
            except Exception as e:
                logger.warning(f"   ⚠️ Failed to check PR status: {e}")
                all_merged = False
        
        if all_merged:
            logger.info("🎉 All PRs have been merged!")
            return True
        
        # Check timeout
        elapsed = time.time() - start_time
        if elapsed >= max_wait_seconds:
            logger.warning(f"⏱️ Timeout after {max_wait_minutes} minutes")
            unmerged = [pr['pr_url'] for pr in pr_tracking if not pr["merged"]]
            if unmerged:
                logger.warning(f"   Unmerged PRs: {', '.join(unmerged)}")
            return False
        
        # Show progress
        merged_count = sum(1 for pr in pr_tracking if pr["merged"])
        wait_minutes = int(elapsed / 60)
        logger.info(f"   Progress: {merged_count}/{len(pr_tracking)} merged (waiting {wait_minutes} minutes)")
        
        # Wait before next check
        time.sleep(poll_interval)


def find_ready_tasks(plan: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Find all not-complete tasks with satisfied dependencies.
    
    Returns:
        List of task dictionaries that are ready to run
    """
    tasks = plan.get("tasks", [])
    
    # Build status map for quick lookup
    status_map = {t["id"]: t.get("status", "not-complete") for t in tasks}
    
    ready = []
    for task in tasks:
        # Skip completed tasks
        if task.get("status") == "complete":
            continue
        
        # Check if all dependencies are complete
        deps = task.get("depends_on", [])
        if all(status_map.get(dep) == "complete" for dep in deps):
            ready.append(task)
    
    return ready


def select_parallel_batch(ready_tasks: List[Dict[str, Any]], max_parallel: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Use ParallelDetector to find optimal batch of tasks to run together.
    
    Args:
        ready_tasks: All tasks that are ready to run
        max_parallel: Maximum number of parallel sessions (None = no limit)
    
    Returns:
        Optimal batch of tasks to run in parallel
    """
    if not ready_tasks:
        return []
    
    if len(ready_tasks) == 1:
        return ready_tasks
    
    # Use ParallelDetector to find truly independent tasks
    detector = ParallelDetector(ready_tasks)
    parallel_groups = detector.detect_parallel_groups()
    
    if parallel_groups:
        # Take the first parallel group (all at same level, no interdependencies)
        first_group = parallel_groups[0]
        if max_parallel is None:
            # No limit - take all tasks in the group
            selected_ids = first_group.task_ids
        else:
            # Apply limit
            selected_ids = first_group.task_ids[:max_parallel]
        return [t for t in ready_tasks if t["id"] in selected_ids]
    else:
        # No parallel opportunities found - tasks have dependencies on each other
        # Just take the first task to be safe
        return ready_tasks[:1]


def create_task_prompt(task: Dict[str, Any], parallel_context: List[Dict[str, Any]]) -> str:
    """Create prompt for a task with context about parallel execution."""
    
    # Build context about other parallel tasks
    other_tasks = [t for t in parallel_context if t['id'] != task['id']]
    parallel_info = ""
    if other_tasks:
        parallel_info = f"\n## ⚡ Running in Parallel With:\n"
        for t in other_tasks:
            parallel_info += f"• {t['id']}: {t['title']}\n"
        parallel_info += "\nAvoid file conflicts with parallel tasks.\n"
    
    return f"""
# Task: {task['title']}

**Task ID**: {task['id']}
**Status**: Starting execution
{parallel_info}

## Your Mission
{task.get('action', task.get('content', 'Execute this task'))}

## Success Criteria
{task.get('definition_of_done', 'Complete the task successfully')}

## Validation
{task.get('validation_mechanism', 'Verify the task is complete')}

## Important
- Complete ALL work for this task
- Create tests if this is a validator task
- Update migration_plan.py to mark this task as "complete" when done
- Create a PR with your changes

## Repository Context
**Target Repository**: taylor-curran/target-springboot-cics
**Source Repository**: taylor-curran/og-cics-cobol-app
"""


@task(name="Execute Task")
def execute_task(task_dict: Dict[str, Any], prompt: str) -> Dict[str, Any]:
    """Execute a single task via Devin session."""
    logger = get_run_logger()
    logger.info(f"🚀 Starting: {task_dict['id']} - {task_dict['title']}")
    
    result = run_session_and_wait_for_pr(
        prompt=prompt,
        title=f"{task_dict['id']}: {task_dict['title'][:50]}",
        max_wait_for_pr=600  # Wait up to 10 minutes for PR
    )
    
    logger.info(f"✅ Completed: {task_dict['id']}")
    logger.info(f"   Session: {result['session_url']}")
    
    # Extract session ID from URL
    session_url = result.get('session_url', '')
    session_id = session_url.split('/')[-1] if '/sessions/' in session_url else None
    
    return {
        "task_id": task_dict['id'],
        "session_url": session_url,
        "session_id": session_id,
        "prs": result.get('prs', [])
    }


@task(name="Run PR Compatibility Check")
def run_pr_compatibility_check(batch_results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Run a Devin session to analyze and ensure PR compatibility from parallel tasks."""
    logger = get_run_logger()
    
    # Collect all PR URLs
    pr_list = []
    for result in batch_results:
        if result.get('prs'):
            for pr in result['prs']:
                if pr.get('pr_url'):
                    pr_list.append(f"- {pr['pr_url']}")
    # No PRs found in any results
    if not pr_list:
        logger.info("ℹ️ No PRs found in batch results, skipping compatibility check")
        return None
    
    prompt_path = Path(__file__).parent / "prompts" / "merge_conflict_resolution.md"
    prompt_template = prompt_path.read_text()
    
    # Replace placeholders
    prompt = prompt_template.replace("[TARGET_REPO]", "target-springboot-cics")
    prompt = prompt.replace("[PR_LIST]", "\n".join(pr_list))
    
    # Add repository context at the end
    prompt += "\n\n## Repository Context\n**Primary Focus - Target Repository**: taylor-curran/target-springboot-cics\nThis is where all merge conflicts should be resolved and where the migrated code lives.\n\n**Context - Source Repository**: taylor-curran/og-cics-cobol-app\nThis is the original COBOL CICS application being migrated from (for reference only)."
    
    logger.info(f"🔧 Running PR compatibility analysis for {len(pr_list)} PRs")
    
    result = run_session_and_wait_for_pr(
        prompt=prompt,
        title="Ensure PR compatibility and integration",
        max_wait_for_pr=300  # Wait up to 5 minutes for PR
    )
    
    logger.info(f"✅ PR compatibility check complete")
    logger.info(f"   Session: {result['session_url']}")
    
    # Extract session ID
    session_url = result.get('session_url', '')
    session_id = session_url.split('/')[-1] if '/sessions/' in session_url else None
    
    return {
        "task_id": "pr_compatibility_check",
        "session_url": session_url,
        "session_id": session_id,
        "prs": result.get('prs', [])
    }


@task(name="Run Phase 11 Completion Verification")
def run_phase11_verification() -> Dict[str, Any]:
    """Run phase 11 to verify completion status of all tasks."""
    logger = get_run_logger()
    
    # Load phase 11 prompt
    prompt_path = Path(__file__).parent / "prompts" / "phases_initial_graph_creation" / "phase11_completion_verification.md"
    prompt_template = prompt_path.read_text()
    
    # Replace placeholders
    prompt = prompt_template.replace("[SOURCE_REPO]", "legacy-cobol-cics")
    prompt = prompt_template.replace("[TARGET_REPO]", "target-springboot-cics")
    
    # Add repository context at the end
    prompt += "\n\n## Repository Context\n**Target Repository**: taylor-curran/target-springboot-cics\n**Source Repository**: taylor-curran/og-cics-cobol-app"
    
    logger.info("🔍 Running Phase 11: Completion Verification")
    
    result = run_session_and_wait_for_pr(
        prompt=prompt,
        title="Phase 11: Verify task completion status",
        max_wait_for_pr=300  # Wait up to 5 minutes for PR
    )
    
    logger.info(f"✅ Phase 11 complete")
    logger.info(f"   Session: {result['session_url']}")
    
    # Extract session ID  
    session_url = result.get('session_url', '')
    session_id = session_url.split('/')[-1] if '/sessions/' in session_url else None
    
    return {
        "task_id": "phase11_verification",
        "session_url": session_url,
        "session_id": session_id,
        "prs": result.get('prs', [])
    }


@flow(name="Deterministic Orchestrator")
def orchestrate_migration(
    max_parallel: Optional[int] = None,
    wait_between_batches: int = 30,
    dry_run: bool = False,
    use_remote_plan: bool = False
) -> Dict[str, Any]:
    """
    Main orchestration flow - deterministically executes migration plan.
    
    Args:
        max_parallel: Maximum parallel sessions (None = no limit)
        wait_between_batches: Seconds to wait between batches for PR merges
        dry_run: If True, only show what would be executed without running sessions
        use_remote_plan: If True, fetch plan from GitHub instead of local file
    
    Returns:
        Orchestration summary with all session results
    """
    logger = get_run_logger()
    if dry_run:
        logger.info("🎯 Starting Deterministic Migration Orchestrator (DRY RUN)")
    else:
        logger.info("🎯 Starting Deterministic Migration Orchestrator")
    
    all_results = []
    iteration = 0
    
    while True:
        iteration += 1
        logger.info(f"\n{'='*60}")
        logger.info(f"📍 Iteration {iteration}")
        logger.info(f"{'='*60}")
        
        # Step 1: Load current plan state
        logger.info("📖 Loading migration plan...")
        if use_remote_plan and iteration > 1:
            # After first iteration, fetch from GitHub to get updates from Phase 11
            plan = fetch_migration_plan_from_github()
        elif use_remote_plan:
            # First iteration, try remote first, fall back to local
            try:
                plan = fetch_migration_plan_from_github()
            except Exception as e:
                logger.warning(f"Failed to fetch remote plan: {e}, using local")
                plan = load_migration_plan()
        else:
            plan = load_migration_plan()
        tasks = plan.get("tasks", [])
        
        # Calculate progress
        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.get("status") == "complete")
        logger.info(f"📊 Progress: {completed_tasks}/{total_tasks} tasks complete ({completed_tasks*100//total_tasks}%)")
        
        # Check if we're done
        if completed_tasks == total_tasks:
            logger.info("🎉 All tasks complete! Migration finished!")
            break
        
        # Step 2: Find ready tasks
        logger.info("\n🔍 Finding ready tasks...")
        ready_tasks = find_ready_tasks(plan)
        
        if not ready_tasks:
            logger.warning("⚠️ No tasks ready to run!")
            
            # Analyze why we're blocked
            blocked_tasks = [t for t in tasks if t.get("status") != "complete"]
            logger.info(f"\n🔒 Blocked tasks ({len(blocked_tasks)} remaining):")
            
            # Group by reason
            waiting_for_deps = []
            for task in blocked_tasks:
                deps = task.get("depends_on", [])
                incomplete_deps = [d for d in deps if any(t["id"] == d and t.get("status") != "complete" for t in tasks)]
                if incomplete_deps:
                    waiting_for_deps.append((task, incomplete_deps))
            
            # Show blocked tasks
            for task, incomplete_deps in waiting_for_deps[:5]:
                logger.info(f"   • {task['id']}: Blocked by → {', '.join(incomplete_deps)}")
            if len(waiting_for_deps) > 5:
                logger.info(f"   ... and {len(waiting_for_deps)-5} more blocked tasks")
            
            logger.info("\n💡 Next steps:")
            logger.info("   1. Check if PRs from previous batch need merging")
            logger.info("   2. Verify no circular dependencies exist") 
            logger.info("   3. Run 'python src/utils/validate_graph.py' to check plan validity")
            break
        
        logger.info(f"✅ Found {len(ready_tasks)} ready tasks")
        
        # Show which tasks are ready
        if len(ready_tasks) <= 5:
            logger.info("📋 Ready tasks (all dependencies satisfied):")
            for task in ready_tasks:
                deps_info = f" (deps: {', '.join(task.get('depends_on', [])) or 'none'})"
                logger.info(f"   • {task['id']}: {task['title']}{deps_info}")
        else:
            logger.info(f"📋 Ready tasks: {', '.join([t['id'] for t in ready_tasks[:5]])} ... and {len(ready_tasks)-5} more")
        
        # Step 3: Select optimal parallel batch
        limit_msg = "no limit" if max_parallel is None else f"max {max_parallel}"
        logger.info(f"\n🧮 Selecting parallel batch ({limit_msg})...")
        batch = select_parallel_batch(ready_tasks, max_parallel)
        logger.info(f"📦 Selected {len(batch)} tasks for parallel execution:")
        
        for task in batch:
            logger.info(f"   ✓ {task['id']}: {task['title']}")
        
        # If some ready tasks weren't selected, explain why
        not_selected = [t for t in ready_tasks if t not in batch]
        if not_selected:
            logger.info(f"\n⏸️ Not selected ({len(not_selected)} tasks):")
            for task in not_selected[:3]:  # Show first 3
                logger.info(f"   • {task['id']} - would conflict with selected tasks or exceeds parallel limit")
            if len(not_selected) > 3:
                logger.info(f"   ... and {len(not_selected)-3} more")
        
        # Show efficiency if multiple tasks
        if len(batch) > 1:
            analysis = analyze_tasks(batch)
            logger.info(f"\n⚡ Parallel Efficiency:")
            logger.info(f"   • Serial time: {analysis['total_duration_serial']} hours")
            logger.info(f"   • Parallel time: {analysis['total_duration_parallel']} hours")
            logger.info(f"   • Time saved: {analysis['time_saved']} hours ({analysis['efficiency_gain']}% faster)")
        
        # Step 4: Execute batch in parallel (or dry run)
        batch_results = []
        if dry_run:
            logger.info(f"\n🏃 DRY RUN - Would execute {len(batch)} tasks in parallel:")
            logger.info("─" * 50)
            for task in batch:
                logger.info(f"   Task: {task['id']}")
                logger.info(f"   Title: {task['title']}")
                logger.info(f"   Time: {task.get('estimated_hours', 8)} hours")
                logger.info(f"   Action: {task.get('action', 'No action specified')}")
                logger.info("─" * 50)
            
            # Simulate results for dry run
            batch_results = [
                {
                    "task_id": task['id'],
                    "session_url": f"(dry-run: would create session for {task['id']})",
                    "session_id": f"dry-run-{task['id']}",
                    "prs": []
                }
                for task in batch
            ]
            all_results.extend(batch_results)
            
            # In dry run, stop after showing first batch
            logger.info("\n⏭️ DRY RUN - Would continue with merge resolution and PR waiting, but stopping here")
            break
            
        else:
            logger.info(f"\n🚀 Executing {len(batch)} tasks in parallel...")
            
            # Create prompts with parallel context
            prompts = [create_task_prompt(task, batch) for task in batch]
            
            # Submit all tasks for parallel execution
            futures = []
            for task, prompt in zip(batch, prompts):
                future = execute_task.submit(task, prompt)
                futures.append(future)
            
            # Wait for all to complete
            batch_results = [f.result() for f in futures]
            all_results.extend(batch_results)
            
            # Show results
            logger.info("\n📊 Batch Results:")
            for result in batch_results:
                logger.info(f"   • {result['task_id']}: {result['session_url']}")
                if result.get('prs'):
                    for pr in result['prs']:
                        logger.info(f"     PR: {pr.get('pr_url', 'Unknown URL')}")
            
            # Step 5: Always run PR compatibility check after parallel batch
            logger.info("\n🔍 Running PR compatibility and integration check...")
            logger.info("   Analyzing interactions between parallel PRs...")
            compatibility_result = run_pr_compatibility_check(batch_results)
            if compatibility_result:
                all_results.append(compatibility_result)
                # Add compatibility check PR to batch results for tracking
                if compatibility_result.get('prs'):
                    batch_results.append(compatibility_result)
                logger.info(f"   Compatibility session: {compatibility_result['session_url']}")
            else:
                logger.info("   No PRs to analyze in this batch")
            
            # Step 6: Wait for all PRs to be merged
            logger.info("\n⏳ Waiting for PRs to be merged by human reviewer...")
            logger.info("👍 Please review and merge the PRs when ready")
            
            prs_merged = wait_for_prs_to_merge(
                batch_results, 
                poll_interval=30,
                max_wait_minutes=60
            )
            
            if not prs_merged:
                logger.warning("⚠️ Timeout waiting for PRs. Please merge manually and restart.")
                break
            
            # Step 7: Run Phase 11 completion verification
            logger.info("\n🔍 Running Phase 11 to verify task completion...")
            phase11_result = run_phase11_verification()
            all_results.append(phase11_result)
            
            logger.info(f"   Phase 11 session: {phase11_result['session_url']}")
            if phase11_result.get('prs'):
                for pr in phase11_result['prs']:
                    logger.info(f"   Phase 11 PR: {pr.get('pr_url', 'Unknown URL')}")
            
            # Step 8: Wait for Phase 11 PR to be merged
            logger.info("\n⏳ Waiting for Phase 11 PR to be merged...")
            phase11_merged = wait_for_prs_to_merge(
                [phase11_result],
                poll_interval=30,
                max_wait_minutes=30
            )
            
            if not phase11_merged:
                logger.warning("⚠️ Timeout waiting for Phase 11 PR. Please merge manually and restart.")
                break
            
            logger.info("🔁 Phase 11 merged! Starting next iteration...\n")
            
            # Enable remote plan fetching after first iteration
            use_remote_plan = True
    
    # Final summary
    logger.info(f"\n{'='*60}")
    if dry_run:
        logger.info("📈 DRY RUN COMPLETE")
    else:
        logger.info("📈 ORCHESTRATION COMPLETE")
    logger.info(f"{'='*60}")
    
    # Reload to get final state
    plan = load_migration_plan()
    tasks = plan.get("tasks", [])
    completed_tasks = sum(1 for t in tasks if t.get("status") == "complete")
    
    logger.info(f"✅ Final Progress: {completed_tasks}/{len(tasks)} tasks complete")
    logger.info(f"🔄 Total Iterations: {iteration}")
    logger.info(f"🚀 Total Sessions Run: {len(all_results)}")
    
    if completed_tasks < len(tasks):
        remaining = [t['id'] for t in tasks if t.get("status") != "complete"]
        logger.info(f"\n⚠️ Remaining tasks: {', '.join(remaining[:5])}")
        if len(remaining) > 5:
            logger.info(f"   ... and {len(remaining)-5} more")
    
    return {
        "iterations": iteration,
        "total_sessions": len(all_results),
        "completed_tasks": completed_tasks,
        "total_tasks": len(tasks),
        "all_results": all_results
    }


@flow(name="Single Batch Execution")
def run_single_batch(max_parallel: Optional[int] = None) -> Dict[str, Any]:
    """
    Run just one batch of tasks (no looping).
    Useful for testing or manual orchestration.
    
    Args:
        max_parallel: Maximum parallel sessions (None = no limit)
    """
    logger = get_run_logger()
    logger.info("🎯 Running Single Batch")
    
    # Load plan
    plan = load_migration_plan()
    tasks = plan.get("tasks", [])
    
    # Show progress
    completed = sum(1 for t in tasks if t.get("status") == "complete")
    logger.info(f"📊 Current Progress: {completed}/{len(tasks)} tasks complete")
    
    # Find ready tasks
    ready_tasks = find_ready_tasks(plan)
    if not ready_tasks:
        logger.warning("⚠️ No tasks ready to run!")
        return {"message": "No tasks ready"}
    
    logger.info(f"✅ Found {len(ready_tasks)} ready tasks")
    
    # Select batch
    batch = select_parallel_batch(ready_tasks, max_parallel)
    logger.info(f"📦 Selected {len(batch)} tasks for execution:")
    for task in batch:
        logger.info(f"   • {task['id']}: {task['title']}")
    
    # Execute
    prompts = [create_task_prompt(task, batch) for task in batch]
    futures = []
    for task, prompt in zip(batch, prompts):
        future = execute_task.submit(task, prompt)
        futures.append(future)
    
    results = [f.result() for f in futures]
    
    # Summary
    logger.info("\n✅ Batch Complete!")
    for result in results:
        logger.info(f"   {result['task_id']}: {result['session_url']}")
    
    return {
        "batch_size": len(batch),
        "results": results
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Deterministic Migration Orchestrator")
    parser.add_argument("--max-parallel", type=int, default=None,
                       help="Max parallel sessions (default: no limit)")
    parser.add_argument("--wait", type=int, default=30,
                       help="Seconds between batches (default: 30)")
    parser.add_argument("--single", action="store_true",
                       help="Run single batch only (no looping)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be executed without running sessions")
    parser.add_argument("--remote-plan", action="store_true",
                       help="Fetch migration plan from GitHub instead of local file")
    
    args = parser.parse_args()
    
    if args.single:
        # Just run one batch
        run_single_batch(max_parallel=args.max_parallel)
    else:
        # Full orchestration loop
        orchestrate_migration(
            max_parallel=args.max_parallel,
            wait_between_batches=args.wait,
            dry_run=args.dry_run,
            use_remote_plan=args.remote_plan
        )
