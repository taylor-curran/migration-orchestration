#!/usr/bin/env python3
"""
Validation script for migration plan task graphs.
Run this to check for common issues in your migration_plan.py
"""
import sys
from typing import Dict, List, Set, Any

def check_unique_ids(tasks: List[Dict]) -> List[str]:
    """Check for duplicate task IDs."""
    errors = []
    seen_ids = set()
    duplicates = set()
    
    for task in tasks:
        task_id = task.get('id', '')
        if task_id in seen_ids:
            duplicates.add(task_id)
        seen_ids.add(task_id)
    
    if duplicates:
        errors.append(f"❌ Duplicate IDs found: {duplicates}\nFIX: Rename duplicate tasks with unique IDs like setup_001, setup_002, migrate_001, etc. Each ID must be unique across all tasks.")
    else:
        print("✅ All task IDs are unique")
    
    return errors

def check_naming_conventions(tasks: List[Dict]) -> List[str]:
    """Verify tasks follow naming conventions."""
    errors = []
    valid_prefixes = ['setup_', 'migrate_', 'integrate_', 'validator_']
    
    for task in tasks:
        task_id = task.get('id', '')
        if not any(task_id.startswith(prefix) for prefix in valid_prefixes):
            errors.append(f"❌ Invalid ID prefix: {task_id}\nFIX: Change ID to start with one of: {valid_prefixes}\nExample: 'setup_001' for shared infrastructure, 'migrate_001' for migrations, 'validator_001' for tasks that build validation mechanisms like tests data observability etc, 'integrate_001' for integration")
    
    if not errors:
        print("✅ All tasks follow naming conventions")
    
    return errors

def check_field_brevity(tasks: List[Dict]) -> List[str]:
    """Check that fields respect length limits."""
    errors = []
    
    for task in tasks:
        task_id = task.get('id', '')
        
        # Check title length (30 words max)
        title = task.get('title', '')
        if len(title.split()) > 30:
            words_to_remove = len(title.split()) - 30
            errors.append(f"❌ {task_id}: title too long ({len(title.split())} words, max 30)\nFIX: Remove {words_to_remove} word(s) from title. Keep it concise and descriptive.\nCurrent: \"{title[:50]}...\"")
    
    if not errors:
        print("✅ All fields respect brevity limits")
    
    return errors

def check_dependencies_exist(tasks: List[Dict]) -> List[str]:
    """Verify all dependencies reference existing tasks."""
    errors = []
    task_ids = {task.get('id') for task in tasks}
    
    for task in tasks:
        task_id = task.get('id', '')
        deps = task.get('depends_on', [])
        
        for dep in deps:
            if dep not in task_ids:
                # Suggest similar task IDs
                similar = [tid for tid in task_ids if dep.split('_')[0] in tid]
                suggestion = f" Did you mean one of: {similar[:3]}?" if similar else ""
                errors.append(f"❌ {task_id}: depends on non-existent task '{dep}'\nFIX: Either create task '{dep}' or fix the dependency ID.{suggestion}\nAvailable task IDs: {sorted(list(task_ids))[:5]}...")
    
    if not errors:
        print("✅ All dependencies reference existing tasks")
    
    return errors

def detect_cycles(tasks: List[Dict]) -> List[str]:
    """Detect circular dependencies in the task graph."""
    errors = []
    
    # Build adjacency list
    graph = {}
    for task in tasks:
        task_id = task.get('id', '')
        graph[task_id] = task.get('depends_on', [])
    
    # DFS to detect cycles
    visited = set()
    rec_stack = set()
    
    def has_cycle(node: str, path: List[str] = None) -> bool:
        if path is None:
            path = []
        
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if has_cycle(neighbor, path.copy()):
                    return True
            elif neighbor in rec_stack:
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                errors.append(f"❌ Circular dependency detected: {' -> '.join(cycle)}\nFIX: Remove one of these dependencies to break the cycle. Tasks cannot depend on each other in a loop.\nSuggestion: Review if {cycle[-2]} really needs to depend on {cycle[-1]}")
                return True
        
        rec_stack.remove(node)
        return False
    
    for task_id in graph:
        if task_id not in visited:
            has_cycle(task_id)
    
    if not errors:
        print("✅ No circular dependencies detected")
    
    return errors

def check_time_estimates(tasks: List[Dict]) -> List[str]:
    """Check that time estimates are reasonable."""
    errors = []
    warnings = []
    
    for task in tasks:
        task_id = task.get('id', '')
        hours = task.get('estimated_hours', 0)
        
        if hours < 4:
            warnings.append(f"⚠️  {task_id}: very short estimate ({hours} hours)\nCONSIDER: Tasks under 4 hours might be too granular. Can this be combined with related work?")
        elif hours > 20:
            errors.append(f"❌ {task_id}: task too large ({hours} hours, max 20)\nFIX: Split this into 2-3 smaller tasks of 8-12 hours each. DO NOT just reduce the estimate!\nExample splits:\n  - {task_id}_part1: Core implementation (10 hrs)\n  - {task_id}_part2: Testing and validation (8 hrs)\n  - {task_id}_part3: Integration and documentation ({hours - 18} hrs)")
    
    if warnings:
        print("\n".join(warnings))
    
    if not errors:
        print("✅ All time estimates within bounds")
    
    return errors

def check_required_fields(tasks: List[Dict]) -> List[str]:
    """Verify all required fields are present."""
    errors = []
    required_fields = ['id', 'title', 'content', 'status']
    
    for task in tasks:
        task_id = task.get('id', '<no-id>')
        missing = []
        
        for field in required_fields:
            if field not in task or task[field] == "":
                missing.append(field)
        
        if missing:
            field_examples = {'id': '"migrate_001"', 'title': '"Migrate Customer Service"', 'content': '"Port customer CRUD operations."', 'status': '"not-complete"'}
            examples = [f"{field}: {field_examples.get(field, 'value')}" for field in missing]
            errors.append(f"❌ {task_id}: missing required fields {missing}\nFIX: Add these fields to the task:\n  {', '.join(examples)}")
    
    if not errors:
        print("✅ All required fields present")
    
    return errors

def check_status_values(tasks: List[Dict]) -> List[str]:
    """Check that status values are valid."""
    errors = []
    valid_statuses = ['not-complete', 'completed']
    
    for task in tasks:
        task_id = task.get('id', '')
        status = task.get('status', '')
        
        if status not in valid_statuses:
            errors.append(f"❌ {task_id}: invalid status '{status}'\nFIX: Change status to either 'not-complete' or 'completed'\nRule: Use 'not-complete' for any task not 100% done, 'completed' only when fully finished")
    
    if not errors:
        print("✅ All status values are valid")
    
    return errors

def validate_migration_plan(file_path: str = 'migration_plan.py') -> bool:
    """Main validation function."""
    print("\n🔍 Validating Migration Plan Graph...\n")
    
    try:
        # Import the migration plan
        import importlib.util
        spec = importlib.util.spec_from_file_location("migration_plan", file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if not hasattr(module, 'migration_plan'):
            print("❌ migration_plan variable not found in file")
            print("FIX: Ensure your file contains a variable named 'migration_plan' with a dictionary containing a 'tasks' array.")
            print("Example structure:")
            print('migration_plan = {"tasks": [{"id": "setup_001", "title": "...", "content": "...", "status": "not-complete", ...}]}')
            return False
        
        tasks = module.migration_plan.get('tasks', [])
        
        if not tasks:
            print("❌ No tasks found in migration plan")
            print("FIX: Add tasks to the 'tasks' array in your migration_plan dictionary.")
            print("Each task needs: id, title, content, status, and estimated_hours at minimum.")
            return False
        
        print(f"📊 Found {len(tasks)} tasks\n")
        
        # Run all checks
        all_errors = []
        all_errors.extend(check_unique_ids(tasks))
        all_errors.extend(check_naming_conventions(tasks))
        all_errors.extend(check_field_brevity(tasks))
        all_errors.extend(check_required_fields(tasks))
        all_errors.extend(check_status_values(tasks))
        all_errors.extend(check_dependencies_exist(tasks))
        all_errors.extend(detect_cycles(tasks))
        all_errors.extend(check_time_estimates(tasks))
        
        # Report results
        print("\n" + "="*50)
        if all_errors:
            print("\n❌ VALIDATION FAILED\n")
            for error in all_errors:
                print(error)
                print()  # Add spacing between errors
            
            # Print helpful summary
            print("="*50)
            print("\n💡 HOW TO FIX VALIDATION ERRORS:")
            print("\n1. Read each error message above for specific fixes")
            print("2. Common fixes:")
            print("   - Split tasks >20 hours into smaller subtasks")
            print("   - Use valid ID prefixes: setup_, migrate_, validator_, integrate_")
            print("   - Keep titles under 20 words, content under 3 sentences")
            print("   - Use only 'not-complete' or 'completed' for status")
            print("   - Check all dependency IDs exist")
            print("\n3. Run validation again: python src/utils/validate_graph.py migration_plan.py")
            print("\n4. All checks must pass before the migration plan can be used.\n")
            return False
        else:
            print("\n✅ VALIDATION PASSED - Graph looks good!\n")
            return True
            
    except Exception as e:
        print(f"❌ Error loading migration plan: {e}")
        print("\nCOMMON CAUSES:")
        print("1. Syntax error in Python file (check for missing commas, brackets, quotes)")
        print("2. File not found (check file path)")
        print("3. Import errors (ensure file is valid Python)")
        print("\nDEBUG TIP: Try running 'python migration_plan.py' directly to see syntax errors")
        return False

if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else "migration_plan.py"
    sys.exit(0 if validate_migration_plan(file_path) else 1)
