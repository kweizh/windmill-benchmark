def main(age_str: str) -> dict:
    """
    Parse and categorize an age string.
    
    Args:
        age_str: A string representation of an age
        
    Returns:
        A dictionary with 'age' (integer) and 'category' (string)
        
    Raises:
        ValueError: If the age string is not a valid integer or if the age is out of range
    """
    # Try to convert the string to an integer
    try:
        age = int(age_str)
    except ValueError:
        raise ValueError(f"Invalid age: '{age_str}' is not an integer")
    
    # Validate age range
    if age < 0 or age > 150:
        raise ValueError(f"Age {age} is out of valid range (0–150)")
    
    # Determine category
    if age < 18:
        category = "minor"
    elif age < 65:
        category = "adult"
    else:
        category = "senior"
    
    return {"age": age, "category": category}