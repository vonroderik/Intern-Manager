from typing import Optional


class Intern:
    def __init__(
        self,
        name: str,
        registration_number: int,
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
        self.intern_id = intern_id
        self.email = email
        self.start_date = start_date
        self.end_date = end_date
        self.working_days = working_days
        self.working_hours = working_hours
        self.venue_id = venue_id
