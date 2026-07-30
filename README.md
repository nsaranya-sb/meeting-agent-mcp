# After-Meeting Agent — MCP Demo Prototype

An MCP server exposing 3 tools that turn a meeting transcript into concrete
follow-through: a Jira ticket, a Slack summary, and a scheduled follow-up.
Built as an interview demo for an AI Centre of Excellence panel.

## What it demonstrates

- Real MCP server (not a mock CLI) exposing typed tools with docstrings Claude
  reads to decide when/how to call them
- An agentic workflow: unstructured input (transcript) → reasoning → multiple
  tool calls → structured, auditable output (state.json)
- Extensible pattern: swapping mock_store.py functions for real Jira/Slack/
  Calendar API calls is a drop-in change, not a rewrite

## Setup

Set up a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install "mcp<2.0.0"
```

Smoke test the server using the standalone client:

```bash
python3 test_client.py
```

## Option A: Claude Code / Antigravity

Add to your MCP config (`claude mcp add` or `.claude/mcp.json` / `mcp_config.json`):

```json
{
  "mcpServers": {
    "after-meeting-agent": {
      "command": "/absolute/path/to/meeting-agent-mcp/.venv/bin/python3",
      "args": ["/absolute/path/to/meeting-agent-mcp/server.py"]
    }
  }
}
```

Then in an agent session:

```
Read sample_transcript.txt. Identify action items, decisions, and any
follow-up cadence mentioned. For each action item, create a Jira ticket
with an appropriate priority. Post a summary of the meeting to
#project-updates. Schedule any follow-ups mentioned at the cadence discussed.
```

## Option B: Claude Desktop

Same config format, in `claude_desktop_config.json` under `mcpServers`.
Restart Claude Desktop, then paste the transcript into chat with the same
instruction as above.

## Demo script (what to say live)

1. **Set up the problem** (30 sec): "IT transformation teams lose real time
   re-collating what happened in a meeting into tickets, comms, and
   follow-ups. This agent closes that loop automatically."
2. **Show the server code** (30 sec): open `server.py`, point out the 3 tools
   and their docstrings — "Claude reads these to decide which tool to call
   and with what arguments, this is the MCP contract."
3. **Run the demo live**: paste the instruction + `sample_transcript.txt`
   into Claude Code / Desktop, let it work.
4. **Show the result**: `cat state.json` — a ticket was created with the
   Julia/UER context preserved, a second lower-priority ticket for the
   routing issue, a Slack summary posted, a follow-up scheduled at the
   1-week cadence (not the default) — showing it picked up nuance from the
   transcript, not just keyword-matched.
5. **Close with the roadmap** (30 sec): "In production this would swap
   mock_store for real Jira/Slack/Calendar APIs, add a human-in-the-loop
   confirmation step before any ticket/calendar action, and log every tool
   call for audit — which matters a lot in a regulated environment."

## Files

- `server.py` — the MCP server and tool definitions
- `mock_store.py` — mock backing store (swap for real APIs later)
- `sample_transcript.txt` — demo input
- `test_client.py` — standalone MCP stdio client verification script
- `state.json` — generated after first run, shows what the agent created
