def main(
    message: str,
    recipient: str = "admin@example.com",
    subject: str = "Notification",
    priority: int = 1
) -> dict:
    return {
        "to": recipient,
        "subject": subject,
        "body": message,
        "priority": priority,
        "sent": False,
    }
