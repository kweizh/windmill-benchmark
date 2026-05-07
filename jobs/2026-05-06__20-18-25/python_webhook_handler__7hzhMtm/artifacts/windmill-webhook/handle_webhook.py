def main(event_type: str, payload: dict) -> dict:
    """
    Dispatch and process incoming GitHub webhook events.
    
    Args:
        event_type: The type of webhook event (e.g., "push", "pull_request", "ping")
        payload: The webhook payload dictionary containing event data
    
    Returns:
        dict: A response dictionary with action details and handled status
    """
    if event_type == "push":
        repo_name = payload["repository"]["name"]
        commits = payload["commits"]
        return {
            "action": "push",
            "repo": repo_name,
            "commit_count": len(commits),
            "handled": True
        }
    elif event_type == "pull_request":
        pr_action = payload["action"]
        title = payload["pull_request"]["title"]
        return {
            "action": "pull_request",
            "pr_action": pr_action,
            "title": title,
            "handled": True
        }
    elif event_type == "ping":
        return {
            "action": "ping",
            "message": "pong",
            "handled": True
        }
    else:
        return {
            "action": event_type,
            "handled": False,
            "message": f"Unhandled event type: {event_type}"
        }