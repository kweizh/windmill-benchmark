def main(
    message: str,
    recipient: str = "admin@example.com",
    subject: str = "Notification",
    priority: int = 1
) -> dict:
    """
    Prepare a notification payload for sending.
    
    Args:
        message: The body/content of the notification
        recipient: Email address to send notification to (default: "admin@example.com")
        subject: Subject line for the notification (default: "Notification")
        priority: Priority level of the notification (default: 1)
    
    Returns:
        A dictionary containing the notification payload details
    """
    return {
        "to": recipient,
        "subject": subject,
        "body": message,
        "priority": priority,
        "sent": False  # simulated — no real email is sent
    }