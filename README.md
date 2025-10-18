# migration-orchestration

Orchestrate Devin API sessions with automated workflow management and session analysis retrieval.

## Virtual Environment Setup

```bash
# Create virtual environment with uv
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

## Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Add your Devin API key to `.env`:
   ```
   DEVIN_API_KEY=your_actual_api_key
   ```