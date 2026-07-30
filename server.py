"""
After-Meeting Agent MCP Server (demo prototype)

Exposes 3 tools that a Claude Code / Claude Desktop session can call after
reading a meeting transcript:
    - create_jira_ticket
    - post_slack_summary
    - schedule_followup

All backed by mock_store.py so state persists to state.json for the demo
(you can `cat state.json` live to show what got created).

Run standalone for a quick smoke test:
    python3 server.py
Then connect via Claude Code / Claude Desktop MCP config (see README.md).
"""
from mcp.server.fastmcp import FastMCP
import mock_store

mcp = FastMCP("after-meeting-agent")


@mcp.tool()
def create_jira_ticket(title: str, description: str, priority: str = "Medium") -> dict:
    """
    Create a Jira ticket from an action item identified in a meeting transcript.

    Args:
        title: Short ticket title / summary of the action item.
        description: Fuller context - who owns it, what was discussed.
        priority: One of Low, Medium, High, Urgent.
    """
    return mock_store.create_ticket(title, description, priority)


@mcp.tool()
def post_slack_summary(channel: str, summary: str) -> dict:
    """
    Post a meeting summary to a Slack channel.

    Args:
        channel: Slack channel name, e.g. '#project-updates'.
        summary: The summary text to post (key decisions, action items, owners).
    """
    return mock_store.post_slack_summary(channel, summary)


@mcp.tool()
def schedule_followup(title: str, days_from_now: int = 3) -> dict:
    """
    Schedule a follow-up meeting or reminder.

    Args:
        title: What the follow-up is about.
        days_from_now: How many days from today to schedule it.
    """
    return mock_store.schedule_followup(title, days_from_now)


if __name__ == "__main__":
    mcp.run()
