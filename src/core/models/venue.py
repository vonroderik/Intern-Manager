from typing import Optional


class Venue:
    """Venue where the intern is allocated. Can have multiple Interns"""

    def __init__(
        self,
        venue_name: str,
        venue_id: Optional[int] = None,
        address: Optional[str] = None,
        supervisor_name: Optional[str] = None,
        email: Optional[str] = None,
    ):
        self.venue_name = venue_name
        self.venue_id = venue_id
        self.address = address
        self.supervisor_name = supervisor_name
        self.email = email
