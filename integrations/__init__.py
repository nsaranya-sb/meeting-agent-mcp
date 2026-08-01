"""
Integrations package for After-Meeting Agent.
"""
from integrations.base import (
    JiraIntegrationBase,
    SlackIntegrationBase,
    CalendarIntegrationBase,
)
from integrations.jira_real import JiraRealIntegration
from integrations.jira_mock import JiraMockIntegration
from integrations.slack_mock import SlackMockIntegration
from integrations.calendar_mock import CalendarMockIntegration

__all__ = [
    "JiraIntegrationBase",
    "SlackIntegrationBase",
    "CalendarIntegrationBase",
    "JiraRealIntegration",
    "JiraMockIntegration",
    "SlackMockIntegration",
    "CalendarMockIntegration",
]
