"""
Standalone MCP client test — connects to server.py over stdio and exercises
the risk-tiered confirmation flow (auto-run for Slack/Calendar, 2-phase proposed -> confirm for Jira).

Run:
    .venv/bin/python3 test_client.py
"""
import asyncio
import json
import os
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_PATH = os.path.join(os.path.dirname(__file__), "server.py")


async def main():
    # Clean state.json, pending_batches.json, and audit_log.jsonl before run
    for fname in ["state.json", "pending_batches.json", "audit_log.jsonl"]:
        fpath = os.path.join(os.path.dirname(__file__), fname)
        if os.path.exists(fpath):
            os.remove(fpath)

    params = StdioServerParameters(command=sys.executable, args=[SERVER_PATH])

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("=== Tools exposed by server ===")
            for t in tools.tools:
                print(f"- {t.name}: {t.description.strip().splitlines()[0]}")
            print()

            print("=== 1. Proposing Jira Tickets (CONFIRMED Tier - Phase 1) ===")
            prop_result = await session.call_tool(
                "propose_jira_tickets",
                arguments={
                    "tickets": [
                        {
                            "title": "Fix UER data mapping - replace fragile macro",
                            "description": "Source spreadsheet columns shifted again, broke Julia's macro. Needs proper contextual mapping fix.",
                            "priority": "High",
                        },
                        {
                            "title": "Fix GAME request form password reset routing issue",
                            "description": "GAME request form is routing password resets to wrong queue because Chatbot is misrouting intent.",
                            "priority": "Medium",
                        },
                    ]
                },
            )
            prop_text = prop_result.content[0].text
            print(prop_text)
            print()

            # Parse batch_id from proposal JSON result
            prop_data = json.loads(prop_text)
            batch_id = prop_data.get("batch_id")

            print("=== 2. Posting Slack Summary (AUTO-RUN Tier) ===")
            slack_result = await session.call_tool(
                "post_slack_summary",
                arguments={
                    "channel": "#project-updates",
                    "summary": "IAM sync: UER mapping fix ticket proposed (High). GAME routing issue proposed (Medium). Follow-up check-in in 1 week.",
                },
            )
            print(slack_result.content[0].text)
            print()

            print("=== 3. Scheduling Follow-up (AUTO-RUN Tier) ===")
            cal_result = await session.call_tool(
                "schedule_followup",
                arguments={
                    "title": "IAM Sync check-in on UER mapping fix and GAME routing issue",
                    "days_from_now": 7,
                },
            )
            print(cal_result.content[0].text)
            print()

            print(f"=== 4. Confirming Jira Ticket Batch '{batch_id}' (CONFIRMED Tier - Phase 2) ===")
            confirm_result = await session.call_tool(
                "confirm_action",
                arguments={"batch_id": batch_id},
            )
            print(confirm_result.content[0].text)
            print()

    state_path = os.path.join(os.path.dirname(__file__), "state.json")
    if os.path.exists(state_path):
        print("=== Resulting state.json ===")
        with open(state_path) as f:
            print(json.dumps(json.load(f), indent=2))
        print()

    audit_path = os.path.join(os.path.dirname(__file__), "audit_log.jsonl")
    if os.path.exists(audit_path):
        print("=== Resulting audit_log.jsonl ===")
        with open(audit_path) as f:
            print(f.read())


if __name__ == "__main__":
    asyncio.run(main())
