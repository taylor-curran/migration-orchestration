#!/usr/bin/env python3
"""
Test to see if ParallelDetector adds value to our simple orchestration.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.parallel_detector import ParallelDetector

# Example scenario: Multiple ready tasks, but some share resources
SCENARIO_1 = {
    "tasks": [
        # All these are "ready" (no pending dependencies)
        {"id": "test_customer_read", "depends_on": [], "estimated_hours": 8},
        {"id": "test_customer_write", "depends_on": [], "estimated_hours": 8},
        {"id": "test_account_read", "depends_on": [], "estimated_hours": 8},
        {"id": "test_account_write", "depends_on": [], "estimated_hours": 8},
        {"id": "setup_monitoring", "depends_on": [], "estimated_hours": 4},
    ]
}

# More complex scenario with hidden dependencies
SCENARIO_2 = {
    "tasks": [
        # These look independent but validator_002 extends validator_001
        {"id": "validator_001", "depends_on": ["setup"], "estimated_hours": 8},
        {"id": "validator_002", "depends_on": ["setup", "validator_001"], "estimated_hours": 8},
        {"id": "validator_003", "depends_on": ["setup"], "estimated_hours": 8},
        {"id": "setup", "depends_on": [], "estimated_hours": 4, "status": "completed"},
    ]
}

def test_scenario(name: str, tasks: dict):
    """Test a scenario with and without ParallelDetector."""
    print(f"\n{'='*50}")
    print(f"Scenario: {name}")
    print(f"{'='*50}")
    
    # Simple approach: Just take all ready tasks
    ready_tasks = [t for t in tasks["tasks"] if not t.get("depends_on", [])]
    print(f"\n📋 Simple Approach:")
    print(f"   Found {len(ready_tasks)} ready tasks:")
    for t in ready_tasks:
        print(f"   • {t['id']}")
    
    # Smart approach: Use ParallelDetector
    if ready_tasks:
        detector = ParallelDetector(ready_tasks)
        parallel_groups = detector.detect_parallel_groups()
        
        print(f"\n🧠 With ParallelDetector:")
        if parallel_groups:
            for i, group in enumerate(parallel_groups):
                print(f"   Group {i+1}: {', '.join(group.task_ids)} (can run together)")
        else:
            print("   No parallel groups detected (run sequentially)")
        
        # Get execution plan
        plan = detector.get_execution_plan()
        print(f"\n📊 Efficiency Analysis:")
        print(f"   Max parallelism: {plan.max_parallelism} tasks")
        print(f"   Time if serial: {plan.total_duration_serial} hours")
        print(f"   Time if parallel: {plan.total_duration_parallel} hours")
        print(f"   Time saved: {plan.time_saved} hours ({plan.efficiency_gain:.1f}%)")

def main():
    print("🔍 Testing if ParallelDetector adds value...")
    
    # Test Scenario 1: All independent
    test_scenario("All Independent Tasks", SCENARIO_1)
    
    # Test Scenario 2: Hidden dependency
    scenario2_ready = [t for t in SCENARIO_2["tasks"] 
                       if t.get("status") != "completed" 
                       and all(d == "setup" for d in t.get("depends_on", []))]
    test_scenario("Tasks with Hidden Dependencies", {"tasks": scenario2_ready})
    
    print("\n" + "="*50)
    print("💡 Conclusions:")
    print("="*50)
    print("\n✅ ParallelDetector is valuable when:")
    print("  • You have many ready tasks (>3)")
    print("  • You want to optimize execution time")
    print("  • Tasks have complex interdependencies")
    print("\n❌ ParallelDetector might be overkill when:")
    print("  • You only have 1-2 ready tasks anyway")
    print("  • All tasks are truly independent")
    print("  • You're keeping it simple for MVP")

if __name__ == "__main__":
    main()
