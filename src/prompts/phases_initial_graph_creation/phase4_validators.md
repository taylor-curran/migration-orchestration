# Phase 4: Validator Task Creation

## Migration Context
- **Source Repository**: `[SOURCE_REPO]`
- **Target Repository**: `[TARGET_REPO]`

## YOUR ONLY JOB THIS PHASE
Create validator TASKS (new task nodes like `validator_001`) and inject them before migrations.

**What are validator tasks?**
Validator tasks are actual task nodes that BUILD validation infrastructure - tests, benchmarks, data quality checks, etc. They're working sessions where an agent creates the tooling needed to validate migrations.

## Previous Work Done
- Phase 1: Task discovery completed
- Phase 2: Task sizing adjusted
- Phase 3: Dependencies mapped
- File exists: `migration_plan.py` with dependencies

## What You Must Do
1. Load existing `migration_plan.py`
2. For each migrate_XXX task, determine what validation it needs
3. Create new validator_XXX tasks
4. Update migrate_XXX to depend on its validator(s)
5. Update task IDs to maintain sequential numbering
6. Run validation: `python src/utils/validate_graph.py migration_plan.py`

## The Golden Rule
**NO MIGRATION WITHOUT VALIDATOR TASKS**

If you're migrating code, you need a validator task that creates **key tests and at least one integration test** FIRST.
If you're claiming performance, you need a validator task that creates **baseline benchmarks** FIRST.
If you're moving data, you need a validator task that creates **basic quality checks** FIRST.

**Note**: These validators create the ESSENTIAL tests to guide migration. Comprehensive coverage comes later.

## Validator Types and Examples

### Test Suite Validators (Key Tests + Integration)
```python
{
    "id": "validator_001",
    "title": "Create Customer Read Core Tests",
    "content": "Build key unit tests for critical paths and at least one integration test for customer inquiry operations. Focus on main success paths and critical error cases.",
    "status": "not-complete",
    "depends_on": ["setup_001"],  # Validators can have dependencies too
    "estimated_hours": 8
}
```

### Performance Benchmark Validators  
```python
{
    "id": "validator_002",
    "title": "Create Transaction Performance Benchmarks",
    "content": "Build performance test harness. Measure baseline metrics. Define success criteria.",
    "status": "not-complete",
    "depends_on": ["setup_001"],
    "estimated_hours": 6
}
```

### Data Quality Validators
```python
{
    "id": "validator_003",
    "title": "Create Data Migration Validators",
    "content": "Build data comparison tools. Create checksums. Implement reconciliation reports.",
    "status": "not-complete",
    "depends_on": ["setup_002"],
    "estimated_hours": 10
}
```

## Injection Pattern

### BEFORE (no validator):
```python
{
    "id": "migrate_001",
    "title": "Migrate Customer Read Operations",
    "depends_on": ["setup_001", "setup_002"],
    ...
}
```

### AFTER (validator injected):
```python
{
    "id": "validator_001",
    "title": "Create Customer Read Test Suite",
    "content": "Build tests for INQCUST and BROWCUST operations. Cover all paths. Mock dependencies.",
    "status": "not-complete",
    "depends_on": ["setup_001", "setup_002"],
    "estimated_hours": 8
},
{
    "id": "migrate_001",
    "title": "Migrate Customer Read Operations",
    "depends_on": ["validator_001"],  # NOW DEPENDS ON VALIDATOR!
    ...
}
```

## Validator Reuse vs Splitting

### One Validator → Multiple Migrations (when related)
```python
# One comprehensive test suite validates multiple operations
validator_001 → migrate_001 (customer reads)
              → migrate_002 (customer search)
              → migrate_003 (customer browse)
```

### Multiple Validators → One Migration (when complex)
```python
# Complex migration needs multiple validation types
validator_001 (unit tests) → 
validator_002 (perf tests) → migrate_004 (transaction processing)
validator_003 (data quality) →
```

## Some Setup Tasks May Need Validator Tasks Too!
```python
{
    "id": "validator_004",
    "title": "Create Database Schema Tests",
    "content": "Build tests to verify all tables created. Check constraints. Test connections.",
    "status": "not-complete", 
    "depends_on": ["setup_002"],  # Tests the setup task
    "estimated_hours": 4
}
```

## Important Reminders
1. **Every migration needs validator tasks** - Create tasks that BUILD the validation infrastructure
2. **Validator tasks come FIRST** - Update dependencies so validator tasks run before migrations
3. **Be specific** - "Create Customer Tests" not "Create Tests"
4. **Add missing validator tasks** - If no validator task exists for a migration, create one
5. **Renumber IDs** - Keep sequential after insertions (validator_001, validator_002, etc.)

## What NOT to Do
- ❌ Skip creating validator tasks ("this one doesn't need tests")
- ❌ Create validator tasks without connecting them via dependencies
- ❌ Define HOW to validate - just create the tasks that will build validation

## Validation Check
After injecting validator tasks, run:
```bash
python src/utils/validate_graph.py migration_plan.py
```

Ensure:
- All validator task IDs follow naming convention (validator_001, etc.)
- All migration tasks depend on at least one validator task
- No orphaned validator tasks (all connected via dependencies)

## Output
Update `migration_plan.py` with:
1. New validator task nodes added (validator_001, validator_002, etc.)
2. Migration task dependencies updated to depend on their validator tasks
