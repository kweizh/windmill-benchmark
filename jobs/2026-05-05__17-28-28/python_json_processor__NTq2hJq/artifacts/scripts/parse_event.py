import json


def main(event_json: str) -> dict:
    try:
        data = json.loads(event_json)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON payload")

    event = data["event"]
    user_id = data["user_id"]
    metadata = data.get("metadata", {})

    plan = metadata.get("plan", "free")
    source = metadata.get("source", "unknown")

    return {
        "event": event,
        "user_id": user_id,
        "plan": plan,
        "source": source,
        "summary": f"{event} by user #{user_id} via {source} on {plan} plan",
    }
