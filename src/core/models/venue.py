from typing import Optional


class Venue:
    """
    Domain model representing a venue where interns are allocated.

    A Venue represents an organization, unit, or location responsible
    for hosting one or more interns. Each venue may be associated with
    multiple interns.

    This class mirrors the structure of the `venues` table in the database.

    Attributes:
        venue_id (Optional[int]): Unique database identifier. None if the
            venue has not yet been persisted.
        venue_name (str): Name of the venue.
        venue_address (Optional[str]): Physical address of the venue.
        supervisor_name (Optional[str]): Name of the responsible supervisor.
        supervisor_email (Optional[str]): Contact email for the venue.
        supervisor_phone (Optional[str]): Contact phone number for the venue.
    """

    def __init__(
        self,
        venue_name: str,
        venue_id: Optional[int] = None,
        venue_address: Optional[str] = None,
        supervisor_name: Optional[str] = None,
        supervisor_email: Optional[str] = None,
        supervisor_phone: Optional[str] = None,
    ):
        """
        Initializes a Venue instance.

        Args:
            venue_name (str): Name of the venue.
            venue_id (Optional[int]): Database identifier. None if not persisted.
            venue_address (Optional[str]): Physical address of the venue.
            supervisor_name (Optional[str]): Name of the supervisor responsible
                for interns at this venue.
            supervisor_email (Optional[str]): Contact email address.
            supervisor_phone (Optional[str]): Contact phone number.
        """

        self.venue_name = venue_name
        self.venue_id = venue_id
        self.venue_address = venue_address
        self.supervisor_name = supervisor_name
        self.supervisor_email = supervisor_email
        self.supervisor_phone = supervisor_phone

    def __repr__(self) -> str:
        return (
            f"Venue("
            f"venue_name={self.venue_name}, "
            f"venue_id={self.venue_id}, "
            f"venue_address={self.venue_address}, "
            f"supervisor_name={self.supervisor_name}, "
            f"supervisor_email={self.supervisor_email}, "
            f"supervisor_phone={self.supervisor_phone}, "
            f")"
        )
