#!/usr/bin/env python3
"""
Test the full orchestration cycle with PR merge waiting and phase 11.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.orchestrate_deterministic import orchestrate_migration

def test_dry_run():
    """Test the orchestrator in dry-run mode."""
    print("🧪 Testing orchestrator in dry-run mode...")
    print("=" * 60)
    
    result = orchestrate_migration(
        max_parallel=3,
        wait_between_batches=30,
        dry_run=True,
        use_remote_plan=False
    )
    
    print("\n✅ Dry run test complete!")
    print(f"Results: {result}")


def test_full_cycle():
    """Test the full orchestration cycle."""
    print("🧪 Testing full orchestration cycle...")
    print("=" * 60)
    print("\n⚠️  This will:")
    print("1. Execute tasks and create PRs")
    print("2. Run merge conflict resolution")
    print("3. Wait for you to merge PRs")
    print("4. Run Phase 11 verification")
    print("5. Wait for Phase 11 PR merge")
    print("6. Restart cycle with updated plan from GitHub")
    print("\n" + "=" * 60)
    
    response = input("Continue with full test? (y/n): ")
    if response.lower() != 'y':
        print("Test cancelled.")
        return
    
    result = orchestrate_migration(
        max_parallel=2,  # Start conservatively
        wait_between_batches=30,
        dry_run=False,
        use_remote_plan=True
    )
    
    print("\n✅ Full cycle test complete!")
    print(f"Results: {result}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test orchestrator cycle")
    parser.add_argument("--full", action="store_true",
                       help="Run full cycle test (not just dry run)")
    
    args = parser.parse_args()
    
    if args.full:
        test_full_cycle()
    else:
        test_dry_run()
