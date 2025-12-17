from datetime import datetime
import re
from typing import Any

DATE_INPUT_FORMAT = "%d/%m/%Y"
"""
Expected input date format used by the application UI.
Format: DD/MM/YYYY
"""

EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
"""
Regular expression used to validate e-mail addresses.
"""


def validate_email_format(email: str) -> None:
    """
    Validates whether the given string matches a valid e-mail format.

    Args:
        email (str): E-mail address to be validated.

    Raises:
        ValueError: If the e-mail does not match the expected format.
    """
    if not re.match(EMAIL_REGEX, email):
        raise ValueError("Invalid e-mail format.")


def validate_date_range(start_date_str: str, end_date_str: str) -> None:
    """
    Validates that two date strings are in the expected format and that
    the end date is later than the start date.

    Both dates must be provided in the DD/MM/YYYY format.

    Args:
        start_date_str (str): Internship start date.
        end_date_str (str): Internship end date.

    Raises:
        ValueError: If the date format is invalid or if the end date
        is not later than the start date.
    """
    try:
        dt_start = datetime.strptime(start_date_str, DATE_INPUT_FORMAT)
        dt_end = datetime.strptime(end_date_str, DATE_INPUT_FORMAT)
    except ValueError:
        raise ValueError(f"Date format must be {DATE_INPUT_FORMAT}.")

    if dt_end <= dt_start:
        raise ValueError("End date must be later than start date.")


def validate_required_fields(data_object: Any, fields_map: dict) -> None:
    """
    Checks whether required attributes exist and are not None
    in a given object.

    This function is intentionally generic and can be used for
    different domain entities (e.g. Intern, Venue, etc.).

    Args:
        data_object (Any): Domain object to be validated.
        fields_map (dict): Mapping of object attribute names to
            human-readable field names for error messages.
            Example:
            {
                "name": "Student Name",
                "email": "E-mail"
            }

    Raises:
        ValueError: If one or more required fields are missing or None.
    """
    missing = []

    for attr, ui_attr_name in fields_map.items():
        if not hasattr(data_object, attr) or getattr(data_object, attr) is None:
            missing.append(ui_attr_name)

    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")


def parse_date_to_iso(date_str: str) -> str:
    """
    Converts a date string from the UI format (DD/MM/YYYY)
    to ISO format (YYYY-MM-DD).

    This function assumes the input date has already been validated.

    Args:
        date_str (str): Date string in DD/MM/YYYY format.

    Returns:
        str: Date string in ISO format (YYYY-MM-DD).

    Raises:
        ValueError: If the input date does not match the expected format.
    """
    dt = datetime.strptime(date_str, DATE_INPUT_FORMAT)
    return dt.strftime("%Y-%m-%d")
