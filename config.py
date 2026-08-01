"""
Configuration management for After-Meeting Agent MCP Server.
Loads settings from environment variables and .env file.
"""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    jira_url: str
    jira_email: str
    jira_api_token: str
    jira_project_key: str
    jira_mode: str  # 'real' or 'mock'

    @classmethod
    def load(cls) -> "Config":
        mode = os.getenv("JIRA_MODE", "mock").lower()
        return cls(
            jira_url=os.getenv("JIRA_URL", "").rstrip("/"),
            jira_email=os.getenv("JIRA_EMAIL", ""),
            jira_api_token=os.getenv("JIRA_API_TOKEN", ""),
            jira_project_key=os.getenv("JIRA_PROJECT_KEY", "AICOE"),
            jira_mode=mode,
        )

    def validate_for_jira_real(self) -> None:
        """
        Fails fast if Jira mode is 'real' but required credentials are missing.
        """
        if self.jira_mode == "real":
            missing = []
            if not self.jira_url:
                missing.append("JIRA_URL")
            if not self.jira_email:
                missing.append("JIRA_EMAIL")
            if not self.jira_api_token:
                missing.append("JIRA_API_TOKEN")

            if missing:
                raise ValueError(
                    f"Jira integration set to 'real' but missing environment variable(s): {', '.join(missing)}. "
                    "Please set them in your .env file or environment, or set JIRA_MODE=mock."
                )


# Global default configuration instance
config = Config.load()
