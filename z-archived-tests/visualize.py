#!/usr/bin/env python3
"""
Simple visualization tool for migration_plan_graph.py
Generates a Mermaid diagram where each task is exactly one node.

Usage:
  python tools/visualize.py                  # Use default migration_plan_graph
  python tools/visualize.py --adaptive       # Use sample adaptive plan
Output: docs/migration_diagram.html (opens automatically in browser)
"""

import os
import sys
import webbrowser
from pathlib import Path

# Add project root to path to import migration_plan_graph
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Check for adaptive flag
if len(sys.argv) > 1 and sys.argv[1] == "--adaptive":
    from tools.sample_adaptive_plan import migration_plan_graph

    print("📚 Using sample adaptive plan to demonstrate audit/replanning...")
else:
    from tools.migration_plan_graph import migration_plan_graph


def escape_text(text: str) -> str:
    """Escape text for Mermaid/HTML display."""
    return text.replace('"', "'").replace("\n", " ").replace("(", "").replace(")", "")


def generate_mermaid_code() -> str:
    """Generate Mermaid diagram code from migration plan graph.
    Focus on clear dependencies and parallel groups."""
    lines = []
    lines.append("graph TD")
    lines.append("")

    # Style definitions - simplified without audit/replan
    lines.append("    %% Style definitions")
    lines.append("    classDef pre fill:#e1f5fe,stroke:#01579b,stroke-width:2px")
    lines.append("    classDef low fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px")
    lines.append("    classDef medium fill:#fff9c4,stroke:#f57f17,stroke-width:2px")
    lines.append("    classDef high fill:#ffccbc,stroke:#d84315,stroke-width:2px")
    lines.append("    classDef validation fill:#e8eaf6,stroke:#283593,stroke-width:2px")
    lines.append("    classDef critical stroke:#ff0000,stroke-width:3px")
    lines.append(
        "    classDef parallelGroup stroke:#9c27b0,stroke-width:3px,stroke-dasharray: 5 5"
    )
    lines.append("")

    all_tasks = {}
    critical_path = set(migration_plan_graph.get("critical_path", []))

    # Process pre-migration tasks
    lines.append("    %% Pre-migration tasks")
    for task in migration_plan_graph["migration_plan"]["pre_migration_tasks"]:
        task_id = task["id"]
        all_tasks[task_id] = task

        content = escape_text(task["content"][:40])
        hours = task.get("estimated_hours", 0)
        label = f"{task_id}\\n{content}...\\n{hours}h"

        lines.append(f'    {task_id}["{label}"]:::pre')
        if task_id in critical_path:
            lines.append(f"    class {task_id} critical")

    lines.append("")
    lines.append("    %% Migration tasks")

    # Process migration tasks
    for task in migration_plan_graph["migration_plan"]["migration_tasks"]:
        task_id = task["id"]
        all_tasks[task_id] = task

        content = escape_text(task["content"][:40])
        complexity = task.get("complexity", "medium")
        hours = task.get("estimated_hours", 0)
        audit = "🔒 " if task.get("audit_required", False) else ""
        label = f"{task_id}\\n{audit}{content}...\\n{hours}h"

        lines.append(f'    {task_id}["{label}"]:::{complexity}')
        if task_id in critical_path:
            lines.append(f"    class {task_id} critical")

    lines.append("")
    lines.append("    %% Validation tasks")

    # Process validation tasks
    for task in migration_plan_graph["migration_plan"].get("validation_tasks", []):
        task_id = task["id"]
        all_tasks[task_id] = task

        content = escape_text(task["content"][:40])
        continuous = " ♾️" if task.get("type") == "continuous" else ""
        label = f"{task_id}\\n{content}...{continuous}"

        lines.append(f'    {task_id}(("{label}")):::validation')
        if task_id in critical_path:
            lines.append(f"    class {task_id} critical")

    lines.append("")
    lines.append("    %% Dependencies")

    # Add dependencies
    for task_id, task in all_tasks.items():
        if "depends_on" in task:
            for dep_id in task["depends_on"]:
                if dep_id in all_tasks:
                    lines.append(f"    {dep_id} --> {task_id}")

        if "blocks" in task:
            for blocked_id in task["blocks"]:
                if blocked_id in all_tasks:
                    lines.append(f"    {task_id} --> {blocked_id}")

    return "\n".join(lines)


def generate_html(mermaid_code: str) -> str:
    """Generate HTML page with Mermaid diagram."""

    # Calculate stats - focus on core migration tasks only
    pre_tasks = len(
        migration_plan_graph["migration_plan"].get("pre_migration_tasks", [])
    )
    mig_tasks = len(migration_plan_graph["migration_plan"].get("migration_tasks", []))
    val_tasks = len(migration_plan_graph["migration_plan"].get("validation_tasks", []))
    total_tasks = pre_tasks + mig_tasks + val_tasks

    # Count parallel groups if present
    parallel_groups = len(migration_plan_graph.get("parallel_groups", []))

    # Count dependencies
    dep_count = 0
    for tasks in migration_plan_graph["migration_plan"].values():
        if isinstance(tasks, list):
            for task in tasks:
                if "depends_on" in task:
                    dep_count += len(task["depends_on"])
                if "blocks" in task:
                    dep_count += len(task["blocks"])

    # Count critical path
    critical_path_count = len(migration_plan_graph.get("critical_path", []))

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Migration Plan Visualization</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        h1 {{
            color: #333;
            margin-bottom: 10px;
        }}
        .stats {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }}
        .stat {{
            background: white;
            padding: 15px 25px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }}
        .stat-label {{
            color: #666;
            font-size: 14px;
            margin-top: 5px;
        }}
        .diagram-container {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: auto;
        }}
        .legend {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 30px;
            flex-wrap: wrap;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .color-box {{
            width: 20px;
            height: 20px;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Migration Plan Visualization</h1>
        <p style="color: #666;">Migration Plan - {total_tasks} Total Tasks</p>
        <p style="color: #999; font-size: 14px;">
            <strong>Focus:</strong> Clear dependencies and {parallel_groups} parallel execution groups
        </p>
    </div>
    
    <div class="stats">
        <div class="stat">
            <div class="stat-value">{pre_tasks}</div>
            <div class="stat-label">Pre-migration</div>
        </div>
        <div class="stat">
            <div class="stat-value">{mig_tasks}</div>
            <div class="stat-label">Migration</div>
        </div>
        <div class="stat">
            <div class="stat-value">{val_tasks}</div>
            <div class="stat-label">Validation</div>
        </div>
        <div class="stat" style="border: 2px solid #9c27b0;">
            <div class="stat-value">{parallel_groups}</div>
            <div class="stat-label">Parallel Groups</div>
        </div>
        <div class="stat">
            <div class="stat-value">{dep_count}</div>
            <div class="stat-label">Dependencies</div>
        </div>
        <div class="stat">
            <div class="stat-value">{critical_path_count}</div>
            <div class="stat-label">Critical Path</div>
        </div>
    </div>
    
    <div class="diagram-container">
        <div class="mermaid">
{mermaid_code}
        </div>
    </div>
    
    <div class="legend">
        <div class="legend-item">
            <div class="color-box" style="background: #e1f5fe; border: 2px solid #01579b;"></div>
            <span>Pre-migration</span>
        </div>
        <div class="legend-item">
            <div class="color-box" style="background: #c8e6c9; border: 2px solid #2e7d32;"></div>
            <span>Low Complexity</span>
        </div>
        <div class="legend-item">
            <div class="color-box" style="background: #fff9c4; border: 2px solid #f57f17;"></div>
            <span>Medium Complexity</span>
        </div>
        <div class="legend-item">
            <div class="color-box" style="background: #ffccbc; border: 2px solid #d84315;"></div>
            <span>High Complexity</span>
        </div>
        <div class="legend-item">
            <div class="color-box" style="background: #e8eaf6; border: 2px solid #283593;"></div>
            <span>Validation</span>
        </div>
        <div class="legend-item">
            <div class="color-box" style="background: white; border: 3px solid #ff0000;"></div>
            <span>Critical Path</span>
        </div>
        <div class="legend-item">
            <span>♾️ Continuous Validation</span>
        </div>
    </div>
    
    <script>
        mermaid.initialize({{ 
            startOnLoad: true,
            theme: 'default',
            flowchart: {{
                useMaxWidth: true,
                htmlLabels: true,
                curve: 'basis'
            }}
        }});
    </script>
</body>
</html>"""

    return html


def main():
    """Generate visualization and open in browser."""
    print("🚀 Generating migration plan visualization...")

    # Generate Mermaid code
    mermaid_code = generate_mermaid_code()

    # Generate HTML
    html_content = generate_html(mermaid_code)

    # Ensure docs directory exists
    docs_dir = PROJECT_ROOT / "docs"
    docs_dir.mkdir(exist_ok=True)

    # Save HTML file
    output_file = docs_dir / "migration_diagram.html"
    with open(output_file, "w") as f:
        f.write(html_content)

    print(f"✅ Visualization saved to: docs/migration_diagram.html")

    # Open in browser
    file_url = f"file://{output_file.absolute()}"
    webbrowser.open(file_url)
    print("📊 Opening in browser...")

    # Print stats - focus on core migration tasks
    pre_count = len(
        migration_plan_graph["migration_plan"].get("pre_migration_tasks", [])
    )
    mig_count = len(migration_plan_graph["migration_plan"].get("migration_tasks", []))
    val_count = len(migration_plan_graph["migration_plan"].get("validation_tasks", []))
    parallel_count = len(migration_plan_graph.get("parallel_groups", []))

    print(f"\nStats:")
    print(f"  • Pre-migration tasks: {pre_count}")
    print(f"  • Migration tasks: {mig_count}")
    print(f"  • Validation tasks: {val_count}")
    print(f"  • Parallel groups: {parallel_count}")
    print(f"  • Total: {pre_count + mig_count + val_count} tasks")

    # Note about audit/replanning being handled separately
    if (
        "audit_tasks" in migration_plan_graph["migration_plan"]
        or "replanning_tasks" in migration_plan_graph["migration_plan"]
    ):
        audit_count = len(migration_plan_graph["migration_plan"].get("audit_tasks", []))
        replan_count = len(
            migration_plan_graph["migration_plan"].get("replanning_tasks", [])
        )
        if audit_count > 0 or replan_count > 0:
            print(
                f"\n  Note: {audit_count} audit and {replan_count} replanning tasks are in the data"
            )
            print(f"        but not visualized - they're inferred from parallel groups")


if __name__ == "__main__":
    main()
