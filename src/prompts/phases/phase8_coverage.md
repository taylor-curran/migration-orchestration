# Phase 8: Comprehensive Coverage Tasks

## Migration Context
- **Source Repository**: `[SOURCE_REPO]`
- **Target Repository**: `[TARGET_REPO]`

## YOUR ONLY JOB THIS PHASE
Create coverage tasks that achieve comprehensive test coverage AFTER migrations.

**What are coverage tasks?**
Coverage tasks are post-migration tasks that take the initial tests created by validator tasks and expand them to achieve comprehensive coverage, add edge cases, and ensure production readiness.

## Previous Work Done
- Phases 1-7: Complete task graph with validators, migrations, and actions defined
- File exists: `migration_plan.py` with migrations that have basic validator tests
- Migrations can be executed with essential tests, now we ensure comprehensive coverage

## What You Must Do
1. Load existing `migration_plan.py`
2. For each migrate_XXX task, check if it needs a coverage task
3. Create new coverage_XXX tasks that depend on their migrate_XXX tasks
4. Focus on achieving 85-95% test coverage and production stability
5. Update task IDs to maintain sequential numbering
6. Run validation: `python src/utils/validate_graph.py migration_plan.py`

## The Coverage Philosophy
**MIGRATIONS GET REFINED, THEN HARDENED**

1. **Validator tasks** (Phase 4) = Essential tests to guide migration
2. **Migration tasks** (existing) = Do the migration, refine tests as needed
3. **Coverage tasks** (THIS PHASE) = Achieve comprehensive coverage post-migration

## Coverage Task Types and Examples

### Comprehensive Test Coverage
```python
{
    "id": "coverage_001",
    "title": "Achieve Customer Module Full Coverage",
    "content": "Expand customer tests to 90%+ coverage. Add edge cases, error scenarios, boundary conditions, and negative tests.",
    "status": "not-complete",
    "depends_on": ["migrate_001"],  # Depends on the migration being done
    "estimated_hours": 10
}
```

### Integration Test Expansion
```python
{
    "id": "coverage_002",
    "title": "Customer Integration Test Suite",
    "content": "Create comprehensive integration tests covering all customer workflows, cross-module interactions, and end-to-end scenarios.",
    "status": "not-complete",
    "depends_on": ["migrate_001", "migrate_002"],  # After related migrations
    "estimated_hours": 12
}
```

### Performance Test Hardening
```python
{
    "id": "coverage_003",
    "title": "Customer Performance Test Suite",
    "content": "Comprehensive load tests, stress tests, and performance regression suite. Establish performance baselines and alerts.",
    "status": "not-complete",
    "depends_on": ["migrate_003"],
    "estimated_hours": 8
}
```

### Data Quality Validation
```python
{
    "id": "coverage_004",
    "title": "Customer Data Integrity Suite",
    "content": "Build comprehensive data validation including referential integrity, constraint validation, and data migration verification.",
    "status": "not-complete",
    "depends_on": ["migrate_004"],
    "estimated_hours": 8
}
```

## Coverage Patterns

### One Coverage Task → Multiple Migrations (when cohesive)
```python
# One comprehensive coverage task for related migrations
coverage_001 → covers migrate_001, migrate_002, migrate_003 (all customer operations)
```

### Separate Coverage Tasks (when distinct)
```python
# Different domains need separate coverage efforts
coverage_001 → Customer module coverage
coverage_002 → Order module coverage  
coverage_003 → Payment module coverage
```

## What Makes Good Coverage Tasks

### Focus Areas:
- **Unit Test Expansion**: From 50-60% → 85-95% coverage
- **Edge Cases**: Null handling, boundary values, concurrent access
- **Error Scenarios**: Network failures, timeout handling, rollback scenarios
- **Integration Tests**: Cross-module, end-to-end workflows
- **Performance Tests**: Load, stress, spike, soak tests
- **Security Tests**: Input validation, authorization checks
- **Data Quality**: Integrity checks, migration verification

### Sizing Guidelines:
- Small module coverage: 6-8 hours
- Medium module coverage: 8-12 hours  
- Large module coverage: 12-16 hours (consider splitting)
- Full integration suite: 10-14 hours

## Important Reminders
1. **Coverage comes AFTER migration** - These tasks depend on migrate_XXX tasks
2. **Group related work** - One coverage task can cover multiple small migrations
3. **Be specific** - "Customer Module Coverage" not "Add More Tests"
4. **Include integration** - Don't just focus on unit tests
5. **Production ready** - These tasks make the code production-grade

## What NOT to Do
- ❌ Create coverage tasks for setup or validator tasks (they don't need it)
- ❌ Duplicate work already in validator tasks
- ❌ Create coverage before migration (that's what validators are for)

## Validation Check
After adding coverage tasks, run:
```bash
python src/utils/validate_graph.py migration_plan.py
```

Ensure:
- All coverage task IDs follow naming convention (coverage_001, etc.)
- Coverage tasks depend on their corresponding migrations
- No coverage tasks for non-migration work

## Output
Update `migration_plan.py` with:
1. New coverage task nodes added (coverage_001, coverage_002, etc.)
2. Dependencies properly set (coverage tasks depend on migrations)
