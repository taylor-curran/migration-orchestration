# Migration Analysis Prompt - Stability-First Parallel Execution

Analyze source repository at `[source_path]` and target repository at `[target_path]` to create a migration plan that prioritizes stability through continuous validation and feedback loops.

## Core Philosophy

**Stability Over Speed**: Never sacrifice validation for velocity. Every parallel group must be followed by validation and learning.

**Continuous Feedback**: Build in monitoring, validation, and adaptation points throughout - not just at the end.

**Learn and Adapt**: After each parallel group, we audit results and adjust the next phase based on learnings.

## Core Requirements

**Task Sizing**: Each task 0.5-1 day. Add 30-50% buffer for complex operations. Be honest about complexity - underestimation kills projects.

**Validation First**: Every task must define how we know it succeeded. No task is complete without validation.

**Dependency Clarity**: Explicit dependencies enable parallelization. Every task states what it needs and what needs it.

## Analysis Steps

### 1. Observability & Baselines (ABSOLUTELY FIRST)
Before touching ANY code, establish your eyes and ears:
- **pre_000**: Performance baseline - measure EVERYTHING (latency, throughput, error rates)
- **Monitoring/alerting**: Real-time dashboards, anomaly detection, alert thresholds
- **Audit trail framework**: Every financial operation must be traceable
- **Continuous validation hooks**: Build the infrastructure to validate as you go
- **Why**: You can't improve what you can't measure. You can't debug what you can't see.

### 2. Infrastructure Foundation
After observability, build the foundation:
- Authentication/authorization framework
- Session management 
- Database connection pools (sized based on actual patterns from baseline)
- Shared services (ID generation with proper atomicity)
- UI component library
- Network configuration for gradual rollout

### 3. Dependency Mapping 
Map TRUE dependencies that prevent parallelization:
- **Data dependencies**: Task B needs data created by Task A
- **Service dependencies**: Task B calls service created by Task A  
- **Cascade dependencies**: Delete operations need their target operations first
- **Infrastructure dependencies**: Business logic needs framework setup first
- **WRONG**: Don't create artificial dependencies between unrelated tasks

### 4. Parallel Group Identification with Validation Gates
Group tasks that can run in parallel, BUT each group must include:
- **Parallel tasks**: What can run together (read-only ops, different entities, independent workflows)
- **Validation gate**: What we validate after this group completes
- **Learning checkpoint**: What we might discover that changes the next group
- **Resource limits**: Max 2-3 parallel to avoid exhaustion
- **Example**: "Phase 1: Read Ops" → Validate performance → Learn actual latencies → Adjust Phase 2 estimates

### 5. Continuous Validation Strategy (NOT JUST CHECKPOINTS)
Build validation INTO the migration, not after:
- **During migration**: Real-time monitoring, continuous data validation
- **After each task**: Automated tests, performance checks, data consistency
- **After each group**: Comprehensive validation before proceeding
- **Dual-write validation**: Both systems write, continuous comparison, zero tolerance for discrepancies
- **Rollback triggers**: Define specific metrics that force a rollback

### 6. Feedback Loop Architecture
After EVERY parallel group:
- **What worked**: Actual hours vs estimated, performance vs baseline
- **What didn't**: Unexpected dependencies, complexity underestimation  
- **What we learned**: New patterns, better approaches
- **How we adapt**: Update next phase estimates, adjust parallelization
- **This is NOT optional**: Plans that don't adapt are plans that fail

## Required Output Format

```python
migration_plan_graph = {
  "migration_plan": {
    "pre_migration_tasks": [
      {
        "id": "pre_000",  # ALWAYS start with observability
        "content": "Establish performance baseline and monitoring infrastructure",
        "type": "baseline",
        "estimated_hours": 12,
        "validation": "Dashboards live, baseline documented, alerts configured",
        "blocks": ["val_performance"],
        "deliverables": ["baseline_metrics.md", "dashboard_urls.txt", "alert_rules.yaml"]
      }
    ],
    "migration_tasks": [
      {
        "id": "mig_001",
        "content": "Migrate CustomerService read operations",
        "complexity": "low",
        "estimated_hours": 6,
        "depends_on": ["pre_000", "pre_001"],  # Need monitoring first!
        "can_parallel_with": ["mig_005"],  
        "validation_steps": [
          "Unit tests pass (80% coverage)",
          "Performance within 10% of baseline",
          "Zero data discrepancies in validation run"
        ],
        "continuous_validation": "Real-time comparison with legacy during dual-read",
        "rollback_strategy": "Feature flag to legacy, rollback if error rate > 0.1%"
      }
    ],
    "validation_tasks": [
      {
        "id": "val_continuous_001",
        "content": "Continuous validation during Phase 1 dual-read period",
        "type": "continuous",  # Runs throughout, not just at end
        "depends_on": ["mig_001", "mig_005"],
        "success_criteria": "Real-time dashboard shows zero discrepancies",
        "monitors": ["Latency comparison", "Data consistency", "Error rates"]
      }
    ]
  },
  
  # CRITICAL: Define clear parallel execution groups with validation gates
  "parallel_groups": [
    {
      "name": "Phase 1: Read Operations",
      "task_ids": ["mig_001", "mig_005"],
      "max_parallel": 2,
      "rationale": "Both read-only, different data stores, no shared state",
      
      # VALIDATION GATE - What happens after this group
      "validation_after": {
        "continuous": "val_continuous_001",  # Running during execution
        "gate": "checkpoint_1",  # Must pass before next group
        "duration": "24-48 hours dual-read validation"
      },
      
      # LEARNING CHECKPOINT - How we adapt
      "expected_learnings": [
        "Actual performance vs baseline",
        "Unexpected data patterns",
        "Resource utilization reality"
      ],
      "adapts": "Phase 2 estimates and parallelization"
    }
  ],
  
  "critical_path": ["pre_000", "pre_001", "mig_001", "val_continuous_001"],
  
  "checkpoints": [
    {
      "id": "checkpoint_1",
      "after_groups": ["Phase 1"],
      "validation": "Read ops validated with continuous monitoring",
      "metrics_required": [
        "P95 latency within 10% of baseline",
        "Zero data discrepancies over 24 hours",
        "Error rate < 0.01%"
      ],
      "proceed_if": "All metrics met",
      "rollback_if": "Any metric fails",
      "learnings_to_document": [
        "Actual hours vs estimated",
        "Performance characteristics",
        "Discovered dependencies"
      ]
    }
  ]
}
```

## Key Output Principles

### Stability & Monitoring First
- **pre_000 ALWAYS first**: Can't validate "within 10% of legacy" without baseline
- **Observability before code**: Build monitoring/alerting infrastructure first
- **Continuous validation**: Not just checkpoints - real-time monitoring throughout
- **Zero tolerance**: Financial data requires ZERO discrepancies, not percentages

### Parallel Execution with Validation Gates
- **CAN parallelize**: Read operations, different entities, independent UI screens
- **CANNOT parallelize**: Shared counters, cascade operations, distributed transactions  
- **Resource limits**: Max 2-3 parallel tasks to avoid exhaustion
- **ALWAYS validate after parallel group**: Never proceed without validation

### Feedback Loops Are Mandatory
- **After each group**: Document what worked, what didn't, what we learned
- **Adapt the plan**: Update estimates, adjust parallelization based on learnings
- **Continuous over batch**: Continuous validation reveals issues immediately
- **Plans that don't adapt are plans that fail**

### Honest Complexity Assessment
- **Add 30-50% buffer** to complex tasks - optimism kills projects
- **Document uncertainty**: Flag tasks where estimates are guesses
- **Learn from actuals**: First task in a category informs others
- **Infrastructure takes time**: Don't underestimate setup tasks

### Validation Is Not Optional
- **Every task**: Define success criteria before starting
- **Every group**: Gate before proceeding to next phase
- **Continuous monitoring**: Real-time dashboards, not just end-of-phase checks
- **Rollback triggers**: Define specific metrics that force rollback
- **If you can't measure it, you can't migrate it**
