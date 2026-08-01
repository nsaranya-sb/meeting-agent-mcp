"""
Mock Jira integration implementing JiraIntegrationBase, backed by mock_store.py.
"""
from typing import Dict, Any
from integrations.base import JiraIntegrationBase
import mock_store


class JiraMockIntegration(JiraIntegrationBase):
    def create_ticket(self, title: str, description: str, priority: str = "Medium") -> Dict[str, Any]:
        return mock_store.create_ticket(title, description, priority)
