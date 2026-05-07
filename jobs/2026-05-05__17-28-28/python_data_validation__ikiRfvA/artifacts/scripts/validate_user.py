def main(user: dict) -> dict:
    errors = []

    # Validate name: required, must be a non-empty string
    name = user.get("name")
    if name is None or not isinstance(name, str) or not name.strip():
        errors.append("name is required and must be a non-empty string")

    # Validate email: required, must contain '@' and '.'
    email = user.get("email")
    if email is None or not isinstance(email, str) or not email.strip():
        errors.append("email is required and must be a non-empty string")
    elif "@" not in email or "." not in email:
        errors.append("email must contain '@' and '.'")

    # Validate age: optional; if present, must be an integer between 0 and 150
    age = user.get("age")
    if age is not None:
        if not isinstance(age, int) or isinstance(age, bool):
            errors.append("age must be an integer")
        elif age < 0 or age > 150:
            errors.append("age must be between 0 and 150")

    if errors:
        raise ValueError(f"Validation failed: {'; '.join(errors)}")

    return {
        "valid": True,
        "name": user["name"].strip(),
        "email": user["email"].lower(),
        "age": user.get("age"),
    }
