import json


def main(event_json: str) -> dict:
    """
    Parse and summarize a JSON event payload.
    
    Args:
        event_json: A JSON string containing event data with the shape:
            {"event": "user.signup", "user_id": 42, "metadata": {"plan": "pro", "source": "web"}}
    
    Returns:
        A dict containing the parsed event data with summary:
        {
            "event": event,
            "user_id": user_id,
            "plan": metadata.get("plan", "free"),
            "source": metadata.get("source", "unknown"),
            "summary": f"{event} by user #{user_id} via {source} on {plan} plan"
        }
    
    Raises:
        ValueError: If the JSON payload is invalid
    """
    try:
        data = json.loads(event_json)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON payload")
    
    event = data.get("event")
    user_id = data.get("user_id")
    metadata = data.get("metadata", {})
    
    plan = metadata.get("plan", "free")
    source = metadata.get("source", "unknown")
    
    summary = f"{event} by user #{user_id} via {source} on {plan} plan"
    
    return {
        "event": event,
        "user_id": user_id,
        "plan": plan,
        "source": source,
        "summary": summary
    }