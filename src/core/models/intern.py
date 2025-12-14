from typing import Optional


class Intern:
    """Represents the Intern. Is associated with a Venue"""

    def __init__(
        self,
        name: str,
        registration_number: int,
        term: str,
        intern_id: Optional[int] = None,
        email: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        working_days: Optional[str] = None,
        working_hours: Optional[str] = None,
        venue_id: Optional[int] = None,
    ):
        self.name = name
        self.registration_number = registration_number
        self.term = term
        self.intern_id = intern_id
        self.email = email
        self.start_date = start_date
        self.end_date = end_date
        self.working_days = working_days
        self.working_hours = working_hours
        self.venue_id = venue_id
