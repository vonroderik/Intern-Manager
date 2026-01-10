from typing import Optional
from dataclasses import dataclass

@dataclass
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

    venue_name: str
    venue_id: Optional[int] = None
    venue_address: Optional[str] = None
    supervisor_name: Optional[str] = None
    supervisor_email: Optional[str] = None
    supervisor_phone: Optional[str] = None

