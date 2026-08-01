# After-Meeting Agent — MCP Portfolio Server

An MCP server exposing tools to convert meeting transcripts into structured follow-through actions: Jira tickets, Slack summaries, and calendar follow-ups. Built as a portfolio project demonstrating real REST API integration, risk-tiered human-in-the-loop confirmation, and audit logging.

## What it demonstrates

1. **Modular Integration Architecture**:
   - `integrations/base.py`: Clean abstract interfaces (`JiraIntegrationBase`, `SlackIntegrationBase`, `CalendarIntegrationBase`).
   - `integrations/jira_real.py`: Production-grade REST client using Atlassian Jira API v3 (Basic Auth with API Token).
   - `integrations/*_mock.py`: Mock implementations for Slack & Calendar (and Jira offline fallback).
2. **Risk-Tiered Execution & Batched Human-in-the-Loop Confirmation**:
   - **AUTO-RUN Tier**: `post_slack_summary` and `schedule_followup` execute immediately (reversible / mock side-effects).
   - **CONFIRMED Tier (2-Phase Batched)**: `propose_jira_tickets` stages ALL action items into a pending batch without creating anything external. `confirm_action(batch_id)` executes creation only after explicit user confirmation in chat.
3. **Structured Audit Log**:
   - Append-only `audit_log.jsonl` tracking every auto-run action and 2-phase confirmation event (including propose vs confirm timestamps and elapsed seconds).
4. **Fail-Fast Environment Configuration**:
   - `config.py` loads variables from `.env` and validates credentials on startup when `JIRA_MODE=real`.

## Setup

Set up a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install "mcp<2.0.0" httpx python-dotenv pytest
```

Configure environment variables (copy `.env.example` to `.env`):

```bash
cp .env.example .env
```

For live Jira integration, set in `.env`:
```env
JIRA_MODE=real
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your_jira_api_token
JIRA_PROJECT_KEY=AICOE
```
For local mock testing, keep `JIRA_MODE=mock`.

## Running Tests

Run unit tests (includes HTTP mocking for Jira REST API):

```bash
pytest tests/
```

Run stdio client integration test:

```bash
python3 test_client.py
```

## MCP Configuration (Claude Code / Antigravity / Claude Desktop)

Add to your MCP configuration file (`.claude/mcp.json` or `mcp_config.json`):

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

## Agent Interaction Workflow

In a chat session, ask the agent to process a transcript:

> "Read sample_transcript.txt. Identify action items, decisions, and follow-up cadence. Propose Jira tickets for the action items, post a Slack summary to #project-updates, and schedule follow-ups."

The agent will:
1. Auto-run `post_slack_summary` and `schedule_followup`.
2. Propose Jira tickets via `propose_jira_tickets` and display a summary preview with a `batch_id` (e.g. `batch-77a2219f`).
3. Pause and ask for confirmation.
4. When you reply "Confirm", the agent calls `confirm_action(batch_id="batch-77a2219f")` to create the tickets in Jira.

## Demo Script (What to say live)

1. **Problem Statement** (30 sec): "Meeting follow-through breaks down because taking action requires multiple tools and manual triage. This agent closes that loop safely."
2. **Architecture** (30 sec): "We separate risk into two tiers. Slack posts and follow-up reminders run automatically. External write actions like Jira tickets require explicit, batched human-in-the-loop approval."
3. **Live Demonstration**: Show proposing tickets, reviewing preview, and confirming execution.
4. **Auditability**: `cat audit_log.jsonl` — show exact records of auto actions and confirm events with timing metrics.

## File Map

- `server.py` — FastMCP server exposing risk-tiered tools
- `config.py` — Environment configuration & credential validator
- `.env.example` — Environment variable template
- `confirmation.py` — Batched 2-phase confirmation engine
- `audit_log.py` — Append-only audit logger (`audit_log.jsonl`)
- `integrations/` — Abstract interfaces & REST/Mock implementations
- `mock_store.py` — File-backed mock store (`state.json`)
- `sample_transcript.txt` — Input transcript for demo
- `test_client.py` — Stdio client test script
- `tests/` — Pytest suite (`test_jira_real.py`, `test_confirmation_flow.py`)
