#!/usr/bin/env python3
"""
Parallel Task Detection Utility

Analyzes task dependencies to identify which tasks can run in parallel.
Used by visualization, orchestration, and planning tools.
"""

from typing import Dict, List, Set, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict, deque


@dataclass
class ParallelGroup:
    """Represents a group of tasks that can run in parallel."""
    level: int  # Depth in the dependency graph
    task_ids: List[str]  # Tasks that can run simultaneously
    earliest_start: int  # Earliest this group can start (cumulative hours)
    max_duration: int  # Duration of longest task in group
    
    @property
    def size(self) -> int:
        """Number of tasks in this parallel group."""
        return len(self.task_ids)
    
    @property
    def time_saved(self) -> int:
        """Hours saved by running in parallel vs serial."""
        if self.size <= 1:
            return 0
        # Sum of all task durations minus the max duration
        return sum(self.task_durations.values()) - self.max_duration
    
    def __post_init__(self):
        """Initialize task durations if not provided."""
        if not hasattr(self, 'task_durations'):
            self.task_durations = {}


@dataclass
class ExecutionPlan:
    """Complete execution plan with parallel groups and statistics."""
    parallel_groups: List[ParallelGroup]
    serial_tasks: List[str]  # Tasks that must run alone
    critical_path: List[str]  # Longest dependency chain
    critical_path_duration: int  # Total hours for critical path
    total_duration_serial: int  # Hours if all tasks run serially
    total_duration_parallel: int  # Hours with parallel execution
    max_parallelism: int  # Maximum tasks that can run simultaneously
    
    @property
    def time_saved(self) -> int:
        """Total time saved through parallelization."""
        return self.total_duration_serial - self.total_duration_parallel
    
    @property
    def efficiency_gain(self) -> float:
        """Percentage improvement from parallelization."""
        if self.total_duration_serial == 0:
            return 0.0
        return (self.time_saved / self.total_duration_serial) * 100


class ParallelDetector:
    """Detects parallel execution opportunities in task graphs."""
    
    def __init__(self, tasks: List[Dict[str, Any]]):
        """
        Initialize with task list.
        
        Args:
            tasks: List of task dictionaries with 'id', 'depends_on', and optionally 'estimated_hours'
        """
        self.tasks = tasks
        self.task_dict = {task['id']: task for task in tasks}
        self.reverse_deps = self._build_reverse_dependencies()
    
    def _build_reverse_dependencies(self) -> Dict[str, Set[str]]:
        """Build a map of task -> tasks that depend on it."""
        reverse_deps = defaultdict(set)
        for task in self.tasks:
            task_id = task['id']
            for dep in task.get('depends_on', []):
                reverse_deps[dep].add(task_id)
        return dict(reverse_deps)
    
    def calculate_levels(self) -> Dict[str, int]:
        """
        Calculate the level (depth) of each task in the dependency graph.
        Level 0 = no dependencies, Level N = depends on level N-1 tasks.
        
        Returns:
            Dictionary mapping task_id to level number
        """
        levels = {}
        visited = set()
        
        def get_level(task_id: str) -> int:
            if task_id in levels:
                return levels[task_id]
            
            if task_id in visited:
                # Circular dependency detected
                raise ValueError(f"Circular dependency detected involving task: {task_id}")
            
            visited.add(task_id)
            
            task = self.task_dict.get(task_id, {})
            deps = task.get('depends_on', [])
            
            if not deps:
                levels[task_id] = 0
            else:
                # Filter out non-existent dependencies
                valid_deps = [d for d in deps if d in self.task_dict]
                if not valid_deps:
                    levels[task_id] = 0
                else:
                    max_dep_level = max(get_level(dep) for dep in valid_deps)
                    levels[task_id] = max_dep_level + 1
            
            visited.remove(task_id)
            return levels[task_id]
        
        for task_id in self.task_dict:
            get_level(task_id)
        
        return levels
    
    def detect_parallel_groups(self) -> List[ParallelGroup]:
        """
        Detect groups of tasks that can run in parallel.
        
        Returns:
            List of ParallelGroup objects
        """
        levels = self.calculate_levels()
        
        # Group tasks by level
        tasks_by_level = defaultdict(list)
        for task_id, level in levels.items():
            tasks_by_level[level].append(task_id)
        
        parallel_groups = []
        cumulative_time = 0
        
        for level in sorted(tasks_by_level.keys()):
            task_ids = tasks_by_level[level]
            
            # Within a level, find tasks that don't depend on each other
            independent_groups = self._find_independent_groups(task_ids)
            
            for group in independent_groups:
                if len(group) > 1:  # Only consider groups with 2+ tasks
                    # Calculate durations
                    durations = {}
                    for task_id in group:
                        task = self.task_dict[task_id]
                        durations[task_id] = task.get('estimated_hours', 8)
                    
                    pg = ParallelGroup(
                        level=level,
                        task_ids=group,
                        earliest_start=cumulative_time,
                        max_duration=max(durations.values()) if durations else 8
                    )
                    pg.task_durations = durations
                    parallel_groups.append(pg)
            
            # Update cumulative time (max duration at this level)
            level_duration = 0
            for task_id in task_ids:
                task = self.task_dict[task_id]
                duration = task.get('estimated_hours', 8)
                level_duration = max(level_duration, duration)
            cumulative_time += level_duration
        
        return parallel_groups
    
    def _find_independent_groups(self, task_ids: List[str]) -> List[List[str]]:
        """
        Find groups of tasks that don't depend on each other.
        
        Args:
            task_ids: List of task IDs to analyze
            
        Returns:
            List of groups where tasks within each group are independent
        """
        if len(task_ids) <= 1:
            return [task_ids] if task_ids else []
        
        # Check dependencies between tasks
        groups = []
        used = set()
        
        for task_id in task_ids:
            if task_id in used:
                continue
            
            group = [task_id]
            used.add(task_id)
            
            # Try to add other tasks that don't conflict
            for other_id in task_ids:
                if other_id in used:
                    continue
                
                # Check if this task can be added to the group
                can_add = True
                for existing_id in group:
                    if self._has_dependency_between(existing_id, other_id):
                        can_add = False
                        break
                
                if can_add:
                    group.append(other_id)
                    used.add(other_id)
            
            groups.append(group)
        
        return groups
    
    def _has_dependency_between(self, task1: str, task2: str) -> bool:
        """
        Check if there's a dependency relationship between two tasks.
        
        Args:
            task1: First task ID
            task2: Second task ID
            
        Returns:
            True if one depends on the other (directly or indirectly)
        """
        # Check direct dependencies
        task1_deps = set(self.task_dict[task1].get('depends_on', []))
        task2_deps = set(self.task_dict[task2].get('depends_on', []))
        
        if task2 in task1_deps or task1 in task2_deps:
            return True
        
        # Check transitive dependencies using BFS
        def has_path(from_task: str, to_task: str) -> bool:
            visited = set()
            queue = deque([from_task])
            
            while queue:
                current = queue.popleft()
                if current == to_task:
                    return True
                
                if current in visited:
                    continue
                visited.add(current)
                
                # Add dependencies to queue
                task = self.task_dict.get(current, {})
                for dep in task.get('depends_on', []):
                    if dep in self.task_dict:
                        queue.append(dep)
            
            return False
        
        return has_path(task1, task2) or has_path(task2, task1)
    
    def calculate_critical_path(self) -> Tuple[List[str], int]:
        """
        Calculate the critical path through the task graph.
        
        Returns:
            Tuple of (critical_path_task_ids, total_duration)
        """
        # Use dynamic programming to find longest path
        task_times = {}
        task_paths = {}
        
        def get_longest_path(task_id: str) -> Tuple[int, List[str]]:
            if task_id in task_times:
                return task_times[task_id], task_paths[task_id]
            
            task = self.task_dict[task_id]
            duration = task.get('estimated_hours', 8)
            deps = task.get('depends_on', [])
            
            if not deps:
                task_times[task_id] = duration
                task_paths[task_id] = [task_id]
            else:
                max_dep_time = 0
                max_dep_path = []
                
                for dep in deps:
                    if dep in self.task_dict:
                        dep_time, dep_path = get_longest_path(dep)
                        if dep_time > max_dep_time:
                            max_dep_time = dep_time
                            max_dep_path = dep_path
                
                task_times[task_id] = max_dep_time + duration
                task_paths[task_id] = max_dep_path + [task_id]
            
            return task_times[task_id], task_paths[task_id]
        
        # Find the longest path from any task
        max_time = 0
        critical_path = []
        
        for task_id in self.task_dict:
            time, path = get_longest_path(task_id)
            if time > max_time:
                max_time = time
                critical_path = path
        
        return critical_path, max_time
    
    def get_execution_plan(self) -> ExecutionPlan:
        """
        Generate a complete execution plan with parallelization analysis.
        
        Returns:
            ExecutionPlan object with all statistics
        """
        parallel_groups = self.detect_parallel_groups()
        critical_path, critical_duration = self.calculate_critical_path()
        
        # Identify serial tasks (not in any parallel group)
        parallel_task_ids = set()
        for group in parallel_groups:
            parallel_task_ids.update(group.task_ids)
        
        serial_tasks = [
            task['id'] for task in self.tasks 
            if task['id'] not in parallel_task_ids
        ]
        
        # Calculate total serial duration
        total_serial = sum(
            task.get('estimated_hours', 8) 
            for task in self.tasks
        )
        
        # Calculate parallel execution duration
        levels = self.calculate_levels()
        level_durations = defaultdict(int)
        
        for task_id, level in levels.items():
            task = self.task_dict[task_id]
            duration = task.get('estimated_hours', 8)
            level_durations[level] = max(level_durations[level], duration)
        
        total_parallel = sum(level_durations.values())
        
        # Find maximum parallelism
        max_parallelism = max(
            (group.size for group in parallel_groups),
            default=1
        )
        
        return ExecutionPlan(
            parallel_groups=parallel_groups,
            serial_tasks=serial_tasks,
            critical_path=critical_path,
            critical_path_duration=critical_duration,
            total_duration_serial=total_serial,
            total_duration_parallel=total_parallel,
            max_parallelism=max_parallelism
        )


def analyze_tasks(tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Convenience function to analyze tasks and return summary statistics.
    
    Args:
        tasks: List of task dictionaries
        
    Returns:
        Dictionary with parallelization analysis
    """
    detector = ParallelDetector(tasks)
    plan = detector.get_execution_plan()
    
    return {
        'total_tasks': len(tasks),
        'parallel_groups': len(plan.parallel_groups),
        'serial_tasks': len(plan.serial_tasks),
        'parallelizable_tasks': len(tasks) - len(plan.serial_tasks),
        'max_parallelism': plan.max_parallelism,
        'critical_path_length': len(plan.critical_path),
        'critical_path_duration': plan.critical_path_duration,
        'total_duration_serial': plan.total_duration_serial,
        'total_duration_parallel': plan.total_duration_parallel,
        'time_saved': plan.time_saved,
        'efficiency_gain': round(plan.efficiency_gain, 1),
        'critical_path': plan.critical_path,
        'parallel_groups_detail': [
            {
                'level': g.level,
                'tasks': g.task_ids,
                'size': g.size,
                'max_duration': g.max_duration,
                'time_saved': g.time_saved
            }
            for g in plan.parallel_groups
        ]
    }


# Example usage
if __name__ == "__main__":
    # Example task list
    example_tasks = [
        {"id": "setup_001", "title": "Setup monitoring", "depends_on": [], "estimated_hours": 8},
        {"id": "setup_002", "title": "Setup database", "depends_on": [], "estimated_hours": 6},
        {"id": "validator_001", "title": "Create tests", "depends_on": ["setup_001"], "estimated_hours": 10},
        {"id": "migrate_001", "title": "Migrate service A", "depends_on": ["setup_001", "setup_002", "validator_001"], "estimated_hours": 12},
        {"id": "migrate_002", "title": "Migrate service B", "depends_on": ["setup_002", "validator_001"], "estimated_hours": 10},
        {"id": "validate_001", "title": "Validate migration", "depends_on": ["migrate_001", "migrate_002"], "estimated_hours": 8},
    ]
    
    # Analyze
    results = analyze_tasks(example_tasks)
    
    print("Task Parallelization Analysis")
    print("=" * 50)
    print(f"Total tasks: {results['total_tasks']}")
    print(f"Parallel groups: {results['parallel_groups']}")
    print(f"Max parallelism: {results['max_parallelism']} tasks")
    print(f"Critical path: {' -> '.join(results['critical_path'])}")
    print(f"Serial execution time: {results['total_duration_serial']} hours")
    print(f"Parallel execution time: {results['total_duration_parallel']} hours")
    print(f"Time saved: {results['time_saved']} hours ({results['efficiency_gain']}%)")
    print("\nParallel Groups:")
    for group in results['parallel_groups_detail']:
        print(f"  Level {group['level']}: {', '.join(group['tasks'])} ({group['size']} tasks, saves {group['time_saved']}h)")
