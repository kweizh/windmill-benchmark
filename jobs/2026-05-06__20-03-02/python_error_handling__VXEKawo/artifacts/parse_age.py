def main(age_str: str) -> dict:
    try:
        age = int(age_str)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid age: '{age_str}' is not an integer")

    if age < 0 or age > 150:
        raise ValueError(f"Age {age} is out of valid range (0–150)")

    if age < 18:
        category = "minor"
    elif age < 65:
        category = "adult"
    else:
        category = "senior"

    return {"age": age, "category": category}
