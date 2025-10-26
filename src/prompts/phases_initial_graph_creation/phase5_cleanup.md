# Phase 5: Cleanup and Deduplication

## Migration Context
- **Source Repository**: `[SOURCE_REPO]`
- **Target Repository**: `[TARGET_REPO]`

## YOUR ONLY JOB THIS PHASE
Clean up the task graph. Remove duplicates, fix orphans, renumber IDs. Make it pristine.

**DO NOT**: Add new features or change the fundamental plan. Just clean.

## Previous Work Done  
- Phases 1-4: Discovery, splitting, dependencies, validators added
- File exists: `migration_plan.py` with validators injected
- Likely issues: duplicates, inconsistent numbering, orphaned dependencies

## What You Must Do
1. Load existing `migration_plan.py`
2. Remove exact duplicate tasks
3. Merge near-duplicates intelligently
4. Fix any orphaned dependencies
5. Renumber all IDs sequentially by category
6. Ensure all fields follow brevity rules
7. Run validation: `python src/utils/validate_graph.py migration_plan.py`

## Deduplication Rules

### Exact Duplicates - Remove
```python
# If two tasks are identical except for ID, keep first, remove second
{"id": "validator_007", "title": "Create Customer Tests", ...}
{"id": "validator_015", "title": "Create Customer Tests", ...}  # DELETE
```

### Near Duplicates - Merge
```python
# BEFORE (redundant):
{"id": "validator_007", "title": "Test Customer Read Operations", ...}
{"id": "validator_008", "title": "Test Customer Browse Operations", ...}

# AFTER (merged):
{"id": "validator_007", "title": "Test Customer Read and Browse Operations", ...}
# Update all dependencies from validator_008 → validator_007
```

## Renumbering Convention
After cleanup, renumber sequentially within each category:
```python
setup_001, setup_002, setup_003...
validator_001, validator_002, validator_003...
migrate_001, migrate_002, migrate_003...
integrate_001, integrate_002, integrate_003...
```

## Dependency Repair

### Fix Orphaned References
```python
# If migrate_015 depends on validator_008 (which was merged into validator_007)
# Update: depends_on: ["validator_008"] → depends_on: ["validator_007"]
```

### Remove Self-Dependencies
```python
# BAD: Task depends on itself
{"id": "migrate_001", "depends_on": ["migrate_001", "setup_001"]}
# FIX: Remove self-reference
{"id": "migrate_001", "depends_on": ["setup_001"]}
```

## Brevity Enforcement
If any fields are too long, trim them:
```python
# BEFORE (too verbose):
"content": "This task will comprehensively migrate all customer operations including reads, writes, updates, and deletes with full transaction support and comprehensive validation of all edge cases and error conditions."

# AFTER (concise and focused):
"content": "Migrate all customer CRUD operations. Handle transaction boundaries. Add caching layer."
```

## Validation Checklist
- [ ] No duplicate IDs
- [ ] All IDs follow naming convention (setup_, validator_, migrate_, integrate_)
- [ ] Sequential numbering within each category
- [ ] All dependencies exist
- [ ] No circular dependencies
- [ ] All fields respect length limits
- [ ] No orphaned tasks

## What to Preserve
- **Keep all essential work** - Don't delete tasks just because they seem small
- **Maintain logical flow** - Dependencies should still make sense
- **Preserve validators** - Every migration still needs validation

## Decision Log
When making significant changes, add a comment:
```python
# Merged validator_008 into validator_007 (both tested customer reads)
# Removed duplicate setup_015 (identical to setup_003)  
# Renumbered all tasks sequentially after cleanup
```

## Final Validation
Must pass all checks:
```bash
python src/utils/validate_graph.py migration_plan.py
```

## Output  
Update `migration_plan.py` with cleaned, deduplicated, properly numbered tasks.
