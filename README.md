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

## Testing

### Setup
Install test dependencies:
```bash
source .venv/bin/activate
uv pip install -r requirements-dev.txt
```

### Running Tests
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/tasks/test_run_sessions.py

# Run specific test
pytest tests/tasks/test_run_sessions.py::test_run_session_without_structured_output
```

### Code Coverage
```bash
# Run tests with coverage report
pytest --cov=src --cov-report=term-missing

# Coverage for specific module
pytest --cov=src/tasks/run_sessions --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

### Test Structure
```
tests/
├── conftest.py                     # Shared fixtures
├── tasks/
│   └── test_run_sessions.py       # Tests for run_sessions module
└── utils/                          # Tests for utility modules
```

All tests use mocks to avoid making real API calls, ensuring fast and reliable test execution.