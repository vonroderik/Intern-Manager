from typing import Optional


class Intern:
    """
    Domain model representing an intern.

    This class represents an intern entity and mirrors the structure of
    the `interns` table in the database. It is primarily used as a data
    container for persistence and retrieval operations.

    An Intern may optionally be associated with a Venue through `venue_id`.

    Attributes:
        intern_id (Optional[int]): Unique database identifier. None if the
            intern has not yet been persisted.
        name (str): Full name of the intern.
        registration_number (int): Unique registration number assigned
            to the intern.
        term (str): Academic term or internship period.
        email (Optional[str]): Contact email address.
        start_date (Optional[str]): Internship start date (ISO format string).
        end_date (Optional[str]): Internship end date (ISO format string).
        working_days (Optional[str]): Description of working days.
        working_hours (Optional[str]): Description of working hours.
        venue_id (Optional[int]): Identifier of the associated venue.
    """

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
        """
        Initializes an Intern instance.

        Args:
            name (str): Full name of the intern.
            registration_number (int): Unique registration number.
            term (str): Academic term or internship period.
            intern_id (Optional[int]): Database identifier. Should be None
                for new interns not yet persisted.
            email (Optional[str]): Contact email address.
            start_date (Optional[str]): Internship start date as a string.
            end_date (Optional[str]): Internship end date as a string.
            working_days (Optional[str]): Description of working days.
            working_hours (Optional[str]): Description of working hours.
            venue_id (Optional[int]): Identifier of the associated venue.
        """

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

    def __repr__(self) -> str:
        return (
            f"Intern("
            f"id={self.intern_id}, "
            f"name={self.name}, "
            f"registration_number={self.registration_number}, "
            f"term={self.term}, "
            f"email={self.email}, "
            f"start_date={self.start_date}, "
            f"end_date={self.end_date}, "
            f"working_days={self.working_days}, "
            f"working_hours={self.working_hours}, "
            f"venue_id={self.venue_id}"
            f")"
        )
