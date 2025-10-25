"""
Tests for run_sessions.py module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from tasks.run_sessions import (
    run_session_and_wait_for_analysis,
    run_session_until_blocked,
    generate_analysis,
)


@pytest.fixture
def mock_api_key():
    """Fixture for API key."""
    return "test-api-key-123"


@pytest.fixture
def mock_session_response():
    """Mock response for creating a session."""
    return {
        "session_id": "devin-test-session-123",
        "url": "https://app.devin.ai/sessions/test-session-123",
    }


@pytest.fixture
def mock_session_status_blocked():
    """Mock session status response when blocked."""
    return {"status_enum": "blocked", "session_id": "devin-test-session-123"}


@pytest.fixture
def mock_session_status_finished():
    """Mock session status response when finished (sleeping)."""
    return {"status_enum": "finished", "session_id": "devin-test-session-123"}


@pytest.fixture
def mock_session_status_planning():
    """Mock session status response when planning."""
    return {"status_enum": "planning", "session_id": "devin-test-session-123"}


@pytest.fixture
def mock_session_status_working():
    """Mock session status response when working."""
    return {"status_enum": "working", "session_id": "devin-test-session-123"}


@pytest.fixture
def mock_analysis_response():
    """Mock analysis response."""
    return {
        "session_analysis": {
            "issues": [],
            "action_items": ["Review the implementation"],
            "timeline": [
                {"event": "Session started", "timestamp": "2024-01-01T00:00:00Z"},
                {"event": "Task completed", "timestamp": "2024-01-01T00:05:00Z"},
            ],
            "suggested_prompt": {
                "suggested_prompt": "Improved prompt for better results",
                "original_prompt": "Original prompt",
            },
        }
    }


@patch("tasks.run_sessions.httpx.Client")
@patch("tasks.run_sessions.create_session_link_artifact")
def test_run_session_until_blocked(
    mock_link_artifact,
    mock_httpx_client,
    mock_api_key,
    mock_session_response,
    mock_session_status_blocked,
):
    """Test run_session_until_blocked task - Phase 1 of orchestration."""

    # Setup mock client
    mock_client = MagicMock()
    mock_httpx_client.return_value.__enter__.return_value = mock_client

    # 1. Create session response
    create_response = Mock()
    create_response.json.return_value = mock_session_response
    create_response.raise_for_status = Mock()

    # 2. Status check - returns blocked (simulating immediate blocked status)
    status_response = Mock()
    status_response.json.return_value = mock_session_status_blocked
    status_response.raise_for_status = Mock()

    # Configure mock client
    mock_client.post.return_value = create_response
    mock_client.get.return_value = status_response

    # Run the function
    result = run_session_until_blocked(
        prompt="Test prompt for Devin", title="Test Session", api_key=mock_api_key
    )

    # Assertions
    assert result is not None
    assert result["session_id"] == "devin-test-session-123"
    assert result["session_url"] == "https://app.devin.ai/sessions/test-session-123"
    assert result["status"] == "blocked"
    assert result["api_key"] == mock_api_key
    assert result["has_schema"] is False
    assert "execution_time" in result

    # Verify API calls
    assert mock_client.post.call_count == 1  # Create session
    assert mock_client.get.call_count == 1  # Status check

    # Verify artifact was created
    mock_link_artifact.assert_called_once()


@patch("tasks.run_sessions.httpx.Client")
@patch("tasks.run_sessions.create_timeline_artifact")
@patch("tasks.run_sessions.create_improvements_artifact")
@patch("tasks.run_sessions.create_orchestration_summary_artifact")
def test_generate_analysis(
    mock_summary_artifact,
    mock_improvements_artifact,
    mock_timeline_artifact,
    mock_httpx_client,
    mock_session_status_finished,
    mock_analysis_response,
):
    """Test generate_analysis task - Phase 2 of orchestration."""

    # Setup mock client
    mock_client = MagicMock()
    mock_httpx_client.return_value.__enter__.return_value = mock_client

    # Setup responses
    # 1. Sleep message response
    sleep_response = Mock()
    sleep_response.raise_for_status = Mock()

    # 2. Status check - returns finished (sleeping)
    status_response = Mock()
    status_response.json.return_value = mock_session_status_finished
    status_response.raise_for_status = Mock()

    # 3. Analysis check - returns analysis
    analysis_response = Mock()
    analysis_response.json.return_value = mock_analysis_response
    analysis_response.raise_for_status = Mock()

    # Configure mock client
    responses = [sleep_response, status_response, analysis_response]
    response_iterator = iter(responses)

    def side_effect(*args, **kwargs):
        return next(response_iterator)

    mock_client.post.side_effect = side_effect
    mock_client.get.side_effect = side_effect

    # Input from previous task
    session_info = {
        "session_id": "devin-test-session-123",
        "session_url": "https://app.devin.ai/sessions/test-session-123",
        "status": "blocked",
        "api_key": "test-api-key-123",
        "poll_interval": 10,
        "has_schema": False,
        "title": "Test Session",
        "execution_time": 60.0,
    }

    # Run the function
    result = generate_analysis(session_info)

    # Assertions
    assert result is not None
    assert result["session_id"] == "devin-test-session-123"
    assert result["session_url"] == "https://app.devin.ai/sessions/test-session-123"
    assert result["analysis"] == mock_analysis_response["session_analysis"]
    assert result["suggested_prompt"] == "Improved prompt for better results"
    assert result["structured_output"] is None  # No schema provided

    # Verify API calls
    assert mock_client.post.call_count == 1  # Send sleep
    assert mock_client.get.call_count == 2  # Status check + analysis

    # Verify artifacts were created
    mock_timeline_artifact.assert_called_once()
    mock_improvements_artifact.assert_called_once()
    mock_summary_artifact.assert_called_once()


@patch("tasks.run_sessions.run_session_until_blocked")
@patch("tasks.run_sessions.generate_analysis")
def test_run_session_and_wait_for_analysis_orchestration(
    mock_generate_analysis, mock_run_until_blocked, mock_api_key
):
    """Test the full orchestration with both tasks."""

    # Mock the output from Phase 1
    session_info = {
        "session_id": "devin-test-session-123",
        "session_url": "https://app.devin.ai/sessions/test-session-123",
        "status": "blocked",
        "api_key": mock_api_key,
        "poll_interval": 10,
        "has_schema": False,
        "title": "Test Session",
        "execution_time": 60.0,
    }
    mock_run_until_blocked.return_value = session_info

    # Mock the output from Phase 2
    analysis_result = {
        "session_id": "devin-test-session-123",
        "session_url": "https://app.devin.ai/sessions/test-session-123",
        "analysis": {"issues": [], "action_items": ["Review"]},
        "suggested_prompt": "Improved prompt",
        "structured_output": None,
        "execution_time": 30.0,
    }
    mock_generate_analysis.return_value = analysis_result

    # Run the orchestration
    result = run_session_and_wait_for_analysis(
        prompt="Test prompt", title="Test Session", api_key=mock_api_key
    )

    # Verify Phase 1 was called correctly
    mock_run_until_blocked.assert_called_once_with(
        prompt="Test prompt",
        title="Test Session",
        api_key=mock_api_key,
        poll_interval=10,
        structured_output_schema=None,
    )

    # Verify Phase 2 was called with output from Phase 1
    mock_generate_analysis.assert_called_once_with(session_info)

    # Verify final result is from Phase 2
    assert result == analysis_result


@patch("tasks.run_sessions.httpx.Client")
@patch("tasks.run_sessions.create_session_link_artifact")
def test_run_session_with_status_transitions(
    mock_link_artifact,
    mock_httpx_client,
    mock_api_key,
    mock_session_response,
    mock_session_status_planning,
    mock_session_status_working,
    mock_session_status_blocked,
):
    """Test run_session_until_blocked with status transitions (planning -> working -> blocked)."""

    # Setup mock client
    mock_client = MagicMock()
    mock_httpx_client.return_value.__enter__.return_value = mock_client

    # 1. Create session response
    create_response = Mock()
    create_response.json.return_value = mock_session_response
    create_response.raise_for_status = Mock()

    # 2. Status checks - simulate transition from planning -> working -> blocked
    planning_response = Mock()
    planning_response.json.return_value = mock_session_status_planning
    planning_response.raise_for_status = Mock()

    working_response = Mock()
    working_response.json.return_value = mock_session_status_working
    working_response.raise_for_status = Mock()

    blocked_response = Mock()
    blocked_response.json.return_value = mock_session_status_blocked
    blocked_response.raise_for_status = Mock()

    # Configure mock client to return different statuses in sequence
    mock_client.post.return_value = create_response
    mock_client.get.side_effect = [
        planning_response,  # First check: planning
        working_response,  # Second check: working
        blocked_response,  # Third check: blocked
    ]

    # Run the function
    result = run_session_until_blocked(
        prompt="Test prompt with transitions",
        title="Test Session Transitions",
        api_key=mock_api_key,
    )

    # Assertions
    assert result is not None
    assert result["status"] == "blocked"
    assert mock_client.get.call_count == 3  # Three status checks

    # Verify we saw all transitions
    mock_link_artifact.assert_called_once()


@patch("tasks.run_sessions.httpx.Client")
def test_run_session_api_error(mock_httpx_client, mock_api_key):
    """Test handling of API errors during session creation."""

    # Setup mock client to raise an error
    mock_client = MagicMock()
    mock_httpx_client.return_value.__enter__.return_value = mock_client

    error_response = Mock()
    error_response.raise_for_status.side_effect = Exception(
        "API Error: 401 Unauthorized"
    )
    mock_client.post.return_value = error_response

    # Run the function and expect an error
    with pytest.raises(Exception) as exc_info:
        run_session_until_blocked(
            prompt="Test prompt", title="Test Session", api_key=mock_api_key
        )

    assert "401 Unauthorized" in str(exc_info.value)
