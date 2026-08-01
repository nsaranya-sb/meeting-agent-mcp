"""
Mock Calendar integration implementing CalendarIntegrationBase, backed by mock_store.py.
"""
from typing import Dict, Any
from integrations.base import CalendarIntegrationBase
import mock_store


class CalendarMockIntegration(CalendarIntegrationBase):
    def schedule_followup(self, title: str, days_from_now: int = 3) -> Dict[str, Any]:
        return mock_store.schedule_followup(title, days_from_now)
