# Deterministic Orchestrator with Full PR Cycle

## Overview
The orchestrator now implements a complete cycle that includes:
1. Task execution
2. Merge conflict resolution
3. PR merge waiting
4. Completion verification
5. Plan refresh from GitHub
6. Automatic cycle restart

## The Full Cycle

### Phase 1: Task Execution 🚀
- Loads migration plan (local first time, GitHub after)
- Finds ready tasks (dependencies satisfied)
- Selects optimal parallel batch
- Executes tasks in parallel via Devin sessions
- Each task creates a PR

### Phase 2: Merge Conflict Resolution 🔧
- Automatically runs after batch completes
- Session fixes any merge conflicts
- Ensures all PRs are green and mergeable
- Creates its own PR if fixes were needed

### Phase 3: Human Review & Merge 👍
- Polls Devin API every 30 seconds
- Waits for ALL PRs to be merged (including conflict fix PR)
- Shows progress updates
- Timeout after 60 minutes (configurable)

### Phase 4: Completion Verification 🔍
- Runs Phase 11 prompt
- Verifies actual completion status in both repos
- Updates migration_plan.py with:
  - Tasks marked "complete" if 100% done
  - Updated action fields for incomplete tasks
- Creates PR with updated plan

### Phase 5: Phase 11 Merge ✅
- Waits for Phase 11 PR to be merged
- This updates migration_plan.py on GitHub

### Phase 6: Restart Cycle 🔁
- Fetches updated migration_plan.py from GitHub
- Starts next iteration with fresh state
- Continues until all tasks complete

## Usage

### Dry Run (Test Mode)
```bash
python src/orchestrate_deterministic.py --dry-run
```

### Full Execution
```bash
python src/orchestrate_deterministic.py --remote-plan
```

### With Limits
```bash
python src/orchestrate_deterministic.py --max-parallel 3 --wait 45 --remote-plan
```

### Test Script
```bash
# Dry run test
python test_orchestrator_cycle.py

# Full cycle test
python test_orchestrator_cycle.py --full
```

## Command Line Options

- `--max-parallel N`: Limit parallel sessions (default: no limit)
- `--wait N`: Seconds to poll for PR merges (default: 30)
- `--dry-run`: Show what would execute without running
- `--remote-plan`: Fetch plan from GitHub (auto-enabled after first cycle)
- `--single`: Run just one batch (no looping)

## Key Features

### Smart Batching
- Uses ParallelDetector to find truly independent tasks
- Avoids file conflicts between parallel tasks
- Shows efficiency metrics (time saved)

### PR Tracking
- Tracks which session created which PR
- Monitors PR states (open/merged/closed)
- Handles both task PRs and fix PRs

### GitHub Integration
- Fetches migration_plan.py from:
  `https://github.com/taylor-curran/target-springboot-cics/blob/main/migration_plan.py`
- Automatically switches to remote after first iteration
- Ensures plan stays in sync

### Robust Error Handling
- Timeouts for PR waiting
- Fallback to local plan if GitHub fetch fails
- Clear error messages and next steps

## Flow Diagram

```
Start
  ↓
Load Plan (local/GitHub)
  ↓
Find Ready Tasks
  ↓
Execute Batch in Parallel → Creates PRs
  ↓
Run Merge Conflict Fix → Creates Fix PR (if needed)
  ↓
Wait for Human to Merge ALL PRs ← Poll every 30s
  ↓
Run Phase 11 Verification → Creates PR
  ↓
Wait for Phase 11 PR Merge ← Poll every 30s
  ↓
Fetch Updated Plan from GitHub
  ↓
All Tasks Complete? → No → Loop back to "Find Ready Tasks"
  ↓ Yes
End
```

## Important Notes

1. **Manual PR Merging**: The human must review and merge PRs. The orchestrator waits.

2. **GitHub Plan Source**: After first iteration, always fetches from GitHub to get Phase 11 updates.

3. **Merge Conflicts**: Automatically handled by dedicated session before human review.

4. **Binary Status**: Tasks are either "not-complete" or "complete" - no partial states.

5. **Timeout Handling**: If PRs aren't merged within timeout, orchestrator stops gracefully.

## Monitoring Progress

The orchestrator provides detailed logging:
- Current iteration number
- Progress percentage (X/Y tasks complete)
- Ready tasks found
- Batch selection reasoning
- Parallel efficiency metrics
- PR creation and merge status
- Phase 11 verification results

## Troubleshooting

### PRs Not Detected as Merged
- Check Devin API is returning correct PR states
- Verify PR URLs match between creation and polling
- Look for "closed" vs "merged" state

### GitHub Fetch Fails
- Check network connectivity
- Verify repository is public or you have access
- Confirm migration_plan.py exists on main branch

### No Tasks Ready
- Check for circular dependencies
- Verify PRs from previous batch were merged
- Run validation: `python src/utils/validate_graph.py`
