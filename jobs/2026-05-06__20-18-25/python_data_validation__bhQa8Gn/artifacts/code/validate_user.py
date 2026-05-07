def main(user: dict) -> dict:
    """
    Validate and normalize a user input dict.

    Args:
        user: A dict that may contain:
            - name (str): required, must be a non-empty string
            - email (str): required, must contain '@' and '.'
            - age (int): optional, if present must be an integer between 0 and 150

    Returns:
        A dict with validated and normalized user data:
            {"valid": True, "name": str, "email": str, "age": int|None}

    Raises:
        ValueError: If validation fails, with all validation errors listed
    """
    errors = []

    # Validate name
    if "name" not in user:
        errors.append("name is required")
    elif not isinstance(user["name"], str):
        errors.append("name must be a string")
    elif not user["name"].strip():
        errors.append("name cannot be empty")

    # Validate email
    if "email" not in user:
        errors.append("email is required")
    elif not isinstance(user["email"], str):
        errors.append("email must be a string")
    elif "@" not in user["email"] or "." not in user["email"]:
        errors.append("email must contain '@' and '.'")

    # Validate age (optional)
    if "age" in user:
        if user["age"] is None:
            # None is acceptable for optional fields
            pass
        elif not isinstance(user["age"], int):
            errors.append("age must be an integer")
        elif user["age"] < 0 or user["age"] > 150:
            errors.append("age must be between 0 and 150")

    # If there are any errors, raise ValueError with all errors
    if errors:
        raise ValueError(f"Validation failed: {'; '.join(errors)}")

    # Return validated and normalized data
    return {
        "valid": True,
        "name": user["name"].strip(),
        "email": user["email"].lower(),
        "age": user.get("age")
    }