"""
Mock Slack integration implementing SlackIntegrationBase, backed by mock_store.py.
"""
from typing import Dict, Any
from integrations.base import SlackIntegrationBase
import mock_store


class SlackMockIntegration(SlackIntegrationBase):
    def post_summary(self, channel: str, summary: str) -> Dict[str, Any]:
        return mock_store.post_slack_summary(channel, summary)
