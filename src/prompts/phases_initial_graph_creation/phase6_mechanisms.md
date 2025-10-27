# Phase 6: Validation Mechanisms

## Migration Context
- **Source Repository**: `[SOURCE_REPO]`
- **Target Repository**: `[TARGET_REPO]`

## YOUR ONLY JOB THIS PHASE
Add `validation_mechanism` field to EVERY task. Specify HOW to validate. Be concrete.

**DO NOT**: Change tasks, dependencies, or structure. Just add validation mechanisms.

## Previous Work Done
- Phases 1-5: Complete task graph with validators cleaned
- File exists: `migration_plan.py` with clean structure
- Validators depend on migrations (validate AFTER), now define HOW they validate

## What You Must Do
1. Load existing `migration_plan.py`
2. Add `validation_mechanism` field to EVERY task (including validators themselves!)
3. Be specific - mention tools, metrics, coverage targets
4. Keep it concise but comprehensive
5. Run validation: `python src/utils/validate_graph.py migration_plan.py`

## Validation Mechanism Types

### For Migration Tasks
```python
{
    "id": "migrate_001",
    "title": "Migrate Customer Read Operations",
    "validation_mechanism": "Validator_001 will verify functionality. Basic smoke tests during development. Full validation happens in validator_001 task.",
    ...
}
```

### For Validator Tasks (they do the validation!)
```python
{
    "id": "validator_001",
    "title": "Validate Customer Read Migration",
    "validation_mechanism": "All tests pass with 90%+ branch coverage via JaCoCo. Response times within 10% of baseline. No functional regressions. Test report generated.",
    ...
}
```

### For Setup Tasks
```python
{
    "id": "setup_001",
    "title": "Create Performance Baselines",
    "validation_mechanism": "Metrics dashboard shows P50/P95/P99 for all 10+ programs. Each program measured under load with 100+ samples. Results exported to performance_baseline.json.",
    ...
}
```

### For Integration Tasks
```python
{
    "id": "integrate_001",
    "title": "Customer-Order Integration",
    "validation_mechanism": "Validator_004 will run E2E tests. Basic connectivity verified during integration. Full validation in validator_004.",
    ...
}
```

## Concrete Validation Examples

### Testing Validation
- "Unit tests achieve 85% line coverage via JaCoCo"
- "Integration tests cover all 15 API endpoints"
- "Load tests handle 1000 TPS without errors"

### Data Quality Validation
- "Row counts match source within 0.01%"
- "Checksums identical for all migrated records"  
- "No null values in required fields per data_quality.sql"

### Performance Validation  
- "P95 latency within 10% of baseline metrics"
- "Memory usage stable under 2GB during load test"
- "No memory leaks detected by profiler"

### Observability Validation
- "Grafana dashboard displays all 10 key metrics"
- "Alerts trigger within 30 seconds of threshold breach"
- "Logs contain correlation IDs for all transactions"

## What Makes a Good Validation Mechanism

### ❌ BAD (too vague):
- "Code review"
- "Manual testing"  
- "Looks correct"
- "Performance is good"

### ✅ GOOD (specific and measurable):
- "JUnit tests pass with 90% branch coverage per JaCoCo report"
- "Load test sustains 500 TPS for 10 minutes without errors"
- "Data reconciliation shows zero discrepancies across 1M records"
- "Prometheus metrics match baseline within 5% tolerance"

## Important Reminders
1. **Every task needs a mechanism** - Including validators and setup tasks
2. **Be specific** - Name tools, targets, and thresholds
3. **Stay brief** - Keep it concise and focused
4. **Make it measurable** - Numbers, percentages, concrete outputs
5. **Add tasks if needed** - If you realize validation is missing, add it

## Validation Patterns by Task Type

| Task Type | Common Validation Mechanisms |
|-----------|------------------------------|
| setup_* | Config files exist, services running, dashboards live |
| validator_* | Tests pass, coverage achieved, regressions caught, reports generated |  
| migrate_* | Code compiles, basic smoke tests pass, validator_X will verify |
| integrate_* | Services connect, basic flow works, validator_X will verify fully |

## Output
Update `migration_plan.py` with validation_mechanism field added to all tasks.
