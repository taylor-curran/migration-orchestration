# Phase 4: Post-Migration Validator Task Creation

## Migration Context
- **Source Repository**: `[SOURCE_REPO]`
- **Target Repository**: `[TARGET_REPO]`

## YOUR ONLY JOB THIS PHASE
Create validator TASKS (new task nodes like `validator_001`) that run AFTER migrations to validate what was migrated.

**What are validator tasks?**
Validator tasks are actual task nodes that VALIDATE the migrated code - running tests, checking performance, verifying data integrity, etc. They're working sessions where an agent validates that the migration was successful.

## Previous Work Done
- Phase 1: Task discovery completed
- Phase 2: Task sizing adjusted
- Phase 3: Dependencies mapped
- File exists: `migration_plan.py` with dependencies

## What You Must Do
1. Load existing `migration_plan.py`
2. For each migrate_XXX task, determine what validation it needs
3. Create new validator_XXX tasks that DEPEND ON the migrations
4. Validator tasks verify the migration worked correctly
5. Update task IDs to maintain sequential numbering
6. Run validation: `python src/utils/validate_graph.py migration_plan.py`

## The Golden Rule
**NO MIGRATION WITHOUT VALIDATION**

If you migrated code, you need a validator task that **runs tests and verifies correctness** AFTER.
If you're claiming performance improvement, you need a validator task that **measures and compares metrics** AFTER.
If you moved data, you need a validator task that **validates data integrity** AFTER.

**Note**: We validate AFTER migration because you can't fully test what doesn't exist yet. The migration creates it, then we validate it.

## Validator Types and Examples

### Functional Validation (Test Execution)
```python
{
    "id": "validator_001",
    "title": "Validate Customer Read Operations",
    "content": "Create and run comprehensive tests for migrated customer operations. Verify INQCUST and BROWCUST functionality matches legacy behavior. Test edge cases discovered during migration.",
    "status": "not-complete",
    "depends_on": ["migrate_001"],  # Validators run AFTER migration
    "estimated_hours": 8
}
```

### Performance Validation  
```python
{
    "id": "validator_002",
    "title": "Validate Transaction Performance",
    "content": "Run performance benchmarks on migrated transaction code. Compare against legacy baseline. Verify within 10% performance target. Generate comparison report.",
    "status": "not-complete",
    "depends_on": ["migrate_002", "setup_001"],  # Needs migration + baseline
    "estimated_hours": 6
}
```

### Data Integrity Validation
```python
{
    "id": "validator_003",
    "title": "Validate Data Migration Integrity",
    "content": "Run data validation on migrated records. Compare checksums with source. Generate reconciliation reports. Verify zero data loss.",
    "status": "not-complete",
    "depends_on": ["migrate_003"],  # Validates the data migration
    "estimated_hours": 10
}
```

## The New Pattern: Migrate Then Validate

### BEFORE (just migration):
```python
{
    "id": "migrate_001",
    "title": "Migrate Customer Read Operations",
    "depends_on": ["setup_001", "setup_002"],
    ...
}
```

### AFTER (validator added):
```python
{
    "id": "migrate_001",
    "title": "Migrate Customer Read Operations",
    "content": "Port INQCUST and BROWCUST programs to Java.",
    "status": "not-complete",
    "depends_on": ["setup_001", "setup_002"],
    "estimated_hours": 8
},
{
    "id": "validator_001",
    "title": "Validate Customer Read Migration",
    "content": "Test migrated INQCUST and BROWCUST. Verify functionality matches legacy. Add tests for issues found during migration.",
    "status": "not-complete",
    "depends_on": ["migrate_001"],  # VALIDATOR DEPENDS ON MIGRATION!
    "estimated_hours": 8
}
```

## Validation Patterns

### One Validator for Multiple Migrations (when related)
```python
# One comprehensive validation for related migrations
migrate_001 (customer reads) → 
migrate_002 (customer search) → validator_001 (validate all customer ops)
migrate_003 (customer browse) →
```

### Multiple Validators for One Migration (when complex)
```python
# Complex migration needs multiple validation types
migrate_004 (transaction processing) → validator_001 (functional tests)
                                     → validator_002 (performance tests)
                                     → validator_003 (data integrity)
```

## Integration Validation Example
```python
{
    "id": "validator_004",
    "title": "Validate Customer-Order Integration",
    "content": "Test end-to-end workflows across migrated customer and order modules. Verify transaction boundaries. Check for data consistency.",
    "status": "not-complete", 
    "depends_on": ["migrate_001", "migrate_005"],  # After both migrations
    "estimated_hours": 10
}
```

## Important Reminders
1. **Every migration needs validation** - Create validator tasks that VERIFY the migration worked
2. **Validators come AFTER** - Validators depend on migrations being complete
3. **Be specific** - "Validate Customer Read Operations" not "Run Tests"
4. **Test what was actually built** - Validators test the real migrated code, not mocks
5. **Include lessons learned** - Validators test issues discovered during migration

## What NOT to Do
- ❌ Make migrations depend on validators (migrations come FIRST)
- ❌ Try to test code that doesn't exist yet
- ❌ Skip validation because "it worked when we ran it"
- ❌ Create validators without the migration being complete

## Validation Check
After injecting validator tasks, run:
```bash
python src/utils/validate_graph.py migration_plan.py
```

Ensure:
- All validator task IDs follow naming convention (validator_001, etc.)
- All validator tasks depend on their corresponding migration tasks
- Validators run AFTER migrations, not before

## Output
Update `migration_plan.py` with:
1. New validator task nodes added (validator_001, validator_002, etc.)
2. Validator tasks properly depending on their migration tasks (not vice versa)
