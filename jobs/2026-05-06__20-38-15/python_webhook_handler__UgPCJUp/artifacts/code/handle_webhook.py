def main(event_type: str, payload: dict) -> dict:
    if event_type == "push":
        repo_name = payload.get("repository", {}).get("name")
        commits = payload.get("commits", [])
        return {
            "action": "push",
            "repo": repo_name,
            "commit_count": len(commits),
            "handled": True
        }
    
    elif event_type == "pull_request":
        pr_action = payload.get("action")
        title = payload.get("pull_request", {}).get("title")
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
