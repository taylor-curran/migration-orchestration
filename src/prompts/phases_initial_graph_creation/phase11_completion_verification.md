# Phase 11: Repository Completion Verification

## Migration Context
- **Source Repository**: `[SOURCE_REPO]`
- **Target Repository**: `[TARGET_REPO]`

## YOUR ONLY JOB THIS PHASE
Verify ACTUAL completion status by examining both repositories. **SCRUTINIZE EVERY TASK MARKED "complete"** - if you're only 90% certain it's complete, REVERT IT to "not-complete". Update action field with remaining work for incomplete tasks.

**CRITICAL**: This is NOT about what SHOULD be done. This is about what HAS BEEN done.

**NEW SCRUTINY RULE**: Be HIGHLY SKEPTICAL of recently completed tasks. If there's ANY doubt (even 10% uncertainty), mark it as "not-complete". Better to re-verify than falsely claim completion.

## Previous Work Done
- Phases 1-10: Complete task graph with all fields
- File exists: `migration_plan.py` with initial status assignments
- Both repositories exist with migration work in various states

## What You Must Do
1. Load existing `migration_plan.py`
2. **FIRST**: Use git history to identify recently changed tasks (last 24-48 hours)
3. **SCRUTINIZE** recently completed tasks with EXTREME skepticism
4. For EVERY task, check BOTH repositories to verify actual completion
5. Update status to "complete" ONLY if 100% certain (not 90%, not 95% - 100%!)
6. **REVERT** any task to "not-complete" if you have ANY doubt
7. For incomplete tasks, update action field with specific remaining work
8. Save updated `migration_plan.py`

## Step 0: Git History Analysis (MANDATORY FIRST STEP)

### Find Recently Modified Tasks
```bash
# Check recent commits to migration_plan.py
git log -p --since="2 days ago" migration_plan.py | grep -A2 -B2 "status"

# See what tasks were recently marked complete
git diff HEAD~5 HEAD migration_plan.py | grep -A5 -B5 '"complete"'

# Check actual work done in target repo in last 48 hours
cd [TARGET_REPO]
git log --oneline --since="2 days ago"
git log --stat --since="2 days ago"

# For each recently "completed" task, check what was ACTUALLY done
git log --since="2 days ago" --grep="migrate_" --grep="validator_" --grep="setup_"
git diff HEAD~10 HEAD --name-status

# Examine specific recent changes
git show HEAD~1
git show HEAD~2
git show HEAD~3
```

### Red Flags to Watch For
- Task marked complete but no corresponding commits in target repo
- Task marked complete but recent commits show "WIP" or "partial"
- Task marked complete but CI/builds failing
- Task marked complete but related files were modified AFTER marking complete
- Task marked complete but git history shows fixes/patches afterwards

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

### Step 4: Apply Extreme Scrutiny to Recently Completed Tasks

For any task marked "complete" in the last 48 hours:
1. **DEFAULT ASSUMPTION**: It's probably NOT complete
2. Look for ANY evidence of incompleteness:
   - TODO comments in code
   - Commented out code sections
   - Missing error handling
   - Incomplete test coverage
   - Failed CI runs
   - Recent bug fixes related to this task
   - Missing documentation
   - Hardcoded values that should be configurable

**REVERSION RULE**: If you find ANY of the above, REVERT to "not-complete" immediately.

### Step 5: Update Task Status and Action

#### If 100% Complete AND You're 100% Certain
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

## Binary Status Rule - CRITICAL WITH EXTREME SCRUTINY
**THERE ARE NO PARTIAL COMPLETIONS IN STATUS FIELD**

- Status = "complete": Task is 100% done AND you're 100% CERTAIN
- Status = "not-complete": Task is 0-99% done OR you're less than 100% certain

**SCRUTINY OVERRIDE**: Even if task appears 100% done, if you're only 90% certain, mark as "not-complete"

Examples:
- 95% test coverage when 90% required BUT you're 90% sure → "not-complete" (SCRUTINY RULE)
- 95% test coverage when 90% required AND you're 100% sure → "complete"
- 89% test coverage when 90% required → "not-complete" 
- 3 of 4 tables created → "not-complete"
- All code migrated but no tests → "not-complete"
- Tests written but don't pass → "not-complete"
- Task looks complete but was marked complete 2 hours ago → "not-complete" (SCRUTINIZE!)
- Task complete but you see a recent fix commit → "not-complete" (SUSPICIOUS!)

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

## Git History Scrutiny Commands (USE THESE FIRST!)

### Check What Actually Changed
```bash
# See all files changed by a recent "completion" commit
git show --stat <commit-hash>

# Check if any TODOs or FIXMEs were added
git diff HEAD~5 HEAD | grep -i "todo\|fixme\|hack\|temporary"

# Check if tests were actually added or just marked complete
git log --since="2 days ago" -- "*Test.java" "*test.py" "*spec.js"

# See if any reverts or fixes happened after "completion"
git log --oneline --grep="fix\|revert\|patch" --since="1 day ago"

# Check commit messages for uncertainty
git log --oneline --since="2 days ago" | grep -i "maybe\|probably\|should\|might\|think"
```

### Verify Recent PR Quality
```bash
# Check if PRs were merged or just opened
git log --merges --since="2 days ago"

# See if PR had review comments requiring changes
git log --grep="review" --since="2 days ago"
```

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
- You MUST use git history commands FIRST to understand recent changes
- You MUST scrutinize EVERY recently "completed" task with extreme skepticism
- You MUST check actual files in both repos
- You MUST run actual tests/commands to verify
- You MUST NOT mark as "complete" unless 100% done AND 100% certain
- You MUST REVERT to "not-complete" if you have even 10% doubt
- You MUST update action field for incomplete tasks with specific remaining work
- Status is BINARY: "complete" or "not-complete" only
- **DEFAULT STANCE**: Tasks are incomplete until proven otherwise with 100% certainty
