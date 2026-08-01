"""
Unit tests for JiraRealIntegration HTTP client payload construction and auth.
Uses HTTP mocking so tests pass without live credentials.
"""
import pytest
from unittest.mock import MagicMock, patch
import httpx

from config import Config
from integrations.jira_real import JiraRealIntegration


def test_jira_real_validation_failure():
    invalid_cfg = Config(
        jira_url="",
        jira_email="",
        jira_api_token="",
        jira_project_key="AICOE",
        jira_mode="real",
    )
    with pytest.raises(ValueError) as exc_info:
        JiraRealIntegration(invalid_cfg)
    assert "JIRA_URL" in str(exc_info.value)


@patch("httpx.Client.post")
def test_jira_real_create_ticket_success(mock_post):
    # Setup mock HTTP response from Jira REST API v3
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {
        "id": "10001",
        "key": "AICOE-999",
        "self": "https://example.atlassian.net/rest/api/3/issue/10001",
    }
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    test_cfg = Config(
        jira_url="https://example.atlassian.net",
        jira_email="user@example.com",
        jira_api_token="test_token_123",
        jira_project_key="AICOE",
        jira_mode="real",
    )

    integration = JiraRealIntegration(test_cfg)
    result = integration.create_ticket(
        title="Fix UER Data Mapping",
        description="Spreadsheet shifted columns breaking macro",
        priority="High",
    )

    # Verify HTTP POST call details
    assert mock_post.called
    call_kwargs = mock_post.call_args.kwargs
    assert call_kwargs["auth"] == ("user@example.com", "test_token_123")

    payload = call_kwargs["json"]
    assert payload["fields"]["project"]["key"] == "AICOE"
    assert payload["fields"]["summary"] == "Fix UER Data Mapping"
    assert payload["fields"]["priority"]["name"] == "High"

    # Verify return payload
    assert result["id"] == "AICOE-999"
    assert result["jira_url"] == "https://example.atlassian.net/browse/AICOE-999"
