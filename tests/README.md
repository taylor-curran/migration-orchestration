# Test Suite for Migration Orchestration

## Test Structure

```
tests/
├── __init__.py                     # Test package marker
├── conftest.py                     # Shared pytest fixtures
├── tasks/                          # Tests for task modules
│   ├── __init__.py
│   └── test_run_sessions.py       # Tests for run_sessions module
└── utils/                          # Tests for utility modules (to be added)
```

## Running Tests

### Install Test Dependencies
```bash
source .venv/bin/activate
uv pip install -r requirements-dev.txt
```

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test File
```bash
pytest tests/tasks/test_run_sessions.py
```

### Run Specific Test
```bash
pytest tests/tasks/test_run_sessions.py::test_run_session_without_structured_output
```

### Run with Verbose Output
```bash
pytest tests/ -v
```

### Run with Coverage
```bash
pytest tests/ --cov=src --cov-report=term-missing
```

## Test Coverage

Currently testing:
- ✅ `run_session_and_wait_for_analysis` without structured output
- ✅ API error handling during session creation

To be added:
- Tests for structured output scenarios
- Tests for utility functions
- Tests for orchestration flow
