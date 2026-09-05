import re
from typing import Any


EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

IP_ADDRESS_PATTERN = re.compile(
    r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
)

PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:\+?\d[\d\s().-]{7,}\d)(?!\d)"
)

PII_FIELD_NAMES = {
    "email",
    "phone",
    "mobile",
    "telephone",
    "ssn",
    "social_security_number",
    "credit_card",
    "card_number",
    "password",
    "token",
    "access_token",
    "refresh_token",
}


def mask_text(value: str) -> str:
    """Mask common PII and sensitive values inside text."""
    if not isinstance(value, str):
        return value

    masked = EMAIL_PATTERN.sub("[REDACTED_EMAIL]", value)

    # Mask IP addresses before phone numbers so IPs are not
    # incorrectly detected as phone numbers.
    masked = IP_ADDRESS_PATTERN.sub("[REDACTED_IP]", masked)

    masked = PHONE_PATTERN.sub("[REDACTED_PHONE]", masked)

    return masked


def mask_pii(data: Any) -> Any:
    """Recursively mask PII and sensitive fields in structured API data."""
    if isinstance(data, dict):
        masked_data = {}

        for key, value in data.items():
            normalized_key = str(key).strip().lower()

            if normalized_key in PII_FIELD_NAMES:
                masked_data[key] = "[REDACTED]"
            else:
                masked_data[key] = mask_pii(value)

        return masked_data

    if isinstance(data, list):
        return [mask_pii(item) for item in data]

    if isinstance(data, tuple):
        return tuple(mask_pii(item) for item in data)

    if isinstance(data, str):
        return mask_text(data)

    return data