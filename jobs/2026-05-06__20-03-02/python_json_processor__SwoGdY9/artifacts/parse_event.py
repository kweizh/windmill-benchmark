import json
from typing import Any, Dict


def main(event_json: str) -> dict:
    try:
        payload: Dict[str, Any] = json.loads(event_json)
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid JSON payload") from exc

    event = payload.get("event")
    user_id = payload.get("user_id")
    metadata = payload.get("metadata", {}) or {}
    plan = metadata.get("plan", "free")
    source = metadata.get("source", "unknown")

    return {
        "event": event,
        "user_id": user_id,
        "plan": plan,
        "source": source,
        "summary": f"{event} by user #{user_id} via {source} on {plan} plan",
    }
