# Phase 9: Final Audit and Polish

## Migration Context
- **Source Repository**: `[SOURCE_REPO]`
- **Target Repository**: `[TARGET_REPO]`

## YOUR ONLY JOB THIS PHASE
Final audit. Fix any remaining issues. Add deliverables. Make it production-ready.

**DO NOT**: Make major structural changes. This is final polish only.

## Previous Work Done
- Phases 1-8: Complete task graph with all required fields
- File exists: `migration_plan.py` fully populated

## What You Must Do
1. Load existing `migration_plan.py`
2. Run full validation: `python src/utils/validate_graph.py migration_plan.py`
3. Fix any validation errors
4. Add `deliverables` field where appropriate (optional)
5. Final deduplication check
6. Verify every migration has validation
7. Final validation must pass

## Final Audit Checklist

### Structure Validation
- [ ] All task IDs unique
- [ ] All IDs follow naming convention (setup_, validator_, migrate_, integrate_)
- [ ] Sequential numbering within each category
- [ ] All dependencies exist
- [ ] No circular dependencies
- [ ] DAG is valid

### Field Validation  
- [ ] title: ≤20 words
- [ ] All text fields are concise and focused
- [ ] All required fields present

### Logical Validation
- [ ] Every migrate_* has at least one validator_* dependency
- [ ] Every integrate_* depends on its component migrate_* tasks
- [ ] Setup tasks generally have no dependencies
- [ ] No orphaned validators (validators that nothing depends on)

### Coverage Check
- [ ] All COBOL programs accounted for
- [ ] All major workflows have integration tasks
- [ ] Performance validation exists where needed
- [ ] Data quality checks included

## Add Deliverables (Optional)
Only add where concrete files will be produced:

```python
{
    "id": "migrate_001",
    "deliverables": [
        "CustomerController.java",
        "CustomerService.java",
        "CustomerRepository.java",
        "CustomerDTO.java"
    ],
    ...
}

{
    "id": "validator_001",
    "deliverables": [
        "CustomerControllerTest.java",
        "CustomerServiceTest.java",
        "test_fixtures.json"
    ],
    ...
}
```

## Final Deduplication
One last check for sneaky duplicates:

### Look for Semantic Duplicates
- "Test customer reads" vs "Validate customer inquiries" → Merge
- "Setup database" vs "Configure data layer" → Merge
- "Integration testing" vs "E2E validation" → Merge

### Look for Overlapping Scope
- If two validators test the same component → Merge
- If two migrations handle the same program → Merge
- If two setups configure the same tool → Merge

## Critical Final Checks

### The Validator Rule
```python
# Every migration MUST have validation
for task in migration_tasks:
    assert any(validator in task.depends_on for validator in validator_tasks)
```

### The Sandbox Rule
- No external API calls
- No external databases (SQLite only)
- No authentication/authorization
- No regulatory compliance
- All services internal

### The Brevity Rule
- No novels in content fields
- No dissertations in validation_mechanism
- Keep it concise

## Missing Anything?
Last chance to add missing tasks:
- Missing test coverage?
- Missing data migration?
- Missing integration points?
- Missing monitoring setup?

Add them now with proper IDs and dependencies.

## Final Validation
Must show all green:
```bash
python src/utils/validate_graph.py migration_plan.py

✅ All task IDs are unique
✅ All tasks follow naming conventions
✅ All fields respect brevity limits
✅ All required fields present
✅ All status values are valid
✅ All dependencies reference existing tasks
✅ No circular dependencies detected
✅ All time estimates within bounds
✅ VALIDATION PASSED - Graph looks good!
```

## Output
Final, polished `migration_plan.py` ready for execution.
