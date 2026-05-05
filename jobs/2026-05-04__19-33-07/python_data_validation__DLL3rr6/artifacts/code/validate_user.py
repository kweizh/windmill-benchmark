def main(user: dict) -> dict:
    errors = []

    # Validate name
    name = user.get("name")
    if name is None:
        errors.append("name is required")
    elif not isinstance(name, str) or not name.strip():
        errors.append("name must be a non-empty string")

    # Validate email
    email = user.get("email")
    if email is None:
        errors.append("email is required")
    elif not isinstance(email, str) or "@" not in email or "." not in email:
        errors.append("email must be a string containing '@' and '.'")

    # Validate age
    age = user.get("age")
    if age is not None:
        if not isinstance(age, int) or isinstance(age, bool):  # bool is a subclass of int in Python
            errors.append("age must be an integer")
        elif not (0 <= age <= 150):
            errors.append("age must be between 0 and 150")

    if errors:
        raise ValueError(f"Validation failed: {'; '.join(errors)}")

    return {
        "valid": True,
        "name": user["name"].strip(),
        "email": user["email"].lower(),
        "age": user.get("age"),
    }
