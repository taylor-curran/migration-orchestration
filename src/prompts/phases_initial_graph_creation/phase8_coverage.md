# Phase 8: Comprehensive Test Coverage Tasks

## Migration Context
- **Source Repository**: `[SOURCE_REPO]`
- **Target Repository**: `[TARGET_REPO]`

## YOUR ONLY JOB THIS PHASE
Create coverage tasks that build comprehensive test suites AFTER validation proves the migration works.

**What are coverage tasks?**
Coverage tasks are post-validation tasks that create exhaustive test suites. Once we know the migration works (via validators), we build comprehensive tests for long-term maintenance and CI/CD.

## Previous Work Done
- Phases 1-7: Complete task graph with migrations and validators
- File exists: `migration_plan.py` with migrations validated by validator tasks
- Validators have proven migrations work, now we build comprehensive test suites

## What You Must Do
1. Load existing `migration_plan.py`
2. For each migrate_XXX task, check if it needs comprehensive test coverage
3. Create new coverage_XXX tasks that depend on BOTH migrate_XXX AND validator_XXX
4. Focus on achieving 85-95% test coverage for long-term maintainability
5. Update task IDs to maintain sequential numbering
6. Run validation: `python src/utils/validate_graph.py migration_plan.py`

## The Coverage Philosophy
**MIGRATE → VALIDATE → COMPREHENSIVE TESTING**

1. **Migration tasks** = Port the code to the new system
2. **Validator tasks** = Verify the migration works correctly
3. **Coverage tasks** (THIS PHASE) = Build comprehensive test suites for the future

## Coverage Task Types and Examples

### Comprehensive Test Coverage
```python
{
    "id": "coverage_001",
    "title": "Achieve Customer Module Full Coverage",
    "content": "Expand customer tests to 90%+ coverage. Add edge cases, error scenarios, boundary conditions, and negative tests.",
    "status": "not-complete",
    "depends_on": ["migrate_001", "validator_001"],  # After migration AND validation
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
    "depends_on": ["migrate_001", "migrate_002", "validator_001"],  # After migrations and validation
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
    "depends_on": ["migrate_003", "validator_002"],  # After migration and validation
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
    "depends_on": ["migrate_004", "validator_003"],  # After migration and validation
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
1. **Coverage comes LAST** - After migration AND validation
2. **Build for the future** - These tests will run in CI/CD forever
3. **Be comprehensive** - Edge cases, error handling, performance tests
4. **Don't duplicate validator work** - Validators proved it works, coverage makes it bulletproof
5. **Production ready** - These tasks create the full test harness

## What NOT to Do
- ❌ Create coverage before validation completes
- ❌ Duplicate validation work (validators already proved it works)
- ❌ Skip coverage because "validators already tested it" (different purposes)

## Validation Check
After adding coverage tasks, run:
```bash
python src/utils/validate_graph.py migration_plan.py
```

Ensure:
- All coverage task IDs follow naming convention (coverage_001, etc.)
- Coverage tasks depend on BOTH migrations AND validators
- Coverage focuses on comprehensive testing, not basic validation

## Output
Update `migration_plan.py` with:
1. New coverage task nodes added (coverage_001, coverage_002, etc.)
2. Dependencies properly set (coverage tasks depend on migrations)
