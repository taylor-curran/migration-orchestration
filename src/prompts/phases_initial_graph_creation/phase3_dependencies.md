# Phase 3: Dependency Mapping

## Migration Context  
- **Source Repository**: `[SOURCE_REPO]`
- **Target Repository**: `[TARGET_REPO]`

## YOUR ONLY JOB THIS PHASE
Add `depends_on` field to each task. Create a logical execution order. That's it.

**DO NOT**: Add validators, change tasks, or add validation mechanisms. Just dependencies.

## Previous Work Done
- Phase 1: Task discovery completed
- Phase 2: Task sizing adjusted  
- File exists: `migration_plan.py` with properly sized tasks

## What You Must Do
1. Load existing `migration_plan.py`
2. Add `depends_on: []` field to every task
3. Fill in logical dependencies (what must complete before this can start?)
4. Ensure no circular dependencies 
5. Run validation: `python src/utils/validate_graph.py migration_plan.py`

## Dependency Principles

### Natural Dependencies Only
Ask: "Can this task physically start without X being done first?"

```python
# GOOD: Natural dependency
{
    "id": "migrate_002",
    "title": "Migrate Customer Write Operations",
    "depends_on": ["migrate_001"],  # Need reads before writes
    ...
}

# BAD: Artificial serialization  
{
    "id": "migrate_010",
    "title": "Migrate Product Operations",
    "depends_on": ["migrate_002"],  # Products don't need customers!
    ...
}
```

### Setup Tasks Usually Have No Dependencies
```python
{
    "id": "setup_001",
    "title": "Create Performance Baselines",
    "depends_on": [],  # Can start immediately
    ...
}
```

### Parallel Work is Good
If tasks CAN run in parallel, they SHOULD. Don't add false dependencies.

```python
# These can all run in parallel:
{"id": "migrate_001", "title": "Migrate Customers", "depends_on": ["setup_001"]},
{"id": "migrate_002", "title": "Migrate Products", "depends_on": ["setup_001"]},  
{"id": "migrate_003", "title": "Migrate Orders", "depends_on": ["setup_001"]},
```

### Integration Depends on Components
```python
{
    "id": "integrate_001",
    "title": "Customer-Order Integration",
    "depends_on": ["migrate_001", "migrate_003"],  # Need both parts first
    ...
}
```

## Common Dependency Patterns

1. **Database before Services**: setup_database → migrate_services
2. **Reads before Writes**: migrate_read_ops → migrate_write_ops
3. **Components before Integration**: migrate_A, migrate_B → integrate_AB
4. **Monitoring Setup Early**: Often no dependencies, can start immediately
5. **Performance Baselines First**: Measure before claiming improvement

## Examples

```python
# BEFORE (no dependencies):
{
    "id": "migrate_001",
    "title": "Migrate Customer Read Operations",
    "content": "Port INQCUST and BROWCUST programs.",
    "status": "not-complete",
    "estimated_hours": 8
}

# AFTER (with dependencies):
{
    "id": "migrate_001", 
    "title": "Migrate Customer Read Operations",
    "content": "Port INQCUST and BROWCUST programs.",
    "status": "not-complete",
    "depends_on": ["setup_001", "setup_002"],  # Needs DB and baselines
    "estimated_hours": 8
}
```

## Important Reminders
1. **Think execution order** - What physically must happen first?
2. **Allow parallelism** - Don't serialize unnecessarily
3. **Keep existing work** - Just add depends_on field
4. **Add tasks if needed** - If you realize a prerequisite is missing, add it
5. **Validate the DAG** - Must pass validation script

## What NOT to Do
- ❌ Add validators yet (Phase 4 will do this)
- ❌ Add validation mechanisms (Phase 5 will do this)
- ❌ Create circular dependencies (A→B→C→A)
- ❌ Over-serialize tasks that could run in parallel

## Validation Check
After adding dependencies, run:
```bash
python src/utils/validate_graph.py migration_plan.py
```

The script will check for:
- Missing dependency references
- Circular dependencies  
- Other structural issues

## Output
Update `migration_plan.py` in place with depends_on fields added.
