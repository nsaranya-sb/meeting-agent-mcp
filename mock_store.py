"""
Lightweight in-memory / file-backed store so the demo has visible 'state'
you can show the interviewer (e.g. cat state.json after a few tool calls).
"""
import json
import os
from datetime import datetime, timedelta

STATE_FILE = os.path.join(os.path.dirname(__file__), "state.json")


def _load():
    if not os.path.exists(STATE_FILE):
        return {"tickets": [], "slack_posts": [], "followups": []}
    with open(STATE_FILE, "r") as f:
        return json.load(f)


def _save(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def create_ticket(title: str, description: str, priority: str = "Medium") -> dict:
    state = _load()
    ticket_id = f"AICOE-{100 + len(state['tickets']) + 1}"
    ticket = {
        "id": ticket_id,
        "title": title,
        "description": description,
        "priority": priority,
        "status": "To Do",
        "created_at": datetime.utcnow().isoformat(),
    }
    state["tickets"].append(ticket)
    _save(state)
    return ticket


def post_slack_summary(channel: str, summary: str) -> dict:
    state = _load()
    post = {
        "channel": channel,
        "summary": summary,
        "posted_at": datetime.utcnow().isoformat(),
    }
    state["slack_posts"].append(post)
    _save(state)
    return post


def schedule_followup(title: str, days_from_now: int = 3) -> dict:
    state = _load()
    followup = {
        "title": title,
        "scheduled_for": (datetime.utcnow() + timedelta(days=days_from_now)).date().isoformat(),
    }
    state["followups"].append(followup)
    _save(state)
    return followup
