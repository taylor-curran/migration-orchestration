# Deterministic Migration Orchestrator

A pure Python orchestrator that executes migration plans without AI - just smart graph analysis and parallel execution.

## Quick Start

```bash
# Test what would be executed (no sessions created)
python src/orchestrate_deterministic.py --dry-run

# Run for real with defaults
python src/orchestrate_deterministic.py
```

## How It Works

1. **Load Plan**: Reads `migration_plan.py` from project root
2. **Find Ready Tasks**: Identifies all "not-complete" tasks with satisfied dependencies 
3. **Detect Parallelism**: Uses `ParallelDetector` to find truly independent tasks
4. **Execute Batch**: Runs selected tasks in parallel via Devin sessions
5. **Wait & Repeat**: Waits for PR merges, then loops until complete

## Usage

### Full Orchestration (Loops Until Complete)
```bash
# Run with defaults (unlimited parallel, 30s wait between batches)
python src/orchestrate_deterministic.py

# Limit parallel sessions
python src/orchestrate_deterministic.py --max-parallel 3

# Custom settings with more wait time for PR merges
python src/orchestrate_deterministic.py --max-parallel 5 --wait 60
```

### Single Batch Mode (One Shot)
```bash
# Just run one batch and stop
python src/orchestrate_deterministic.py --single

# Single batch with more parallel sessions  
python src/orchestrate_deterministic.py --single --max-parallel 5
```

## Command Line Options

- `--max-parallel N`: Maximum parallel sessions (default: no limit)
- `--wait N`: Seconds to wait between batches for PR merges (default: 30)
- `--single`: Run single batch only, no looping
- `--dry-run`: Show what would be executed without creating sessions (test mode)

## Example Output

```
🎯 Starting Deterministic Migration Orchestrator
============================================================
📍 Iteration 1
============================================================
📖 Loading migration plan...
📊 Progress: 5/23 tasks complete (21%)

🔍 Finding ready tasks...
✅ Found 3 ready tasks

🧮 Selecting parallel batch (max 3)...
📦 Selected 2 tasks for parallel execution:
   • validator_002: Create Customer Read Test Suite
   • validator_003: Create Customer Create Test Suite

⚡ Parallel Efficiency:
   • Serial time: 18 hours
   • Parallel time: 10 hours  
   • Time saved: 8 hours (44.4% faster)

🚀 Executing 2 tasks in parallel...

📊 Batch Results:
   • validator_002: https://app.devin.ai/sessions/xxx
     PR: https://github.com/user/repo/pull/123
   • validator_003: https://app.devin.ai/sessions/yyy
     PR: https://github.com/user/repo/pull/124

⏰ Waiting 30s for PRs to be merged...
```

## Deterministic Benefits

- **Predictable**: Same plan state = same execution order
- **Efficient**: Automatically finds optimal parallel groups
- **Safe**: Never runs dependent tasks together
- **Simple**: No AI complexity, just graph algorithms
- **Fast**: No AI API calls, instant decision making

## When Tasks Get Stuck

If the orchestrator reports "No tasks ready", check:

1. **PR Merges**: Are there pending PRs that need merging?
2. **Dependencies**: Use `python src/utils/validate_graph.py` to check for circular dependencies
3. **Status Updates**: Ensure PR's update task status to "complete" in `migration_plan.py`

## Monitoring Progress

The orchestrator shows:
- Current progress (X/Y tasks complete)
- Which tasks are running
- Why tasks are blocked (waiting for dependencies)
- Parallel efficiency metrics
- Session URLs and PR links

## Integration with Prefect

This orchestrator is a Prefect flow, so you can:
- View execution in Prefect UI
- See detailed logs per task
- Track task durations
- Monitor parallel execution visually

Start Prefect server:
```bash
prefect server start
```

Then run the orchestrator and view at http://localhost:4200
