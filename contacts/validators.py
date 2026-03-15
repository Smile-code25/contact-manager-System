import re


def validate_username(username: str) -> tuple:
    """
    Username rules:
      - Minimum 3 characters
      - Only letters, numbers, and underscores allowed
    Returns (is_valid, error_message)
    """
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    return True, ""


def validate_password(password: str) -> tuple:
    """
    Password rules:
      - Minimum 6 characters
    Returns (is_valid, error_message)
    """
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, ""


def validate_name(name: str) -> tuple:
    """
    Contact name rules:
      - 2–50 characters
      - Only letters, spaces, apostrophes, and hyphens
      - No consecutive special characters
      - Cannot start or end with a special character or space
      - Must contain at least 2 actual letters
    Returns (is_valid, error_message)
    """
    if not re.match(r"^[A-Za-z\s\'-]{2,50}$", name):
        return False, "Name can only contain letters and spaces (2–50 chars)"

    if re.search(r"[\s\'-]{2,}", name):
        return False, "Name cannot have consecutive spaces, apostrophes, or hyphens"

    if name.startswith(("'", "-", " ")) or name.endswith(("'", "-", " ")):
        return False, "Name cannot start or end with a space, apostrophe, or hyphen"

    letters_only = re.sub(r"[^A-Za-z]", "", name)
    if len(letters_only) < 2:
        return False, "Name must contain at least 2 letters"

    return True, ""


def validate_phone(phone: str) -> tuple:
    """
    Phone number rules (Indian mobile format):
      - Strips spaces, dashes, and parentheses
      - Strips +91 or 91 country code prefix if present
      - Remaining number must be exactly 10 digits
      - Must start with 6, 7, 8, or 9
    Returns (is_valid, cleaned_phone_or_error_message)
    """
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)

    if cleaned.startswith('+91') and len(cleaned) > 3:
        cleaned = cleaned[3:]
    elif cleaned.startswith('91') and len(cleaned) > 2:
        cleaned = cleaned[2:]

    if not cleaned:
        return False, "Phone number cannot be empty"

    if not re.match(r"^[6-9][0-9]{9}$", cleaned):
        return False, "Please enter a valid 10-digit phone number (must start with 6–9)"

    return True, cleaned


def validate_email(email: str) -> tuple:
    """
    Email rules:
      - Optional field — empty string or None is accepted
      - If provided, must match standard email format
    Returns (is_valid, cleaned_email_or_None_or_error_message)
    """
    if not email or not email.strip():
        return True, None

    cleaned = email.strip()

    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", cleaned):
        return False, "Please enter a valid email address"

    return True, cleaned
