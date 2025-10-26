# Phase 1: Exhaustive Task Discovery

## Migration Context
- **Source Repository**: `[SOURCE_REPO]` (legacy COBOL system)
- **Target Repository**: `[TARGET_REPO]` (empty Spring Boot scaffold)

## YOUR ONLY JOB THIS PHASE
Discover ALL migration tasks. Be exhaustive. List everything that needs to be done.

**DO NOT**: Add dependencies, validators, or detailed mechanisms. That comes later.

## Sandbox Assumptions (CRITICAL)
- All services must remain internal - no external APIs or databases
- Use SQLite instead of external databases  
- Skip authentication/authorization completely
- No regulatory compliance needed (SOX, PCI, etc.)
- Use local stubs/fixtures instead of live system connections
- Trust code analysis over potentially outdated docs

## Naming Convention (MANDATORY)
```
setup_XXX    - Infrastructure, baselines, monitoring
migrate_XXX  - Actual migration of business logic
integrate_XXX - Cross-component integration work
```

## Task Structure for Phase 1
```python
{
    "id": "migrate_001",  # Use proper prefix!
    "title": "Migrate Customer Read Operations",  # 20 words max
    "content": "Port INQCUST and BROWCUST programs to Spring Boot endpoints.",  # Keep it concise
    "status": "not-complete",  # ALWAYS not-complete in this phase
    "estimated_hours": 8  # 6-12 hours ideal, 20 max
}
```

## Brevity Rules
- title: 20 words maximum
- content: Keep it concise and focused
- estimated_hours: 6-12 ideal range

## What to Discover
1. **Setup Tasks** (setup_XXX)
   - Performance baseline measurements
   - Local database schema setup
   - Monitoring/observability (local only)
   - Development environment configuration

2. **Migration Tasks** (migrate_XXX)
   - Each COBOL program → Spring Boot service
   - Data access patterns → JPA repositories  
   - Transaction boundaries → @Transactional
   - Batch processes → Spring Batch jobs
   - File I/O → local file handling

3. **Integration Tasks** (integrate_XXX)
   - Service-to-service communication
   - End-to-end workflows
   - Data consistency validation

## Example Output Structure
```python
# migration_plan.py
migration_plan = {
    "tasks": [
        {
            "id": "setup_001",
            "title": "Create Performance Baselines",
            "content": "Measure current COBOL program performance. Document P50/P95/P99 latencies. Establish success metrics.",
            "status": "not-complete",
            "estimated_hours": 8
        },
        {
            "id": "setup_002", 
            "title": "Setup Local SQLite Database",
            "content": "Create SQLite schema matching COBOL data structures. Load test data fixtures. Configure Spring datasource.",
            "status": "not-complete",
            "estimated_hours": 6
        },
        {
            "id": "migrate_001",
            "title": "Migrate Customer Read Operations",
            "content": "Port INQCUST and BROWCUST to REST endpoints. Map COBOL records to DTOs. Implement repository layer.",
            "status": "not-complete", 
            "estimated_hours": 10
        }
        # ... continue for ALL tasks
    ]
}
```

## Critical Reminders
1. **Be EXHAUSTIVE** - Missing tasks is the worst failure mode
2. **Stay FOCUSED** - Just discovery, no dependencies or validators yet
3. **Keep it BRIEF** - Follow word limits strictly
4. **Use PREFIXES** - setup_, migrate_, integrate_ only
5. **Think LOCAL** - Everything runs in sandbox, no external dependencies

## What Comes Next (NOT YOUR JOB)
- Phase 2: Someone else will split/combine tasks for proper sizing
- Phase 3: Someone else will add dependencies
- Phase 4: Someone else will add validators
- Your job: Find EVERYTHING that needs doing

## Output
Save as `migration_plan.py` in the root of `[TARGET_REPO]`.
