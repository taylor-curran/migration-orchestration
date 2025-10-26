#!/usr/bin/env python3
"""
Test the simple parallel runner logic WITHOUT running actual Devin sessions.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from simple_parallel_runner import load_plan, find_ready_tasks

# Create a test migration plan file
TEST_PLAN_CONTENT = '''
migration_plan = {
    "metadata": {
        "source_repo": "taylor-curran/og-cics-cobol-app",
        "target_repo": "taylor-curran/target-springboot-cics",
    },
    "tasks": [
        {
            "id": "setup_001",
            "title": "Setup Monitoring",
            "status": "completed",  # Already done
            "depends_on": [],
            "action": "Setup monitoring",
            "definition_of_done": "Monitoring works",
            "validation_mechanism": "Check dashboards",
        },
        {
            "id": "setup_002",
            "title": "Setup CI/CD",
            "status": "completed",  # Already done
            "depends_on": [],
            "action": "Setup CI/CD",
            "definition_of_done": "CI/CD works",
            "validation_mechanism": "Builds pass",
        },
        {
            "id": "validator_001",
            "title": "Create Customer Tests",
            "status": "pending",  # Ready! (deps completed)
            "depends_on": ["setup_001"],
            "action": "Write tests",
            "definition_of_done": "Tests pass",
            "validation_mechanism": "90% coverage",
        },
        {
            "id": "validator_002",
            "title": "Create Account Tests",
            "status": "pending",  # Ready! (deps completed)
            "depends_on": ["setup_002"],
            "action": "Write tests",
            "definition_of_done": "Tests pass",
            "validation_mechanism": "90% coverage",
        },
        {
            "id": "migrate_001",
            "title": "Migrate Customer Service",
            "status": "pending",  # NOT ready (validator_001 not done)
            "depends_on": ["validator_001"],
            "action": "Migrate service",
            "definition_of_done": "Service works",
            "validation_mechanism": "Tests pass",
        },
    ]
}
'''

def test_logic():
    """Test the task selection logic."""
    print("🧪 Testing Simple Parallel Runner Logic")
    print("="*50)
    
    # Create temporary test file
    import tempfile
    import os
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Write test plan
        plan_path = Path(tmpdir) / "migration_plan.py"
        plan_path.write_text(TEST_PLAN_CONTENT)
        
        # Test loading
        print("\n📖 Testing load_plan()...")
        plan = load_plan(tmpdir)
        assert len(plan["tasks"]) == 5
        print(f"   ✅ Loaded {len(plan['tasks'])} tasks")
        
        # Test finding ready tasks
        print("\n🔍 Testing find_ready_tasks()...")
        ready = find_ready_tasks(plan)
        print(f"   Found {len(ready)} ready tasks:")
        for task in ready:
            print(f"   • {task['id']}: {task['title']}")
        
        # Validate results
        assert len(ready) == 2, f"Expected 2 ready tasks, got {len(ready)}"
        ready_ids = [t["id"] for t in ready]
        assert "validator_001" in ready_ids
        assert "validator_002" in ready_ids
        assert "migrate_001" not in ready_ids  # Should NOT be ready
        
        print("\n✅ Logic test PASSED!")
        print("\nExpected behavior:")
        print("  • setup_001, setup_002: Completed (skipped)")
        print("  • validator_001, validator_002: Ready to run in parallel")
        print("  • migrate_001: Not ready (waiting for validator_001)")
        
        # Test what happens after validators complete
        print("\n📝 Simulating validator completion...")
        for task in plan["tasks"]:
            if task["id"] in ["validator_001", "validator_002"]:
                task["status"] = "completed"
        
        ready2 = find_ready_tasks(plan)
        print(f"   Now {len(ready2)} tasks ready:")
        for task in ready2:
            print(f"   • {task['id']}: {task['title']}")
        
        assert len(ready2) == 1
        assert ready2[0]["id"] == "migrate_001"
        print("\n✅ Dependency chain working correctly!")


if __name__ == "__main__":
    test_logic()
    
    print("\n" + "="*50)
    print("💡 Next: Run the actual script")
    print("="*50)
    print("1. Make sure migration_plan.py exists in target repo")
    print("2. Run: python src/simple_parallel_runner.py")
    print("3. Review and merge the PRs")
    print("4. Run again for next batch")
