# Migration Plan Task Graph Generation

## Migration Parameters

- **Source Repository**: `[SOURCE_REPO]` (e.g., taylor-curran/og-cics-cobol-app)
- **Target Repository**: `[TARGET_REPO]` (e.g., taylor-curran/target-springboot-cics)

You are a migration planning expert. Generate a comprehensive task graph for migrating from the source repository to the target repository. Each task represents a **working session** that an agent will execute. Analyze both repositories to understand the current state and determine what needs to be migrated.

## Core Principles

1. **Tasks are Working Sessions**: Each task is a self-contained unit of work that an agent can complete independently
2. **Dependencies Define Execution**: The dependency graph naturally determines what can run in parallel
3. **Validation is First-Class**: Some tasks create validation mechanisms, all tasks need validation criteria
4. **No Task Without Validation**: If a task lacks a concrete validation mechanism (tests, data quality metrics, coverage), create an upstream task to build one. "Review code or markdown" is NOT sufficient validation.

## Task Node Structure

Each task must have:
```python
{
    "id": "unique_identifier",  # e.g., "setup_001", "migrate_017", "validator_003"
    "title": "Short descriptive title",
    "content": "Detailed description of what this working session accomplishes",
    "depends_on": ["task_id_1", "task_id_2"],  # Empty array if no dependencies
    "prompt": "Complete prompt for the agent executing this session (include all context needed)",
    "definition_of_done": "Clear, measurable success criteria",
    "validation_mechanism": "How to verify completion (tests, metrics, manual review)",
    "estimated_hours": 8,  # Best estimate for planning
    "deliverables": ["artifact_1.md", "code_module.java"]  # Optional: concrete outputs
}
```

## Categories of Tasks (Semantic Only)

All tasks follow the same structure, but generally fall into these categories:

### Setup Tasks
- Performance baselines
- Monitoring/observability infrastructure  
- Test frameworks
- Development environments
- CI/CD pipelines

### Migration Tasks  
- Code translation/rewriting
- Data model migrations
- API implementations
- Integration work

### Validation Mechanism Creation
- Test suite creation
- Performance testing
- Data consistency verification
- End-to-end testing

## Task Granularity Guidelines

### Ideal Task Size
- **Target: 6-12 hours** of focused work (1-2 days for an agent)
- **Acceptable range: 4-20 hours** when natural boundaries exist
- **Never exceed 40 hours** - always break down larger work

### When to Split Tasks
Split into separate nodes when:
1. **Work exceeds 12 hours** and has natural breakpoints
2. **Different expertise needed** (frontend vs backend vs database)
3. **Natural validation point exists** (can verify intermediate result)
4. **Output enables parallel work** (multiple tasks can depend on this output)
5. **Different systems involved** (legacy vs new, different services)

### When to Keep Together  
Keep as single task when:
1. **Under 10 hours** and cohesive
2. **Tightly coupled changes** (must be done atomically)
3. **Shared context critical** (splitting would duplicate work)
4. **No meaningful intermediate state** (can't validate partially)

### Examples
- ❌ **Too Fine**: "Create one REST endpoint" (2 hours) - combine with related endpoints
- ✅ **Just Right**: "Migrate customer read operations - 3 endpoints" (8 hours)
- ❌ **Too Coarse**: "Migrate entire customer subsystem" (60+ hours) - split by operation type

## Dependency Guidelines

1. **Be Explicit**: If task B needs output from task A, then B depends on A
2. **Avoid False Dependencies**: Don't create dependencies just to serialize work
3. **Validation Dependencies**: Validation tasks depend on what they validate
4. **Infrastructure First**: Most tasks depend on monitoring/observability being in place
5. **Validation Mechanism Required**: If a task needs tests/metrics for validation but they don't exist, add an upstream task to create them. Example: "Create integration test suite" must come before "Migrate customer API" if those tests are the validation mechanism

## Example Task Nodes

```python
{
    "tasks": [
        {
            "id": "setup_001",
            "title": "Establish Performance Baseline - Batch 1",
            "content": "Measure and document current system performance metrics for first batch of legacy programs",
            "depends_on": [],
            "prompt": "Analyze the legacy application at [SOURCE_REPO]. Run performance tests on the first batch of critical programs. Document P50/P95/P99 latencies, throughput (TPS), and resource utilization. Create baseline report.",
            "definition_of_done": "Baseline metrics documented for first batch with specific latency numbers",
            "validation_mechanism": "Baseline report complete with all key metrics captured",
            "estimated_hours": 8,
            "deliverables": ["baseline_metrics_batch1.md", "performance_test_results.json"]
        },
        {
            "id": "setup_002",
            "title": "Establish Performance Baseline - Batch 2", 
            "content": "Measure and document performance for remaining legacy programs",
            "depends_on": [],
            "prompt": "Continue baseline analysis for remaining programs. Document P50/P95/P99 latencies, throughput, and resource usage. Create consolidated baseline report.",
            "definition_of_done": "Complete baseline metrics for all programs requiring migration",
            "validation_mechanism": "Consolidated baseline report covering entire legacy system",
            "estimated_hours": 6,
            "deliverables": ["baseline_metrics_batch2.md", "consolidated_baseline.md"]
        },
        {
            "id": "setup_003", 
            "title": "Setup Monitoring Infrastructure",
            "content": "Deploy Prometheus, Grafana, and logging stack for the target system",
            "depends_on": [],
            "prompt": "Set up monitoring for the target application at [TARGET_REPO]. Deploy Prometheus metrics collection, configure Grafana dashboards for key metrics (latency, throughput, errors), set up structured logging with correlation IDs.",
            "definition_of_done": "Monitoring stack deployed and collecting metrics from target application",
            "validation_mechanism": "Dashboards showing live metrics, test alerts firing correctly",
            "estimated_hours": 8,
            "deliverables": ["monitoring_config.yaml", "dashboard_urls.txt"]
        },
        {
            "id": "validator_001",
            "title": "Create Customer Integration Test Suite",
            "content": "Build integration test framework and initial tests for customer operations",
            "depends_on": ["setup_003"],
            "prompt": "Create comprehensive integration test suite for customer operations. Set up test data fixtures, create test harness to call both legacy and new endpoints. Include JaCoCo configuration for coverage reporting. Build at least 20 test cases covering happy paths and edge cases.",
            "definition_of_done": "Test framework operational, 20+ tests running, JaCoCo integrated",
            "validation_mechanism": "Tests execute successfully, JaCoCo generates coverage reports",
            "estimated_hours": 10,
            "deliverables": ["CustomerIntegrationTests.java", "TestFixtures.java", "jacoco.gradle"]
        },
        {
            "id": "migrate_001",
            "title": "Migrate Customer Read Operations",
            "content": "Translate customer inquiry operations to target architecture",
            "depends_on": ["setup_001", "setup_002", "setup_003", "validator_001"],  # Now depends on test suite
            "prompt": "Migrate customer inquiry operations from [SOURCE_REPO] to [TARGET_REPO]. Create REST endpoints matching legacy functionality. Maintain exact business logic. Include comprehensive error handling. Run the integration tests from validator_001 continuously during development.",
            "definition_of_done": "REST endpoints return identical data to legacy programs, all error conditions handled",
            "validation_mechanism": "Integration tests from validator_001 pass, JaCoCo shows 90%+ coverage",
            "estimated_hours": 8,
            "deliverables": ["CustomerInquiryController.java", "CustomerInquiryService.java"]
        },
        {
            "id": "validator_002",
            "title": "Create CRUD Operation Test Suite",
            "content": "Build comprehensive test suite for customer CRUD operations before migration",
            "depends_on": ["validator_001"],
            "prompt": "Extend the integration test suite from validator_001 to include comprehensive CRUD operation tests. Add 50+ test cases for create/update/delete operations including transaction boundaries, rollback scenarios, and concurrency tests. These tests will be used to validate migrate_002.",
            "definition_of_done": "CRUD test suite ready with 50+ test cases, test data fixtures prepared",
            "validation_mechanism": "Tests execute successfully against legacy system, JaCoCo configured",
            "estimated_hours": 8,
            "deliverables": ["CustomerCrudTests.java", "TransactionTestFixtures.java", "test_data.sql"]
        },
        {
            "id": "migrate_002",
            "title": "Migrate Customer Update Operations",
            "content": "Translate customer update/create/delete operations to target architecture",
            "depends_on": ["migrate_001", "validator_002"],  # Needs CRUD tests from validator_002
            "prompt": "Migrate customer CRUD operations from [SOURCE_REPO] to [TARGET_REPO]. Create REST endpoints for customer create/update/delete. Include transaction handling and proper error responses. Run the CRUD tests from validator_002 continuously during development.",
            "definition_of_done": "CRUD operations match legacy logic exactly, transaction boundaries preserved",
            "validation_mechanism": "CRUD tests from validator_002 pass, JaCoCo shows 90%+ coverage",
            "estimated_hours": 10,
            "deliverables": ["CustomerCrudController.java", "CustomerCrudService.java"]
        }
    ]
}
```

## Critical Requirements

1. **Every task must be independently executable** - Include all context in the prompt
2. **Accurate dependencies** - The graph must be logically correct
3. **Measurable validation** - No vague success criteria
4. Follow developer guides, testing guides etc. found in markdown files in the target repo.

## Output Format

Create a Python dictionary with a single "tasks" key containing an array of task nodes, then **save it as `migration_plan.py` at the root of the target repository**:

```python
# migration_plan.py
migration_plan = {
    "tasks": [
        # Array of task nodes
    ]
}
```

Save this file at the root of the target repository (e.g., `[TARGET_REPO]/migration_plan.py`).

Generate a complete migration plan with all necessary tasks to successfully migrate the legacy system. Analyze both repositories to determine what has already been migrated and what remains to be done.

