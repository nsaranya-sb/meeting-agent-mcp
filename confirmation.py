"""
Batched confirmation manager for high-risk actions (Jira ticket creation).
Provides a 2-phase human-in-the-loop workflow: propose_jira_tickets -> confirm_action.
"""
import json
import os
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from integrations.base import JiraIntegrationBase
from integrations.jira_mock import JiraMockIntegration
import audit_log

PENDING_BATCHES_FILE = os.path.join(os.path.dirname(__file__), "pending_batches.json")


def _load_pending_batches() -> Dict[str, Any]:
    if not os.path.exists(PENDING_BATCHES_FILE):
        return {}
    try:
        with open(PENDING_BATCHES_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_pending_batches(batches: Dict[str, Any]) -> None:
    with open(PENDING_BATCHES_FILE, "w") as f:
        json.dump(batches, f, indent=2)


def propose_jira_tickets(tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Phase 1: Stage ALL action items identified from a transcript run for human review.
    Does NOT create anything in Jira yet. Returns a consolidated preview and batch_id.
    """
    if not isinstance(tickets, list) or len(tickets) == 0:
        raise ValueError("Tickets must be a non-empty list of ticket dictionaries.")

    batch_id = f"batch-{uuid.uuid4().hex[:8]}"
    proposed_at = datetime.now(timezone.utc).isoformat()

    batch_record = {
        "batch_id": batch_id,
        "proposed_at": proposed_at,
        "status": "AWAITING_CONFIRMATION",
        "tickets": tickets,
    }

    batches = _load_pending_batches()
    batches[batch_id] = batch_record
    _save_pending_batches(batches)

    # Log propose event to audit log
    audit_log.log_propose_event(batch_id, tickets)

    # Return preview representation
    preview_summary = [
        {
            "item": i + 1,
            "title": t.get("title", ""),
            "priority": t.get("priority", "Medium"),
            "description": t.get("description", ""),
        }
        for i, t in enumerate(tickets)
    ]

    return {
        "status": "PROPOSED_AWAITING_CONFIRMATION",
        "batch_id": batch_id,
        "total_tickets": len(tickets),
        "proposed_tickets": preview_summary,
        "message": (
            f"Successfully staged {len(tickets)} ticket(s) for creation under batch_id '{batch_id}'. "
            "No Jira tickets have been created yet. "
            f"To execute creation, confirm with 'confirm_action(batch_id=\"{batch_id}\")'."
        ),
    }


def confirm_action(
    batch_id: str, jira_client: Optional[JiraIntegrationBase] = None
) -> Dict[str, Any]:
    """
    Phase 2: Confirm and execute creation of all Jira tickets staged in batch_id.
    """
    if jira_client is None:
        jira_client = JiraMockIntegration()

    batches = _load_pending_batches()
    if batch_id not in batches:
        return {
            "status": "ERROR",
            "message": f"Batch ID '{batch_id}' not found or has expired.",
        }

    batch_record = batches[batch_id]
    if batch_record.get("status") == "CONFIRMED":
        return {
            "status": "ALREADY_EXECUTED",
            "message": f"Batch ID '{batch_id}' has already been confirmed and executed.",
            "created_tickets": batch_record.get("created_tickets", []),
        }

    tickets_to_create = batch_record.get("tickets", [])
    created_tickets = []

    for t in tickets_to_create:
        created = jira_client.create_ticket(
            title=t.get("title", ""),
            description=t.get("description", ""),
            priority=t.get("priority", "Medium"),
        )
        created_tickets.append(created)

    # Mark batch as CONFIRMED
    batch_record["status"] = "CONFIRMED"
    batch_record["confirmed_at"] = datetime.now(timezone.utc).isoformat()
    batch_record["created_tickets"] = created_tickets
    batches[batch_id] = batch_record
    _save_pending_batches(batches)

    # Log confirm event to audit log with timing metrics
    audit_log.log_confirm_event(
        batch_id=batch_id,
        created_tickets=created_tickets,
        proposed_at_iso=batch_record.get("proposed_at", datetime.now(timezone.utc).isoformat()),
    )

    return {
        "status": "CONFIRMED_AND_CREATED",
        "batch_id": batch_id,
        "total_created": len(created_tickets),
        "created_tickets": created_tickets,
        "message": f"Successfully created {len(created_tickets)} ticket(s) in Jira for batch '{batch_id}'.",
    }
