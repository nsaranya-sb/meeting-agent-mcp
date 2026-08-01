"""
After-Meeting Agent MCP Server (Modular & Risk-Tiered)

Exposes FastMCP tools for post-meeting execution:
    - propose_jira_tickets (CONFIRMED tier - Phase 1 batch proposal)
    - create_jira_ticket (CONFIRMED tier - Single ticket proposal wrapper)
    - confirm_action (CONFIRMED tier - Phase 2 execution)
    - post_slack_summary (AUTO-RUN tier - Immediate execution)
    - schedule_followup (AUTO-RUN tier - Immediate execution)
"""
from typing import List, Dict, Any
from mcp.server.fastmcp import FastMCP

from config import config
from integrations import (
    JiraRealIntegration,
    JiraMockIntegration,
    SlackMockIntegration,
    CalendarMockIntegration,
)
import confirmation
import audit_log

# Initialize MCP Server
mcp = FastMCP("after-meeting-agent")

# Select Jira integration based on configuration
if config.jira_mode == "real":
    try:
        config.validate_for_jira_real()
        jira_client = JiraRealIntegration(config)
    except Exception as e:
        print(f"[Warning] Jira real mode validation failed: {e}. Falling back to JiraMockIntegration.")
        jira_client = JiraMockIntegration()
else:
    jira_client = JiraMockIntegration()

slack_client = SlackMockIntegration()
calendar_client = CalendarMockIntegration()


@mcp.tool()
def propose_jira_tickets(tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Propose a batch of Jira tickets identified from a meeting transcript for review before creation.

    Args:
        tickets: List of ticket dictionaries, each containing 'title', 'description', and optional 'priority' (Low, Medium, High, Urgent).
    """
    return confirmation.propose_jira_tickets(tickets)


@mcp.tool()
def create_jira_ticket(title: str, description: str, priority: str = "Medium") -> Dict[str, Any]:
    """
    Propose a single Jira ticket for review before creation (routes through human-in-the-loop confirmation).

    Args:
        title: Ticket title / summary of the action item.
        description: Full context - who owns it, what was discussed.
        priority: One of Low, Medium, High, Urgent.
    """
    return confirmation.propose_jira_tickets(
        [{"title": title, "description": description, "priority": priority}]
    )


@mcp.tool()
def confirm_action(batch_id: str) -> Dict[str, Any]:
    """
    Confirm and execute the creation of a proposed batch of Jira tickets in Jira.

    Args:
        batch_id: The unique batch identifier returned by propose_jira_tickets (e.g. 'batch-a1b2c3d4').
    """
    return confirmation.confirm_action(batch_id, jira_client=jira_client)


@mcp.tool()
def post_slack_summary(channel: str, summary: str) -> Dict[str, Any]:
    """
    Post a meeting summary to a Slack channel (Auto-run tool - executes immediately).

    Args:
        channel: Slack channel name, e.g. '#project-updates'.
        summary: The summary text to post (key decisions, action items, owners).
    """
    result = slack_client.post_summary(channel, summary)
    audit_log.log_auto_action("post_slack_summary", {"channel": channel, "summary": summary}, result)
    return result


@mcp.tool()
def schedule_followup(title: str, days_from_now: int = 3) -> Dict[str, Any]:
    """
    Schedule a follow-up meeting or reminder (Auto-run tool - executes immediately).

    Args:
        title: What the follow-up is about.
        days_from_now: How many days from today to schedule it (check transcript for explicit timeline).
    """
    result = calendar_client.schedule_followup(title, days_from_now)
    audit_log.log_auto_action("schedule_followup", {"title": title, "days_from_now": days_from_now}, result)
    return result


if __name__ == "__main__":
    mcp.run()
