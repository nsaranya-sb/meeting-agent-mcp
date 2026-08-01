"""
Real Jira REST API integration client using Atlassian REST API v3.
"""
from typing import Dict, Any
from datetime import datetime, timezone
import httpx
from integrations.base import JiraIntegrationBase
from config import Config, config as global_config


class JiraRealIntegration(JiraIntegrationBase):
    def __init__(self, cfg: Config = global_config):
        self.cfg = cfg
        self.cfg.validate_for_jira_real()

    def create_ticket(self, title: str, description: str, priority: str = "Medium") -> Dict[str, Any]:
        url = f"{self.cfg.jira_url}/rest/api/3/issue"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        auth = (self.cfg.jira_email, self.cfg.jira_api_token)

        payload = {
            "fields": {
                "project": {"key": self.cfg.jira_project_key},
                "summary": title,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"type": "text", "text": description}],
                        }
                    ],
                },
                "issuetype": {"name": "Task"},
            }
        }
        if priority:
            payload["fields"]["priority"] = {"name": priority}

        with httpx.Client(timeout=15.0) as client:
            response = client.post(url, json=payload, headers=headers, auth=auth)
            # If priority scheme rejected, retry without explicit priority
            if response.status_code == 400 and "priority" in response.text.lower():
                payload["fields"].pop("priority", None)
                response = client.post(url, json=payload, headers=headers, auth=auth)

            response.raise_for_status()
            data = response.json()

            ticket_key = data.get("key", data.get("id", "JIRA-CREATED"))
            return {
                "id": ticket_key,
                "title": title,
                "description": description,
                "priority": priority,
                "status": "To Do",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "jira_url": f"{self.cfg.jira_url}/browse/{ticket_key}",
            }
