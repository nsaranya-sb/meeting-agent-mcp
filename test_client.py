"""
Standalone MCP client test — connects to server.py over stdio (the same
transport Claude Code uses) and calls each tool, to prove the server works
before wiring it into an actual Claude Code session.

Run:
    python3 test_client.py
"""
import asyncio
import json
import os
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_PATH = os.path.join(os.path.dirname(__file__), "server.py")


async def main():
    params = StdioServerParameters(command=sys.executable, args=[SERVER_PATH])

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("=== Tools exposed by server ===")
            for t in tools.tools:
                print(f"- {t.name}: {t.description.strip().splitlines()[0]}")
            print()

            print("=== Calling create_jira_ticket ===")
            result = await session.call_tool(
                "create_jira_ticket",
                arguments={
                    "title": "Fix UER data mapping - replace fragile macro",
                    "description": "Source spreadsheet columns shifted again, broke Karen's macro. Needs a proper contextual mapping fix, not another patch.",
                    "priority": "High",
                },
            )
            print(result.content[0].text)
            print()

            print("=== Calling post_slack_summary ===")
            result = await session.call_tool(
                "post_slack_summary",
                arguments={
                    "channel": "#project-updates",
                    "summary": "IAM sync: UER mapping fix raised as high priority ticket. GAME routing issue logged medium priority. Follow-up in 1 week given audit timeline.",
                },
            )
            print(result.content[0].text)
            print()

            print("=== Calling schedule_followup ===")
            result = await session.call_tool(
                "schedule_followup",
                arguments={
                    "title": "Check status of UER mapping fix + GAME routing ticket",
                    "days_from_now": 7,
                },
            )
            print(result.content[0].text)
            print()

    state_path = os.path.join(os.path.dirname(__file__), "state.json")
    if os.path.exists(state_path):
        print("=== Resulting state.json ===")
        with open(state_path) as f:
            print(json.dumps(json.load(f), indent=2))


if __name__ == "__main__":
    asyncio.run(main())
