# Tools & Utilities

This directory contains standalone tools and utilities for the migration orchestration project.

## Files

### 📁 migration_plan_graph.py
The data source containing the complete migration plan structure with:
- 37 total tasks (7 pre-migration, 24 migration, 6 validation)
- Task dependencies and relationships
- Complexity ratings and time estimates
- Critical path definitions
- Parallel execution groups

### 📊 visualize.py
Generates an interactive Mermaid diagram visualization of the migration plan.

**Usage:**
```bash
# From project root
python tools/visualize.py
```

**Output:**
- Creates `docs/migration_diagram.html`
- Automatically opens in your browser
- Shows all 37 migration tasks as nodes with dependencies

**Features:**
- Color-coded by complexity (green=low, yellow=medium, orange=high)
- Blue nodes for pre-migration tasks
- Purple nodes for validation tasks
- Red borders indicate critical path
- 🔒 symbol shows tasks requiring audit
