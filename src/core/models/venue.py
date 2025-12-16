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
        address (Optional[str]): Physical address of the venue.
        supervisor_name (Optional[str]): Name of the responsible supervisor.
        email (Optional[str]): Contact email for the venue.
        phone (Optional[str]): Contact phone number for the venue.
    """

    def __init__(
        self,
        venue_name: str,
        venue_id: Optional[int] = None,
        address: Optional[str] = None,
        supervisor_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
    ):
        """
        Initializes a Venue instance.

        Args:
            venue_name (str): Name of the venue.
            venue_id (Optional[int]): Database identifier. None if not persisted.
            address (Optional[str]): Physical address of the venue.
            supervisor_name (Optional[str]): Name of the supervisor responsible
                for interns at this venue.
            email (Optional[str]): Contact email address.
            phone (Optional[str]): Contact phone number.
        """

        self.venue_name = venue_name
        self.venue_id = venue_id
        self.address = address
        self.supervisor_name = supervisor_name
        self.email = email
        self.phone = phone

    def __repr__(self) -> str:
        return (
            f"Venue("
            f"venue_name={self.venue_name}, "
            f"venue_id={self.venue_id}, "
            f"venue_address={self.address}, "
            f"supervisor_name={self.supervisor_name}, "
            f"venue_email={self.email}, "
            f"venue_phone={self.phone}, "
            f")"
        )
