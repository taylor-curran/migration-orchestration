# Migration Orchestration

Simple, deterministic parallel execution of migration tasks.

## How It Works

1. **Loads** `migration_plan.py` from your target repository
2. **Finds** ready tasks (dependencies completed, status = "pending")
3. **Groups** truly independent tasks using ParallelDetector
4. **Runs** parallel Devin sessions with coordination context
5. **Stops** and waits for PR reviews

## Usage

```bash
# Setup
cd migration-orchestration
source .venv/bin/activate

# Run with defaults (max 3 parallel sessions)
python src/orchestrate_migration.py

# Run with custom settings
python src/orchestrate_migration.py --max 5 --repo ../my-target-repo
```

## The Loop

1. **Run** → Launches parallel Devin sessions
2. **Wait** → Devin creates PRs with task updates
3. **Review** → Human merges PRs (updates statuses)
4. **Repeat** → Run again for next batch

## Key Features

- **Deterministic**: Same plan always produces same parallel groups
- **Coordinated**: Each agent knows what's running alongside it
- **Safe**: Prevents resource conflicts and race conditions
- **Simple**: Just 220 lines of code, easy to understand

## Migration Plan Format

Your `migration_plan.py` needs tasks with:
- `id`: Unique identifier
- `title`: Short description  
- `status`: "pending", "in_progress", or "completed"
- `depends_on`: List of task IDs that must complete first
- `action`: What to do (1-2 sentences)
- `definition_of_done`: Success criteria
- `validation_mechanism`: How to verify

## Example Output

```
📖 Loading migration plan...
   Progress: 5/20 tasks completed

🔍 Finding ready tasks (deterministic grouping)...
   Selected 3 tasks to run in parallel
   Parallel efficiency: 66.7% faster than serial

📋 Tasks to run:
   • validator_001: Create Customer Tests (depends on: setup_001)
   • validator_002: Create Account Tests (depends on: setup_002)
   • validator_003: Create Transaction Tests (depends on: setup_003)

🚀 Starting parallel sessions...
   🚀 Starting: validator_001 - Create Customer Tests
   🚀 Starting: validator_002 - Create Account Tests
   🚀 Starting: validator_003 - Create Transaction Tests

✅ Sessions complete!

📊 Results:
   validator_001: https://app.devin.ai/sessions/xxx
   validator_002: https://app.devin.ai/sessions/yyy
   validator_003: https://app.devin.ai/sessions/zzz

⏸️ NEXT STEPS:
   1. Review PRs from these sessions
   2. Merge PRs to update statuses
   3. Run again for next batch
```
