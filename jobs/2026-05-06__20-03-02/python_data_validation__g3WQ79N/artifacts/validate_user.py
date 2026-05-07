def main(user: dict) -> dict:
    errors = []

    name = user.get("name")
    if not isinstance(name, str) or not name.strip():
        errors.append("name is required and must be a non-empty string")

    email = user.get("email")
    if not isinstance(email, str) or not email.strip():
        errors.append("email is required and must be a non-empty string")
    elif "@" not in email or "." not in email:
        errors.append("email must contain '@' and '.'")

    age = user.get("age")
    if age is not None:
        if not isinstance(age, int):
            errors.append("age must be an integer between 0 and 150")
        elif not (0 <= age <= 150):
            errors.append("age must be between 0 and 150")

    if errors:
        raise ValueError(f"Validation failed: {'; '.join(errors)}")

    return {
        "valid": True,
        "name": name.strip(),
        "email": email.lower(),
        "age": age,
    }
