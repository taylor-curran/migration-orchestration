#!/usr/bin/env python3
"""
Migration Plan Visualization Tool v2
Generates interactive Mermaid diagram with automatic parallel detection.
Works with simplified task structure from new prompt.

Usage:
  python tools/visualize_v2.py                      # Use default migration_plan_graph
  python tools/visualize_v2.py path/to/plan.py      # Use specific plan file
Output: docs/migration_diagram.html (opens automatically in browser)
"""

import os
import sys
import json
import webbrowser
import argparse
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.parallel_detector import ParallelDetector, analyze_tasks


def load_migration_plan(file_path: str = None) -> Dict[str, Any]:
    """Load migration plan from specified file or default location."""
    if file_path:
        plan_path = Path(file_path)
    else:
        # Try default location
        plan_path = PROJECT_ROOT / "tools" / "migration_plan_graph.py"

    if not plan_path.exists():
        # Try to find migration_plan.py in common locations
        alternatives = [
            PROJECT_ROOT / "migration_plan.py",
            PROJECT_ROOT.parent / "target-springboot-cics" / "migration_plan.py",
        ]
        for alt in alternatives:
            if alt.exists():
                plan_path = alt
                break
        else:
            print(f"❌ Could not find migration plan at {plan_path}")
            print("   Tried alternatives:", [str(a) for a in alternatives])
            return None

    print(f"📖 Loading migration plan from: {plan_path}")

    # Import the module
    import importlib.util

    spec = importlib.util.spec_from_file_location("migration_plan", plan_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Get the migration_plan variable
    if hasattr(module, "migration_plan"):
        return module.migration_plan
    elif hasattr(module, "migration_plan_graph"):
        return module.migration_plan_graph
    else:
        # Fallback to alternative locations if default file lacks required variables
        alternatives = [
            PROJECT_ROOT / "migration_plan.py",
            PROJECT_ROOT.parent / "target-springboot-cics" / "migration_plan.py",
        ]
        for alt in alternatives:
            if alt.exists():
                print(f"🔍 Default plan missing variables, trying alternative: {alt}")
                spec_alt = importlib.util.spec_from_file_location(
                    "migration_plan_alt", alt
                )
                module_alt = importlib.util.module_from_spec(spec_alt)
                spec_alt.loader.exec_module(module_alt)
                if hasattr(module_alt, "migration_plan"):
                    return module_alt.migration_plan
                if hasattr(module_alt, "migration_plan_graph"):
                    return module_alt.migration_plan_graph
        print("❌ Could not find a valid migration plan in default or alternatives")
        return None


def infer_task_category(task: Dict[str, Any]) -> str:
    """Infer task category from ID or content."""
    task_id = task.get("id", "").lower()

    if "setup" in task_id or "pre_" in task_id:
        return "setup"
    elif "validator" in task_id or "valid" in task_id:
        return "validator"
    elif "migrate" in task_id or "mig_" in task_id:
        return "migration"
    else:
        return "other"


def escape_text(text: str, max_len: int = 60) -> str:
    """Escape text for Mermaid/HTML display with better formatting."""
    # Clean up the text
    text = text.replace('"', "'").replace("\n", " ").replace("\r", " ")
    text = text.replace("(", "[").replace(")", "]")
    
    # Truncate if needed
    if len(text) > max_len:
        text = text[:max_len-3] + "..."
    
    return text


def generate_mermaid_code(tasks: List[Dict[str, Any]], analysis: Dict[str, Any]) -> str:
    """Generate Mermaid diagram with parallel group visualization."""
    lines = []
    lines.append("%%{init: {'theme':'default', 'themeVariables': { 'fontSize': '16px'}}}%%")
    lines.append("graph TB")
    lines.append("")

    # Style definitions with better colors and readability
    lines.append("    %% Style definitions")
    lines.append("    classDef setup fill:#e1f5fe,stroke:#0277bd,stroke-width:2px,color:#000")
    lines.append("    classDef validator fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000")
    lines.append("    classDef migration fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000")
    lines.append("    classDef other fill:#fff9c4,stroke:#f57c00,stroke-width:2px,color:#000")  
    lines.append("    classDef critical stroke:#c62828,stroke-width:4px")
    lines.append(
        "    classDef parallel stroke:#ad1457,stroke-width:3px,stroke-dasharray: 5 5"
    )
    lines.append("")

    # Track which tasks are in parallel groups
    tasks_in_parallel = set()
    for group in analysis.get("parallel_groups_detail", []):
        tasks_in_parallel.update(group["tasks"])

    # Track critical path
    critical_path = set(analysis.get("critical_path", []))

    # Add task nodes with clean, simple formatting
    lines.append("    %% Task nodes")
    for task in tasks:
        task_id = task["id"]
        title = task.get("title", task.get("content", "Task"))
        hours = task.get("estimated_hours", 8)
        category = infer_task_category(task)
        status = task.get("status", "not-complete")
        
        # Clean title - remove special chars and truncate if needed
        clean_title = title.replace('"', "'").replace("\n", " ")
        if len(clean_title) > 40:
            # Find a good break point
            words = clean_title.split()
            line1 = ""
            line2 = ""
            
            for word in words:
                if len(line1) < 25:
                    line1 = (line1 + " " + word).strip()
                else:
                    line2 = (line2 + " " + word).strip()
            
            if line2:
                if len(line2) > 25:
                    line2 = line2[:22] + "..."
                clean_title = line1 + "\n" + line2
            else:
                clean_title = line1[:37] + "..."
        
        # Build simple label using line breaks that Mermaid understands
        if status == "complete":
            label = f"{task_id.upper()}\n{clean_title}\n({hours}h) ✓"
        else:
            label = f"{task_id.upper()}\n{clean_title}\n({hours}h)"
        
        # Use simpler node syntax for better compatibility
        if category == "validator":
            # Hexagon for validators
            node = f'{task_id}{{{{"{label}"}}}}:::validator'
        elif category == "setup":
            # Stadium shape for setup  
            node = f'{task_id}(["{label}"]):::setup'
        elif category == "migration":
            # Rectangle for migration
            node = f'{task_id}["{label}"]:::migration'
        else:
            # Round edges for other
            node = f'{task_id}("{label}"):::other'
        
        lines.append(f"    {node}")

        # Add critical path styling
        if task_id in critical_path:
            lines.append(f"    class {task_id} critical")

        # Add parallel group styling
        if task_id in tasks_in_parallel:
            lines.append(f"    class {task_id} parallel")

    lines.append("")
    lines.append("    %% Dependencies")

    # Add dependency arrows
    for task in tasks:
        task_id = task["id"]
        for dep_id in task.get("depends_on", []):
            lines.append(f"    {dep_id} --> {task_id}")

    lines.append("")
    lines.append("    %% Parallel group annotations")

    # Add subgraphs for parallel groups
    for i, group in enumerate(analysis.get("parallel_groups_detail", [])):
        if len(group["tasks"]) > 1:
            lines.append(
                f"    subgraph parallel_group_{i}[Parallel Group - Level {group['level']}]"
            )
            lines.append(f"        direction LR")
            for task_id in group["tasks"]:
                lines.append(f"        {task_id}")
            lines.append("    end")
            lines.append(
                f"    style parallel_group_{i} fill:#fce4ec,stroke:#c2185b,stroke-width:2px,stroke-dasharray: 5 5"
            )

    return "\n".join(lines)


def generate_html(tasks: List[Dict[str, Any]], analysis: Dict[str, Any]) -> str:
    """Generate HTML page with visualization and statistics."""

    mermaid_code = generate_mermaid_code(tasks, analysis)

    # Task counts by category
    categories = {"setup": 0, "validator": 0, "migration": 0, "other": 0}
    for task in tasks:
        category = infer_task_category(task)
        categories[category] += 1

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Migration Plan Visualization v2</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1800px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            color: white;
        }}
        h1 {{
            margin-bottom: 10px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        .subtitle {{
            opacity: 0.95;
            font-size: 1.1em;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        .stat {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.2s;
        }}
        .stat:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }}
        .stat-value {{
            font-size: 28px;
            font-weight: bold;
            color: #333;
            display: block;
        }}
        .stat-label {{
            color: #666;
            font-size: 13px;
            margin-top: 5px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .stat.highlight {{
            background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%);
            color: white;
        }}
        .stat.highlight .stat-value {{
            color: white;
        }}
        .stat.highlight .stat-label {{
            color: rgba(255,255,255,0.9);
        }}
        .diagram-container {{
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: auto;
            margin-bottom: 30px;
            min-height: 800px;
        }}
        .efficiency {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        .efficiency h2 {{
            margin-top: 0;
            color: #333;
        }}
        .progress-bar {{
            background: #e0e0e0;
            border-radius: 10px;
            height: 30px;
            overflow: hidden;
            margin: 15px 0;
        }}
        .progress-fill {{
            background: linear-gradient(90deg, #667eea, #764ba2);
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            transition: width 1s ease;
        }}
        .legend {{
            display: flex;
            justify-content: center;
            gap: 25px;
            margin-top: 20px;
            flex-wrap: wrap;
            padding: 20px;
            background: white;
            border-radius: 12px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .color-box {{
            width: 24px;
            height: 24px;
            border-radius: 4px;
        }}
        .critical-path {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 30px;
        }}
        .critical-path h3 {{
            margin-top: 0;
            color: #d32f2f;
        }}
        .path-step {{
            display: inline-block;
            padding: 5px 10px;
            margin: 3px;
            background: #ffebee;
            border: 1px solid #d32f2f;
            border-radius: 4px;
            color: #d32f2f;
            font-weight: 500;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Migration Plan Visualization</h1>
            <p class="subtitle">Automatic Parallel Execution Detection</p>
        </div>
        
        <div class="stats">
            <div class="stat">
                <span class="stat-value">{analysis["total_tasks"]}</span>
                <div class="stat-label">Total Tasks</div>
            </div>
            <div class="stat">
                <span class="stat-value">{categories["setup"]}</span>
                <div class="stat-label">Setup Tasks</div>
            </div>
            <div class="stat">
                <span class="stat-value">{categories["validator"]}</span>
                <div class="stat-label">Validators</div>
            </div>
            <div class="stat">
                <span class="stat-value">{categories["migration"]}</span>
                <div class="stat-label">Migrations</div>
            </div>
            <div class="stat highlight">
                <span class="stat-value">{analysis["parallel_groups"]}</span>
                <div class="stat-label">Parallel Groups</div>
            </div>
            <div class="stat highlight">
                <span class="stat-value">{analysis["max_parallelism"]}</span>
                <div class="stat-label">Max Parallelism</div>
            </div>
            <div class="stat">
                <span class="stat-value">{analysis["critical_path_length"]}</span>
                <div class="stat-label">Critical Path</div>
            </div>
        </div>
        
        <div class="efficiency">
            <h2>⚡ Efficiency Analysis</h2>
            <p><strong>Serial Execution:</strong> {analysis["total_duration_serial"]} hours</p>
            <p><strong>Parallel Execution:</strong> {analysis["total_duration_parallel"]} hours</p>
            <p><strong>Time Saved:</strong> {analysis["time_saved"]} hours ({analysis["efficiency_gain"]}% faster)</p>
            
            <div class="progress-bar">
                <div class="progress-fill" style="width: {min(analysis["efficiency_gain"], 100)}%">
                    {analysis["efficiency_gain"]}% Efficiency Gain
                </div>
            </div>
        </div>
        
        <div class="critical-path">
            <h3>🔴 Critical Path ({analysis["critical_path_duration"]} hours)</h3>
            <div>
                {" → ".join(f'<span class="path-step">{task_id}</span>' for task_id in analysis["critical_path"])}
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
                <span>Setup Tasks</span>
            </div>
            <div class="legend-item">
                <div class="color-box" style="background: #f0e7ff; border: 2px solid #6a1b9a;"></div>
                <span>Validators</span>
            </div>
            <div class="legend-item">
                <div class="color-box" style="background: #c8e6c9; border: 2px solid #2e7d32;"></div>
                <span>Migration Tasks</span>
            </div>
            <div class="legend-item">
                <div class="color-box" style="background: #fce4ec; border: 3px dashed #c2185b;"></div>
                <span>Can Run in Parallel</span>
            </div>
            <div class="legend-item">
                <div class="color-box" style="background: white; border: 4px solid #ff0000;"></div>
                <span>Critical Path</span>
            </div>
        </div>
    </div>
    
    <script>
        mermaid.initialize({{ 
            startOnLoad: true,
            theme: 'default',
            flowchart: {{
                useMaxWidth: true,
                htmlLabels: false,
                curve: 'basis',
                padding: 20,
                nodeSpacing: 80,
                rankSpacing: 80
            }}
        }});
    </script>
</body>
</html>"""

    return html


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Visualize migration plan with parallel detection"
    )
    parser.add_argument("file", nargs="?", help="Path to migration plan file")
    parser.add_argument(
        "--no-browser", action="store_true", help="Don't open in browser"
    )
    args = parser.parse_args()

    # Load migration plan
    migration_plan = load_migration_plan(args.file)
    if not migration_plan:
        return 1

    # Extract tasks - handle both old and new structure
    if "tasks" in migration_plan:
        # New simplified structure
        tasks = migration_plan["tasks"]
    elif "migration_plan" in migration_plan:
        # Old nested structure - flatten it
        tasks = []
        for category in ["pre_migration_tasks", "migration_tasks", "validation_tasks"]:
            if category in migration_plan["migration_plan"]:
                tasks.extend(migration_plan["migration_plan"][category])
    else:
        print("❌ Unknown migration plan structure")
        return 1

    print(f"📊 Analyzing {len(tasks)} tasks...")

    # Analyze with parallel detector
    analysis = analyze_tasks(tasks)

    # Generate HTML
    html_content = generate_html(tasks, analysis)

    # Save to file
    docs_dir = PROJECT_ROOT / "docs"
    docs_dir.mkdir(exist_ok=True)

    output_file = docs_dir / "migration_diagram.html"
    with open(output_file, "w") as f:
        f.write(html_content)

    print(f"✅ Visualization saved to: {output_file}")

    # Print analysis summary
    print("\n📈 Parallelization Analysis:")
    print(f"  • Total tasks: {analysis['total_tasks']}")
    print(f"  • Parallel groups detected: {analysis['parallel_groups']}")
    print(f"  • Maximum parallelism: {analysis['max_parallelism']} tasks")
    print(f"  • Serial execution time: {analysis['total_duration_serial']} hours")
    print(f"  • Parallel execution time: {analysis['total_duration_parallel']} hours")
    print(
        f"  • Time saved: {analysis['time_saved']} hours ({analysis['efficiency_gain']}%)"
    )

    if analysis["parallel_groups_detail"]:
        print("\n🔀 Parallel Groups:")
        for group in analysis["parallel_groups_detail"]:
            print(
                f"  Level {group['level']}: {', '.join(group['tasks'])} ({group['size']} tasks)"
            )

    # Open in browser unless disabled
    if not args.no_browser:
        file_url = f"file://{output_file.absolute()}"
        webbrowser.open(file_url)
        print("\n🌐 Opening in browser...")

    return 0


if __name__ == "__main__":
    sys.exit(main())
