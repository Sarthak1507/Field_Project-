"""Simple server-side validation for values submitted by the browser."""
import re
from datetime import date
from decimal import Decimal, InvalidOperation


def text(data, key, label, required=False, limit=160):
    value = str(data.get(key, "")).strip()
    if required and not value:
        raise ValueError(f"{label} is required.")
    if len(value) > limit:
        raise ValueError(f"{label} must be {limit} characters or fewer.")
    return value or None


def positive_id(data, key, label, required=False):
    value = data.get(key)
    if value in (None, "") and not required:
        return None
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"Choose a valid {label}.")
    if number <= 0:
        raise ValueError(f"Choose a valid {label}.")
    return number


def amount(data, key, label, required=True, allow_negative=False):
    value = data.get(key)
    if value in (None, "") and not required:
        return Decimal("0.00")
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"{label} must be a number.")
    if not number.is_finite() or (number < 0 and not allow_negative):
        raise ValueError(f"{label} must be a valid non-negative amount.")
    if number > Decimal("99999999.99"):
        raise ValueError(f"{label} is too large.")
    return number.quantize(Decimal("0.01"))


def date_value(data, key, label, required=False):
    value = data.get(key)
    if value in (None, "") and not required:
        return None
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        raise ValueError(f"{label} must be a valid date.")


def email_value(data, key="email", required=False):
    value = text(data, key, "Email", required, 254)
    if value and not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
        raise ValueError("Enter a valid email address.")
    return value


def phone_value(data, key, label, required=False):
    value = text(data, key, label, required, 25)
    if value and not re.fullmatch(r"[+0-9 ()-]{7,25}", value):
        raise ValueError(f"{label} has an invalid format.")
    return value


def enum_value(data, key, label, options, default=None):
    value = str(data.get(key, default or "")).strip()
    if value not in options:
        raise ValueError(f"Choose a valid {label}.")
    return value


def database_error_code(error):
    return getattr(error, "errno", None)