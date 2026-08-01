"""
Append-only audit logger for After-Meeting Agent MCP Server.
Logs all auto-run and confirmed actions with timestamps, parameters, tiers, and timing metrics.
"""
import json
import os
from datetime import datetime, timezone
from typing import Dict, Any, List

AUDIT_LOG_FILE = os.path.join(os.path.dirname(__file__), "audit_log.jsonl")


def _append_log(entry: Dict[str, Any]) -> None:
    with open(AUDIT_LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


def log_auto_action(tool_name: str, parameters: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
    entry = {
        "event": f"auto_run_{tool_name}",
        "tool": tool_name,
        "tier": "auto",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "parameters": parameters,
        "result": result,
    }
    _append_log(entry)
    return entry


def log_propose_event(batch_id: str, tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
    entry = {
        "event": "propose_jira_tickets",
        "batch_id": batch_id,
        "tier": "confirmed",
        "status": "proposed",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tickets_count": len(tickets),
        "proposed_tickets": tickets,
    }
    _append_log(entry)
    return entry


def log_confirm_event(
    batch_id: str, created_tickets: List[Dict[str, Any]], proposed_at_iso: str
) -> Dict[str, Any]:
    now = datetime.now(timezone.utc)
    try:
        proposed_dt = datetime.fromisoformat(proposed_at_iso)
        elapsed_seconds = round((now - proposed_dt).total_seconds(), 3)
    except Exception:
        elapsed_seconds = 0.0

    entry = {
        "event": "confirm_jira_tickets",
        "batch_id": batch_id,
        "tier": "confirmed",
        "status": "executed",
        "timestamp": now.isoformat(),
        "proposed_at": proposed_at_iso,
        "elapsed_seconds": elapsed_seconds,
        "created_tickets": created_tickets,
    }
    _append_log(entry)
    return entry


def get_audit_logs() -> List[Dict[str, Any]]:
    if not os.path.exists(AUDIT_LOG_FILE):
        return []
    logs = []
    with open(AUDIT_LOG_FILE, "r") as f:
        for line in f:
            if line.strip():
                logs.append(json.loads(line.strip()))
    return logs
