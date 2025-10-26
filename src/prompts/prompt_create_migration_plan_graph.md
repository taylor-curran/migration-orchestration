# Migration Plan Task Graph Generation

## Migration Parameters

- **Source Repository**: `[SOURCE_REPO]` (e.g., taylor-curran/og-cics-cobol-app)
- **Target Repository**: `[TARGET_REPO]` (e.g., taylor-curran/target-springboot-cics)

## YOUR MISSION

Generate a task graph for migrating from source to target repository. Each task is a working session for an agent. Analyze both repos to understand current state and what needs migration.

## THE GOLDEN RULE: Build Validation Before Migration

**Every migration task MUST have measurable validation. If validation doesn't exist, CREATE IT FIRST.**

This means:
- **Tests come before code**: Can't migrate without tests to verify correctness
- **Metrics come before claims**: Can't claim "within 10% performance" without baseline metrics
- **Coverage comes before completion**: Can't declare done without coverage reports

The dependency chain should always look like:
```
[Setup Infrastructure] → [Create Tests] → [Migrate Code Using Tests]
                     ↗                  ↗
[Establish Baselines]                   
```

Never:
```
[Migrate Code] → [Write Tests After]  ❌ WRONG
```

## Task Node Structure

```python
{
    "id": "unique_id",  # setup_*, validator_*, migrate_*
    "title": "Short descriptive title",
    "content": "What this working session accomplishes",
    "status": "not-complete",  # Options: "not-complete", "completed" (binary only - if partially done, still "not-complete")
    "depends_on": ["task_ids"],  # Dependencies define execution order
    "action": "Brief actionable description of what to do",
    "definition_of_done": "Clear, measurable success criteria",
    "validation_mechanism": "How to concretely test, validate, sanity check, cross reference (tests, data quality metrics, observability metrics and data, coverage) - NOT just code review",
    "estimated_hours": 8,  # Target: 6-12 hours per task
    "deliverables": ["concrete_outputs.java"]  # Optional: specific files produced
}
```

## Task Brevity Rules
- Titles: 20 words maximum
- All fields should be concise and focused
- Focus on WHAT, not HOW

## Task Categories and Sequencing

### 1. Setup Tasks (First)
Infrastructure and baselines that everything depends on:
- Performance baseline measurement
- Monitoring/observability setup
- Development environment setup
- CI/CD pipeline configuration

### 2. Validator Tasks (Before Each Migration)
Create ESSENTIAL validation mechanisms BEFORE the code they will validate:
- Key unit tests for critical paths
- At least one integration test
- Basic performance benchmarks
- Initial data quality checks
- Basic acceptance test scenarios
Note: Comprehensive coverage comes in separate coverage tasks AFTER migration

### 3. Migration Tasks (After Validators)
The actual migration work, which DEPENDS ON validators:
- Code translation
- API implementation
- Data migration
- Integration work

### 4. Coverage Tasks (After Migrations)
Achieve comprehensive test coverage AFTER migrations are working:
- Expand tests to 85-95% coverage
- Add edge cases and error scenarios
- Performance test hardening
- Full integration test suites
- Production-grade validation

## Dependency Rules

1. **Migration tasks MUST depend on their validators**: If `migrate_customer` needs tests, then `validator_customer_tests` must be a dependency
2. **Validators can depend on other validators**: Build incrementally (e.g., CRUD tests extend read-only tests)
3. **Setup tasks have no dependencies**: They establish the foundation
4. **No circular dependencies**: The graph must be a DAG

## Validator-Migration Relationships

**Don't assume 1-to-1 mapping.** Use judgment:

- **One validator → Many migrations**: A comprehensive `validator_customer_tests` can validate both `migrate_customer_read` AND `migrate_customer_write`
- **One migration → Multiple validators**: Complex `migrate_transaction_processing` may need tests + performance benchmarks + data quality checks
- **Combine** validators testing the same domain; **Split** when using different techniques (tests vs metrics vs data checks)

## Task Granularity

- **Target: 6-12 hours** per task
- **Maximum: 20 hours** (split if larger)
- **Minimum: 4 hours** (combine if smaller)

Split when:
- Work exceeds 12 hours with natural breakpoints
- Different validation mechanisms are needed
- Output enables parallel downstream work

## Example Task Graph (SHOWING CORRECT SEQUENCING)

```python
{
    "tasks": [
        {
            "id": "setup_001",
            "title": "Establish Performance Baseline",
            "content": "Measure legacy system performance for all programs",
            "status": "not-complete",  # Options: "not-complete", "completed"
            "depends_on": [],
            "action": "Measure P50/P95/P99 latencies for all programs in [SOURCE_REPO].",
            "definition_of_done": "Baseline metrics documented for all programs",
            "validation_mechanism": "Metrics report covers all programs with specific numbers",
            "estimated_hours": 10,
            "deliverables": ["baseline_metrics.md", "performance_data.json"]
        },
        {
            "id": "setup_002",
            "title": "Setup Target Monitoring",
            "content": "Deploy monitoring stack for target system",
            "status": "not-complete",  # Options: "not-complete", "completed"
            "depends_on": [],
            "action": "Deploy Prometheus/Grafana monitoring stack for [TARGET_REPO].",
            "definition_of_done": "Monitoring operational and collecting metrics",
            "validation_mechanism": "Dashboards showing live data, alerts configured",
            "estimated_hours": 8,
            "deliverables": ["monitoring_config.yaml", "dashboard_urls.txt"]
        },
        {
            "id": "validator_001",
            "title": "Create Customer Read Test Suite",
            "content": "Build tests for customer inquiry operations",
            "status": "not-complete",  # Options: "not-complete", "completed"
            "depends_on": ["setup_002"],  # Needs monitoring to verify test execution
            "action": "Achieve 90%+ test coverage for INQCUST and BROWCUST inquiry operations.",
            "definition_of_done": "Full coverage of read paths including edge cases, error handling",
            "validation_mechanism": "JaCoCo shows 90%+ branch coverage, all scenarios tested",
            "estimated_hours": 10,
            "deliverables": ["CustomerReadTests.java", "test_fixtures.json", "jacoco.gradle"]
        },
        {
            "id": "validator_002", 
            "title": "Create Customer CRUD Test Suite",
            "content": "Build tests for customer create/update/delete",
            "status": "not-complete",  # Options: "not-complete", "completed"
            "depends_on": ["validator_001"],  # Extends read tests
            "action": "Test CRECUST, UPDCUST, DELCUST operations with transaction rollback scenarios.",
            "definition_of_done": "All CRUD paths tested including concurrent access, deadlock handling",
            "validation_mechanism": "95%+ coverage, transaction integrity verified",
            "estimated_hours": 10,
            "deliverables": ["CustomerCrudTests.java", "transaction_fixtures.sql"]
        },
        {
            "id": "migrate_001",
            "title": "Migrate Customer Read Operations",
            "content": "Implement customer inquiry endpoints",
            "status": "not-complete",  # Options: "not-complete", "completed"
            "depends_on": ["setup_001", "setup_002", "validator_001"],  # DEPENDS on tests!
            "action": "Migrate customer read operations to [TARGET_REPO] using validator_001 tests.",
            "definition_of_done": "All read operations migrated, tests passing",
            "validation_mechanism": "validator_001 tests pass, JaCoCo shows 90%+ coverage",
            "estimated_hours": 8,
            "deliverables": ["CustomerReadController.java", "CustomerReadService.java"]
        },
        {
            "id": "migrate_002",
            "title": "Migrate Customer CRUD Operations", 
            "content": "Implement customer create/update/delete",
            "status": "not-complete",  # Options: "not-complete", "completed"
            "depends_on": ["migrate_001", "validator_002"],  # DEPENDS on CRUD tests!
            "action": "Migrate customer CRUD operations preserving transaction boundaries.",
            "definition_of_done": "CRUD operations migrated, transaction handling correct",
            "validation_mechanism": "validator_002 tests pass, JaCoCo shows 90%+ coverage",
            "estimated_hours": 12,
            "deliverables": ["CustomerCrudController.java", "CustomerCrudService.java"]
        },
        {
            "id": "validator_003",
            "title": "Create End-to-End Test Suite",
            "content": "Build E2E tests for complete customer workflows",
            "status": "not-complete",  # Options: "not-complete", "completed"
            "depends_on": ["migrate_001", "migrate_002"],  # After migration, for E2E validation
            "action": "Test customer lifecycle: create → inquire → update → browse → delete with data consistency checks.",
            "definition_of_done": "Full customer lifecycle validated, data integrity across operations verified",
            "validation_mechanism": "All workflows complete successfully, data state consistent at each step",
            "estimated_hours": 8,
            "deliverables": ["CustomerE2ETests.java", "workflow_scenarios.md"]
        }
    ]
}
```

## Critical Principles

1. **No migration without validation**: Every `migrate_*` task must depend on a `validator_*` task
2. **Tests are prerequisites, not afterthoughts**: Validators come BEFORE migrations in the dependency graph
3. **Measurable validation only**: "Code review" is NOT validation. Tests, metrics, and coverage are.
4. **Dependencies enforce sequencing**: The graph structure ensures tests exist before code
5. **Every task independently executable**: Actions should be clear and self-contained
6. **Follow existing guides**: Use developer guides, testing guides, and documentation found in markdown files in the target repo
7. **Zero tolerance for data accuracy**: Financial/banking systems require EXACT data matching, not "close enough"

## Common Anti-Patterns to AVOID

❌ **Writing tests after migration** - Tests must exist first
❌ **Vague validation** - "Looks good" or "Review code" is not validation  
❌ **Missing baselines** - Can't measure improvement without baselines
❌ **Skipping test creation** - Every migration needs tests
❌ **False dependencies** - Don't create dependencies just to serialize work
❌ **Ignoring existing docs** - Always check target repo for guides and patterns

## Output Instructions

Create the task graph as `migration_plan.py` at the root of `[TARGET_REPO]`:

```python
# migration_plan.py
migration_plan = {
    "tasks": [
        # Array of task nodes following above structure
    ]
}
```

Analyze both repositories to determine:
1. What has already been migrated
2. What remains to be done
3. What validation mechanisms exist
4. What validation mechanisms need to be created

Generate a complete plan ensuring EVERY migration task has proper validation built FIRST.
