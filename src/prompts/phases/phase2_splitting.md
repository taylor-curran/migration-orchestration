# Phase 2: Task Splitting and Refinement

## Migration Context
- **Source Repository**: `[SOURCE_REPO]`
- **Target Repository**: `[TARGET_REPO]`

## YOUR ONLY JOB THIS PHASE  
Adjust task granularity. Split tasks >12 hours. Combine tasks <4 hours. That's it.

**DO NOT**: Add dependencies, validators, or change the core work. Just resize tasks.

## Previous Work Done
- Phase 1: Exhaustive task discovery completed
- File exists: `migration_plan.py` with all tasks identified

## What You Must Do
1. Load existing `migration_plan.py`
2. For each task >12 hours: Split into 2-3 smaller tasks
3. For tasks <4 hours: Consider combining with related tasks
4. Keep all task IDs consistent with naming convention
5. Run validation: `python src/utils/validate_graph.py migration_plan.py`

## Splitting Rules
When splitting a large task:
```python
# BEFORE (too large):
{
    "id": "migrate_001",
    "title": "Migrate All Customer Operations",  
    "content": "Port all customer CRUD operations. Handle transactions. Add caching.",
    "status": "not-complete",
    "estimated_hours": 25  # TOO BIG!
}

# AFTER (properly split):
{
    "id": "migrate_001",
    "title": "Migrate Customer Read Operations",
    "content": "Port INQCUST and BROWCUST programs. Map to REST endpoints. Create DTOs.",
    "status": "not-complete",
    "estimated_hours": 8
},
{
    "id": "migrate_002", 
    "title": "Migrate Customer Write Operations",
    "content": "Port CRECUST, UPDCUST, DELCUST programs. Handle transactions. Add validation.",
    "status": "not-complete",
    "estimated_hours": 10
},
{
    "id": "migrate_003",
    "title": "Add Customer Caching Layer",
    "content": "Implement Redis caching for customer data. Add cache invalidation. Configure TTL.",
    "status": "not-complete",
    "estimated_hours": 7
}
```

## Combining Rules
When combining small tasks:
```python
# BEFORE (too granular):
{
    "id": "setup_001",
    "title": "Create Database Schema",
    "estimated_hours": 2  # TOO SMALL
},
{
    "id": "setup_002", 
    "title": "Load Test Data",
    "estimated_hours": 2  # TOO SMALL
}

# AFTER (combined):
{
    "id": "setup_001",
    "title": "Setup Database and Test Data",
    "content": "Create SQLite schema. Load test fixtures. Verify data integrity.",
    "estimated_hours": 4
}
```

## Important Reminders
1. **Preserve all work** - Don't lose any tasks during split/combine
2. **Maintain naming** - Keep setup_, migrate_, integrate_ prefixes
3. **Update IDs** - Renumber sequentially after splits
4. **Keep brevity** - Still follow 10 word titles, 3 sentence content
5. **Add tasks if needed** - If you realize something is missing while splitting, add it

## What NOT to Do
- ❌ Add dependencies (Phase 3 will do this)
- ❌ Add validators (Phase 4 will do this)  
- ❌ Add validation mechanisms (Phase 5 will do this)
- ❌ Change the fundamental work being done

## Validation Check
After making changes, run:
```bash
python src/utils/validate_graph.py migration_plan.py
```

Fix any errors before considering this phase complete.

## Output
Update `migration_plan.py` in place with properly sized tasks.
