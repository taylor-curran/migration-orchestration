# Phase 8: Success Criteria (Definition of Done)

## Migration Context
- **Source Repository**: `[SOURCE_REPO]`
- **Target Repository**: `[TARGET_REPO]`

## YOUR ONLY JOB THIS PHASE
Add `definition_of_done` field to every task. Clear success criteria. One sentence only.

**DO NOT**: Write paragraphs. One sentence that defines completion.

## Previous Work Done
- Phases 1-7: Complete graph with actions defined
- File exists: `migration_plan.py` with action fields

## What You Must Do
1. Load existing `migration_plan.py`
2. Add `definition_of_done` field to every task
3. Keep it to ONE sentence
4. Make it measurable/verifiable
5. Run validation: `python src/utils/validate_graph.py migration_plan.py`

## Success Criteria Rules

### Make It Binary
The criteria should be clearly met or not met. No ambiguity.

```python
# ❌ BAD (ambiguous):
"definition_of_done": "Code is mostly working with good test coverage"

# ✅ GOOD (binary):
"definition_of_done": "All 15 unit tests pass with 90% branch coverage"
```

### Make It Measurable
```python
# ❌ BAD (unmeasurable):  
"definition_of_done": "Performance is acceptable"

# ✅ GOOD (measurable):
"definition_of_done": "P95 latency under 100ms for 1000 TPS load"
```

### Make It Complete
```python
# ❌ BAD (partial):
"definition_of_done": "Some tests written"

# ✅ GOOD (complete):
"definition_of_done": "All CRUD operations tested with 85% coverage"
```

## Examples by Task Type

### Setup Tasks
```python
{
    "id": "setup_001",
    "definition_of_done": "Baseline metrics documented for all 10 programs with P50/P95/P99 values"
}
```

### Validator Tasks  
```python
{
    "id": "validator_001",
    "definition_of_done": "Test suite with 25+ tests achieving 90% coverage on customer module"
}
```

### Migration Tasks
```python
{
    "id": "migrate_001",
    "definition_of_done": "Customer read endpoints returning correct data for all test fixtures"
}
```

### Integration Tasks
```python
{
    "id": "integrate_001",
    "definition_of_done": "Order lifecycle completes successfully with proper customer linkage"
}
```

## Success Pattern Templates

| Task Type | Definition of Done Template |
|-----------|----------------------------|
| Baseline measurement | "[N] programs measured with [metrics] documented" |
| Test creation | "[N]+ tests written achieving [X]% coverage" |
| Code migration | "[Component] migrated with all tests passing" |
| Integration | "[Workflow] executes end-to-end without errors" |
| Schema setup | "Database schema created with [N] tables and test data loaded" |
| Monitoring | "[Tool] dashboard live displaying [N] metrics" |

## Common Pitfalls

### Avoid Vague Terms
- ❌ "properly", "correctly", "well", "good"
- ✅ "90% coverage", "15 tests pass", "under 100ms"

### Avoid Multiple Criteria
```python
# ❌ BAD (multiple):
"definition_of_done": "Tests pass and coverage is good and performance is fine"

# ✅ GOOD (single, comprehensive):
"definition_of_done": "All tests pass with 85% coverage meeting performance SLA"
```

### Avoid Process Descriptions
```python
# ❌ BAD (describes process):
"definition_of_done": "Code has been reviewed and deployed to test environment"

# ✅ GOOD (describes outcome):
"definition_of_done": "Service handles 500 TPS with zero errors in test environment"
```

## Quick Reference

**Ask yourself**: "How would I know this task is 100% complete?"
- Count something: "20 tests", "5 endpoints", "3 tables"
- Measure something: "90% coverage", "100ms latency", "zero errors"
- Verify something: "all tests pass", "data matches", "workflow completes"

## Add Missing Work
If while writing success criteria you realize something is missing, add it:
- Missing test? Add a validator task
- Missing integration? Add an integrate task
- Missing setup? Add a setup task

## Output
Update `migration_plan.py` with definition_of_done field added to all tasks.
