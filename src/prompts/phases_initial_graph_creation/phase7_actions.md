# Phase 7: Action Descriptions

## Migration Context
- **Source Repository**: `[SOURCE_REPO]`
- **Target Repository**: `[TARGET_REPO]`

## YOUR ONLY JOB THIS PHASE
Add `action` field to every task. Brief, actionable instructions.

**DO NOT**: Write long prompts. Keep it short and actionable.

## Previous Work Done
- Phases 1-6: Complete graph with validation mechanisms
- File exists: `migration_plan.py` with validation_mechanism defined

## What You Must Do
1. Load existing `migration_plan.py`
2. Add `action` field to every task
3. Keep it brief and actionable
4. Be directive - tell the agent WHAT to do, not HOW
5. Run validation: `python src/utils/validate_graph.py migration_plan.py`

## Action Writing Rules

### BE BRIEF
```python
# ❌ BAD (too long):
"action": "First analyze the COBOL code to understand the logic. Then create a Spring Boot controller. Map the COBOL data structures to Java DTOs. Implement the repository layer. Add error handling. Configure the endpoints."

# ✅ GOOD (concise):
"action": "Port INQCUST and BROWCUST programs to REST endpoints with DTOs."
```

### BE SPECIFIC
```python
# ❌ BAD (too vague):
"action": "Create tests."

# ✅ GOOD (specific):
"action": "Create JUnit tests for CustomerController achieving 90% branch coverage."
```

### BE ACTIONABLE
```python
# ❌ BAD (not actionable):
"action": "Customer operations should be migrated properly with good test coverage."

# ✅ GOOD (actionable):
"action": "Migrate CRECUST, UPDCUST, DELCUST to Spring services. Preserve transaction boundaries."
```

## Examples by Task Type

### Setup Tasks
```python
{
    "id": "setup_001",
    "action": "Measure P50/P95/P99 latencies for all COBOL programs under load."
}
```

### Validator Tasks
```python
{
    "id": "validator_001",  
    "action": "Write JUnit tests covering all customer read operations. Target 90% coverage."
}
```

### Migration Tasks
```python
{
    "id": "migrate_001",
    "action": "Port customer inquiry programs to Spring REST endpoints."
}
```

### Integration Tasks
```python
{
    "id": "integrate_001",
    "action": "Wire customer and order services together. Test full order lifecycle."
}
```

## Action Patterns

| Task Pattern | Action Template |
|--------------|-----------------|
| Performance baseline | "Measure [metrics] for [components]." |
| Test creation | "Write [test-type] tests for [component] achieving [coverage]%." |
| Code migration | "Port [source-programs] to [target-pattern]." |
| Integration | "Connect [service-A] with [service-B]. Verify [workflow]." |
| Database setup | "Create SQLite schema for [domain]. Load test fixtures." |
| Monitoring | "Deploy [tool] monitoring for [metrics]." |

## Common Mistakes to Avoid

### Don't Explain Why
```python
# ❌ "Create tests because we need validation before migration"
# ✅ "Create integration tests for customer CRUD operations"
```

### Don't List Steps
```python
# ❌ "First do X, then Y, finally Z"  
# ✅ "Implement X with Y approach"
```

### Don't Be Philosophical
```python
# ❌ "Ensure high quality migration with proper testing"
# ✅ "Migrate account services with transaction support"
```

## Validation Check
The validator script will ensure all required fields are present.

## Output
Update `migration_plan.py` with action field added to all tasks.
