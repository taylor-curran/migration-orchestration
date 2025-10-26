#!/usr/bin/env python3
"""
Test the MVP orchestration with a simplified migration plan.
This creates a small test plan to validate the orchestration logic.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from orchestrate_migration_v2 import orchestrate_migration, find_ready_tasks, update_migration_plan
from prefect import flow
from prefect.logging import get_run_logger

# Create a minimal test migration plan
TEST_MIGRATION_PLAN = {
    "metadata": {
        "source_repo": "test-source",
        "target_repo": "test-target",
    },
    "tasks": [
        {
            "id": "setup_001",
            "title": "Setup Monitoring",
            "content": "Setup monitoring infrastructure",
            "status": "pending",
            "depends_on": [],
            "action": "Deploy monitoring stack",
            "definition_of_done": "Monitoring operational",
            "validation_mechanism": "Dashboards accessible",
            "estimated_hours": 4,
        },
        {
            "id": "setup_002", 
            "title": "Setup CI/CD",
            "content": "Setup CI/CD pipeline",
            "status": "pending",
            "depends_on": [],
            "action": "Configure CI/CD",
            "definition_of_done": "Pipeline running",
            "validation_mechanism": "Builds passing",
            "estimated_hours": 4,
        },
        {
            "id": "validator_001",
            "title": "Create Customer Tests",
            "content": "Build customer test suite",
            "status": "pending",
            "depends_on": ["setup_001"],
            "action": "Write comprehensive tests",
            "definition_of_done": "Tests passing",
            "validation_mechanism": "90% coverage",
            "estimated_hours": 6,
        },
        {
            "id": "validator_002",
            "title": "Create Account Tests",
            "content": "Build account test suite",
            "status": "pending",
            "depends_on": ["setup_002"],
            "action": "Write account tests",
            "definition_of_done": "Tests passing",
            "validation_mechanism": "90% coverage",
            "estimated_hours": 6,
        },
        {
            "id": "migrate_001",
            "title": "Migrate Customer Service",
            "content": "Migrate customer operations",
            "status": "pending",
            "depends_on": ["validator_001"],
            "action": "Implement customer service",
            "definition_of_done": "Service working",
            "validation_mechanism": "Tests pass",
            "estimated_hours": 8,
        },
        {
            "id": "migrate_002",
            "title": "Migrate Account Service",
            "content": "Migrate account operations",
            "status": "pending",
            "depends_on": ["validator_002"],
            "action": "Implement account service",
            "definition_of_done": "Service working",
            "validation_mechanism": "Tests pass",
            "estimated_hours": 8,
        },
    ]
}


@flow(name="Test Orchestration Logic")
def test_orchestration_logic():
    """Test the orchestration logic without running actual Devin sessions."""
    logger = get_run_logger()
    
    logger.info("🧪 Testing Orchestration Logic with Sample Plan")
    logger.info("="*50)
    
    plan = TEST_MIGRATION_PLAN.copy()
    
    # Iteration 1: Should find setup_001 and setup_002 (parallel, no dependencies)
    logger.info("\n📍 Iteration 1: Finding initial ready tasks...")
    ready_tasks = find_ready_tasks(plan, max_parallel=3)
    assert len(ready_tasks) == 2, f"Expected 2 ready tasks, got {len(ready_tasks)}"
    assert ready_tasks[0]["id"] in ["setup_001", "setup_002"]
    logger.info(f"✅ Found {len(ready_tasks)} parallel setup tasks")
    
    # Simulate completing setup tasks
    logger.info("\n📝 Simulating completion of setup tasks...")
    for task in plan["tasks"]:
        if task["id"] in ["setup_001", "setup_002"]:
            task["status"] = "completed"
    
    # Iteration 2: Should find validator_001 and validator_002 (parallel)
    logger.info("\n📍 Iteration 2: Finding validator tasks...")
    ready_tasks = find_ready_tasks(plan, max_parallel=3)
    assert len(ready_tasks) == 2, f"Expected 2 ready tasks, got {len(ready_tasks)}"
    assert ready_tasks[0]["id"] in ["validator_001", "validator_002"]
    logger.info(f"✅ Found {len(ready_tasks)} parallel validator tasks")
    
    # Simulate completing validator tasks
    logger.info("\n📝 Simulating completion of validator tasks...")
    for task in plan["tasks"]:
        if task["id"] in ["validator_001", "validator_002"]:
            task["status"] = "completed"
    
    # Iteration 3: Should find migrate_001 and migrate_002 (parallel)
    logger.info("\n📍 Iteration 3: Finding migration tasks...")
    ready_tasks = find_ready_tasks(plan, max_parallel=3)
    assert len(ready_tasks) == 2, f"Expected 2 ready tasks, got {len(ready_tasks)}"
    assert ready_tasks[0]["id"] in ["migrate_001", "migrate_002"]
    logger.info(f"✅ Found {len(ready_tasks)} parallel migration tasks")
    
    # Simulate completing migration tasks
    logger.info("\n📝 Simulating completion of migration tasks...")
    for task in plan["tasks"]:
        if task["id"] in ["migrate_001", "migrate_002"]:
            task["status"] = "completed"
    
    # Iteration 4: Should find no ready tasks (all complete)
    logger.info("\n📍 Iteration 4: Checking for completion...")
    ready_tasks = find_ready_tasks(plan, max_parallel=3)
    assert len(ready_tasks) == 0, f"Expected 0 ready tasks, got {len(ready_tasks)}"
    
    # Check all tasks are complete
    all_complete = all(t["status"] == "completed" for t in plan["tasks"])
    assert all_complete, "Not all tasks are completed"
    logger.info("✅ All tasks completed!")
    
    logger.info("\n" + "="*50)
    logger.info("🎉 Orchestration Logic Test PASSED")
    logger.info("="*50)
    
    # Show the dependency flow
    logger.info("\n📊 Execution Flow:")
    logger.info("   Iteration 1: setup_001, setup_002 (parallel)")
    logger.info("   Iteration 2: validator_001, validator_002 (parallel)")
    logger.info("   Iteration 3: migrate_001, migrate_002 (parallel)")
    logger.info("   Iteration 4: ✅ Complete")


if __name__ == "__main__":
    # Test the orchestration logic
    test_orchestration_logic()
    
    print("\n" + "="*50)
    print("💡 Next Steps:")
    print("="*50)
    print("1. Run with actual Devin sessions: python src/orchestrate_migration_v2.py")
    print("2. Add HIL component for audit phases")
    print("3. Add re-planning logic based on analysis")
    print("4. Add web UI for monitoring progress")
    print("5. Integrate with GitHub for PR submission")
