# Phase 11: Repository Completion Verification

## Migration Context
- **Source Repository**: `[SOURCE_REPO]`
- **Target Repository**: `[TARGET_REPO]`

## YOUR ONLY JOB THIS PHASE
Verify ACTUAL completion status by examining both repositories. Update status to "complete" ONLY if 100% done. Update action field with remaining work for incomplete tasks.

**CRITICAL**: This is NOT about what SHOULD be done. This is about what HAS BEEN done.

## Previous Work Done
- Phases 1-10: Complete task graph with all fields
- File exists: `migration_plan.py` with initial status assignments
- Both repositories exist with migration work in various states

## What You Must Do
1. Load existing `migration_plan.py`
2. For EVERY task, check BOTH repositories to verify actual completion
3. Update status to "complete" ONLY if 100% complete
4. For incomplete tasks, update action field with specific remaining work
5. Save updated `migration_plan.py`

## Verification Process for Each Task

### Step 1: Check Source Repository
For each task, verify what was supposed to be extracted/analyzed from source:
- Does the code/data exist in `[SOURCE_REPO]`?
- Has it been properly analyzed?
- Are all dependencies identified?
- Are all business rules documented?

### Step 2: Check Target Repository  
For each task, verify what was supposed to be created in target:
- Does the migrated code exist in `[TARGET_REPO]`?
- Are all files present that should be?
- Does the code compile/run?
- Are tests present and passing?

### Step 3: Verify Validation Mechanism
Check the specific validation_mechanism for the task:
- If it says "tests pass with 90% coverage" → Run coverage tool
- If it says "performance within 10% of baseline" → Check metrics
- If it says "all 4 tables created" → Query the database
- If it says "endpoint returns data" → Make the API call

### Step 4: Update Task Status and Action

#### If 100% Complete
```python
{
    "id": "migrate_001",
    "status": "complete",  # Changed from "not-complete"
    "action": "Port INQCUST to REST endpoint with composite key support.",  # Keep original
    ...
}
```

#### If Partially Complete (e.g., 80% done)
```python
{
    "id": "migrate_001", 
    "status": "not-complete",  # STAYS as "not-complete"
    "action": "Complete error handling for missing customers and add integration tests.",  # UPDATED with what remains
    ...
}
```

#### If Not Started
```python
{
    "id": "migrate_001",
    "status": "not-complete",  # STAYS as "not-complete"
    "action": "Port INQCUST to REST endpoint with composite key support.",  # Keep original
    ...
}
```

## Specific Checks by Task Type

### Setup Tasks (setup_*)
- Check if infrastructure/configuration exists
- Verify databases, schemas, test data loaded
- Confirm monitoring/logging configured
- Test connections and health checks

### Validator Tasks (validator_*)
- Check if test files exist in `[TARGET_REPO]`
- Run test suites and check coverage
- Verify all test cases pass
- Confirm coverage meets stated thresholds

### Migration Tasks (migrate_*)
- Check if source code analyzed in `[SOURCE_REPO]`
- Verify migrated code exists in `[TARGET_REPO]`
- Confirm code compiles without errors
- Run associated validator tests
- Check if APIs/endpoints are accessible
- Verify data transformations complete

### Integration Tasks (integrate_*)
- Check if components properly connected
- Verify end-to-end flows work
- Confirm data flows between systems
- Test transaction boundaries

### Coverage Tasks (coverage_*)
- Run full test suites with coverage tools
- Check if coverage meets 85-95% target
- Verify edge cases and error scenarios covered
- Confirm performance tests present

## Binary Status Rule - CRITICAL
**THERE ARE NO PARTIAL COMPLETIONS IN STATUS FIELD**

- Status = "complete": Task is 100% done, all success criteria met
- Status = "not-complete": Task is 0-99% done, regardless of progress

Examples:
- 95% test coverage when 90% required → "complete"
- 89% test coverage when 90% required → "not-complete" 
- 3 of 4 tables created → "not-complete"
- All code migrated but no tests → "not-complete"
- Tests written but don't pass → "not-complete"

## Action Field Updates for Incomplete Tasks

Be SPECIFIC about what remains. Good examples:

### Before (generic action)
```python
"action": "Create customer service tests."
```

### After (specific remaining work)
```python
"action": "Add error handling tests for null customer IDs and fix failing cascade delete test."
```

### More Examples of Updated Actions
- "Complete PROCTRAN audit logging and add rollback scenario tests."
- "Fix compilation errors in CustomerController and implement missing DTO mappings."
- "Add remaining 3 tables (Account, Transaction, PROCTRAN) to schema."
- "Implement async credit check mock and increase branch coverage from 72% to 90%."
- "Configure Spring datasource connection and load test fixtures."
- "Port remaining 5 transaction types and add integration tests."

## Common Completion Verification Patterns

### For Test Tasks
```bash
# Check if test files exist
find [TARGET_REPO] -name "*Test.java" -o -name "*test.py"

# Run tests with coverage
mvn test jacoco:report
# or
pytest --cov=src --cov-report=html

# Check coverage percentage
grep -A 3 "Total" target/site/jacoco/index.html
```

### For Migration Tasks
```bash
# Check if migrated files exist
ls -la [TARGET_REPO]/src/main/java/com/example/controller/
ls -la [TARGET_REPO]/src/main/java/com/example/service/

# Try to compile
mvn compile

# Check if endpoints work
curl http://localhost:8080/api/customers/12345
```

### For Database Tasks
```bash
# Check schema
sqlite3 migration.db ".schema"

# Check data
sqlite3 migration.db "SELECT COUNT(*) FROM Customer;"
```

## Final Validation
After updating all tasks, run validation:
```bash
python src/utils/validate_graph.py migration_plan.py
```

## Output Requirements
1. Updated `migration_plan.py` with:
   - Accurate "complete"/"not-complete" status for EVERY task
   - Updated action fields for incomplete tasks showing specific remaining work
   - No changes to other fields unless fixing validation errors

2. Summary report showing:
   - Total tasks: X
   - Completed: Y
   - Not complete: Z
   - Completion percentage: Y/X * 100%

## Remember
- You MUST check actual files in both repos
- You MUST run actual tests/commands to verify
- You MUST NOT mark as "complete" unless 100% done
- You MUST update action field for incomplete tasks with specific remaining work
- Status is BINARY: "complete" or "not-complete" only
