# Phased Migration Plan Generation - Orchestration Guide

## Overview
Building a complete migration plan is too complex for a single agent session. We break it into 10 focused phases, each handled by a separate agent session. This ensures accuracy and allows human review between phases.

## The Phases

### Phase 1: Discovery (phases/phase1_discovery.md)
**Purpose**: Find ALL work that needs to be done
**Output**: Basic task list with IDs, titles, content, estimated_hours
**Key**: Be exhaustive - better to have too many tasks than miss something

### Phase 2: Splitting (phases/phase2_splitting.md)  
**Purpose**: Right-size tasks (6-12 hours ideal)
**Output**: Tasks split/combined to appropriate granularity
**Key**: Maintain all work while adjusting size

### Phase 3: Dependencies (phases/phase3_dependencies.md)
**Purpose**: Add logical execution order
**Output**: Tasks with `depends_on` field populated
**Key**: Only natural dependencies, allow parallelism

### Phase 4: Post-Migration Validators (phases/phase4_validators.md)
**Purpose**: Create validator tasks that VALIDATE migrations after they're complete
**Output**: New validator_* task nodes that depend on migration tasks  
**Key**: Validators run AFTER migration to verify the migration worked correctly

### Phase 5: Cleanup #1 (phases/phase5_cleanup.md)
**Purpose**: Dedupe, fix orphans, renumber
**Output**: Clean, properly numbered task graph
**Key**: Remove redundancy while preserving all work

### Phase 6: Mechanisms (phases/phase6_mechanisms.md)
**Purpose**: Define HOW to validate each task
**Output**: Tasks with `validation_mechanism` field
**Key**: Specific, measurable validation methods

### Phase 7: Actions (phases/phase7_actions.md)
**Purpose**: Add brief action descriptions
**Output**: Tasks with `action` field (brief and actionable)
**Key**: Concise, actionable instructions

### Phase 8: Comprehensive Test Coverage (phases/phase8_coverage.md)
**Purpose**: Create comprehensive test suites after migration is validated
**Output**: New coverage_* task nodes that depend on both migration and validation
**Key**: Build exhaustive test suites for long-term CI/CD and maintenance

### Phase 9: Success Criteria (phases/phase9_success_criteria.md)
**Purpose**: Define completion criteria
**Output**: Tasks with `definition_of_done` field (1 sentence)
**Key**: Binary, measurable success metrics

### Phase 10: Final Audit (phases/phase10_final_audit.md)
**Purpose**: Final polish and validation
**Output**: Production-ready migration plan
**Key**: Everything validates, nothing missing

## Execution Workflow

```
1. Run Phase 1 agent with phases/phase1_discovery.md prompt
   → Review PR
   
2. Run Phase 2 agent with phases/phase2_splitting.md prompt  
   → Review PR
   
3. Run Phase 3 agent with phases/phase3_dependencies.md prompt
   → Review PR
   
4. Run Phase 4 agent with phases/phase4_validators.md prompt
   → Review PR
   
5. Run Cleanup agent with phases/phase5_cleanup.md prompt
   → Review PR
   
6. Run Phase 6 agent with phases/phase6_mechanisms.md prompt
   → Review PR
   
7. Run Phase 7 agent with phases/phase7_actions.md prompt
   → Review PR
   
8. Run Phase 8 agent with phases/phase8_coverage.md prompt
   → Review PR
   
9. Run Phase 9 agent with phases/phase9_success_criteria.md prompt
   → Review PR
   
10. Run Final Audit agent with phases/phase10_final_audit.md prompt
    → Review PR → DONE
```

## Key Principles

### 1. One Focus Per Phase
Each agent session has ONE job. Don't ask them to multitask.

### 2. Allow Task Addition
Any phase can add missing tasks if discovered. Better too many than too few.

### 3. Validate Often  
Each prompt includes validation step: `python src/utils/validate_graph.py migration_plan.py`

### 4. Human Review Between Phases
Review each PR before proceeding. Catch issues early.

### 5. Enforce Brevity
- Titles: 20 words max
- Keep all fields concise and focused
- Focus on WHAT, not HOW

## Sandbox Assumptions (Critical)
All phases operate under these constraints:
- No external APIs or databases
- Use SQLite for data storage
- No authentication/authorization needed
- No regulatory compliance requirements
- All services remain internal
- Use local stubs/fixtures

## Validation Script
The `src/utils/validate_graph.py` script checks:
- Unique IDs
- Naming conventions
- Field brevity
- Required fields
- Valid status values  
- Dependencies exist
- No cycles
- Time estimates reasonable

### Automated Validation
GitHub Actions automatically validates `migration_plan.py` on:
- Push events that modify `migration_plan.py`
- Pull requests that modify `migration_plan.py`

See `.github/workflows/validate_migration_plan.yml` for the automation setup.

## Common Issues and Fixes

| Issue | Solution | Phase to Fix |
|-------|----------|--------------|
| Duplicate tasks | Merge in cleanup phases (5 or 10) | 5, 10 |
| Missing validators | Add validator tasks that depend on migrations | 4 |
| Missing coverage tasks | Add coverage task nodes in Phase 8 | 8 |
| Wrong dependencies | Fix in Phase 3 or cleanup | 3, 5 |
| Tasks too large | Split in Phase 2 | 2 |
| Vague validation_mechanism field | Specify in Phase 6 | 6 |
| Missing work | Add in any phase when discovered | Any |
| Circular dependencies | Fix in cleanup phases | 5, 10 |

## Success Metrics
A good migration plan has:
- 50-100 tasks total (depending on system size)
- ~15-20% validator tasks (post-migration validation)
- ~10-15% coverage tasks (comprehensive tests) 
- ~10-15% setup tasks
- ~40-50% migration tasks
- ~10-15% integration tasks
- Maximum dependency depth of 6-7 levels
- 3-5 parallel work streams

## Notes
- If the system is very large (100+ programs), consider running Phase 1 multiple times for different subsystems
- For complex integrations, might need a dedicated integration phase after Phase 9
- The cleanup phases (5 and 10) are critical - don't skip them
- Trust the process - each phase builds on the previous one
- The migrate-first approach (migrate → validate → coverage) matches real migration patterns where you validate what was built
