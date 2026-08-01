"""
Abstract integration interfaces for After-Meeting Agent services.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class JiraIntegrationBase(ABC):
    @abstractmethod
    def create_ticket(self, title: str, description: str, priority: str = "Medium") -> Dict[str, Any]:
        """
        Create a Jira ticket.
        Returns ticket dictionary containing at least 'id', 'title', 'description', 'priority', 'status'.
        """
        pass


class SlackIntegrationBase(ABC):
    @abstractmethod
    def post_summary(self, channel: str, summary: str) -> Dict[str, Any]:
        """
        Post a summary to Slack.
        Returns dictionary with post details.
        """
        pass


class CalendarIntegrationBase(ABC):
    @abstractmethod
    def schedule_followup(self, title: str, days_from_now: int = 3) -> Dict[str, Any]:
        """
        Schedule a follow-up calendar event.
        Returns dictionary with event details.
        """
        pass
