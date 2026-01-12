from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Intern:
    """
    Domain model representing an intern.

    This class mirrors the structure of the `interns` table in the database.
    It encapsulates personal information, academic details (registration, term),
    and internship specifics (dates, venue).

    Attributes:
        name (str): The full name of the intern.
        registration_number (str): The academic registration ID (RA).
        term (str): The academic term or semester (e.g., "7th Term").
        intern_id (Optional[int]): Unique database identifier. None if the
            intern has not yet been persisted.
        email (Optional[str]): Contact email address.
        start_date (Optional[str]): Internship start date in 'YYYY-MM-DD' format.
        end_date (Optional[str]): Internship end date in 'YYYY-MM-DD' format.
        working_days (Optional[str]): Description of working days.
        working_hours (Optional[str]): Description of working hours.
        venue_id (Optional[int]): Identifier of the associated internship venue.
    """

    name: str
    registration_number: str
    term: str

    intern_id: Optional[int] = None
    email: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    working_days: Optional[str] = None
    working_hours: Optional[str] = None
    venue_id: Optional[int] = None

    @property
    def status(self) -> str:
        """
        Determines the current status of the internship based on the end date.

        Returns:
            str: "Ativo" if the end date is in the future, not set, or invalid.
                 "Concluído" if the end date is in the past.
        """
        if not self.end_date:
            return "Ativo"

        try:
            end = datetime.strptime(self.end_date, "%Y-%m-%d")
            today = datetime.now()

            if end < today:
                return "Concluído"

            return "Ativo"
        except ValueError:
            return "Ativo"

    @property
    def formatted_start_date(self) -> str:
        """
        Formats the start date for UI display.

        Returns:
            str: The date formatted as 'DD/MM/YYYY', or the original string
                 if parsing fails. Returns an empty string if date is missing.
        """
        if not self.start_date:
            return ""
        try:
            d = datetime.strptime(self.start_date, "%Y-%m-%d")
            return d.strftime("%d/%m/%Y")
        except ValueError:
            return self.start_date

    @property
    def formatted_end_date(self) -> str:
        """
        Formats the end date for UI display.

        Returns:
            str: The date formatted as 'DD/MM/YYYY', or the original string
                 if parsing fails. Returns an empty string if date is missing.
        """
        if not self.end_date:
            return ""
        try:
            d = datetime.strptime(self.end_date, "%Y-%m-%d")
            return d.strftime("%d/%m/%Y")
        except ValueError:
            return self.end_date
