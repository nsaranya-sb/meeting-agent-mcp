"""
Unit tests for the batched 2-tier confirmation flow (propose -> confirm) and audit logging.
"""
import os
import json
import pytest
import mock_store
import confirmation
import audit_log
from integrations.jira_mock import JiraMockIntegration


@pytest.fixture(autouse=True)
def clean_state_and_audit():
    # Setup clean state.json, audit_log.jsonl, and pending_batches.json before test
    state_file = mock_store.STATE_FILE
    audit_file = audit_log.AUDIT_LOG_FILE
    batches_file = confirmation.PENDING_BATCHES_FILE

    for f in [state_file, audit_file, batches_file]:
        if os.path.exists(f):
            os.remove(f)

    yield

    for f in [state_file, audit_file, batches_file]:
        if os.path.exists(f):
            os.remove(f)


def test_propose_and_confirm_batch_flow():
    # Step 1: Propose batch of tickets
    tickets = [
        {
            "title": "Fix UER data mapping",
            "description": "Macro broken by column shifts",
            "priority": "High",
        },
        {
            "title": "Fix GAME request form routing",
            "description": "Chatbot misrouting password resets",
            "priority": "Medium",
        },
    ]

    proposal = confirmation.propose_jira_tickets(tickets)
    assert proposal["status"] == "PROPOSED_AWAITING_CONFIRMATION"
    assert proposal["total_tickets"] == 2
    batch_id = proposal["batch_id"]

    # Verify NO tickets created in mock_store state yet
    state_before = mock_store._load()
    assert len(state_before["tickets"]) == 0

    # Step 2: Attempt confirm with invalid batch_id
    invalid_res = confirmation.confirm_action("batch-invalid-123", JiraMockIntegration())
    assert invalid_res["status"] == "ERROR"

    state_still_empty = mock_store._load()
    assert len(state_still_empty["tickets"]) == 0

    # Step 3: Confirm action with valid batch_id
    confirm_res = confirmation.confirm_action(batch_id, JiraMockIntegration())
    assert confirm_res["status"] == "CONFIRMED_AND_CREATED"
    assert confirm_res["total_created"] == 2

    # Verify tickets ARE created in mock_store state now
    state_after = mock_store._load()
    assert len(state_after["tickets"]) == 2
    assert state_after["tickets"][0]["title"] == "Fix UER data mapping"

    # Step 4: Re-confirming same batch returns ALREADY_EXECUTED
    reconfirm_res = confirmation.confirm_action(batch_id, JiraMockIntegration())
    assert reconfirm_res["status"] == "ALREADY_EXECUTED"

    # Step 5: Verify Audit Log entries
    logs = audit_log.get_audit_logs()
    assert len(logs) == 2
    propose_log = logs[0]
    confirm_log = logs[1]

    assert propose_log["event"] == "propose_jira_tickets"
    assert propose_log["tier"] == "confirmed"
    assert propose_log["batch_id"] == batch_id

    assert confirm_log["event"] == "confirm_jira_tickets"
    assert confirm_log["tier"] == "confirmed"
    assert confirm_log["batch_id"] == batch_id
    assert "elapsed_seconds" in confirm_log
