import csv
from pathlib import Path
from services.intern_service import InternService
from services.venue_service import VenueService
from core.models.venue import Venue
from core.models.intern import Intern


class ImportService:
    def __init__(self, intern_service: InternService, venue_service: VenueService):
        self.intern_service = intern_service
        self.venue_service = venue_service

    def read_file(self, filename):
        processed_venues = set()
        processed_interns = set()

        venue_id_map = {}

        with open(filename, "r", newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)

            for row in reader:
                venue_name = row["local"]
                intern_name = row["nome"]
                current_venue_id = None

                # --- 1. VENUE PROCESSING ---
                if venue_name not in processed_venues:
                    existing_venue = self.venue_service.get_by_name(venue_name)

                    venue_data = {
                        "venue_name": row["local"],
                        "supervisor_name": row["nome_supervisor"],
                        "supervisor_email": row.get("email_supervisor"),
                        "supervisor_phone": row.get("telefone_supervisor"),
                    }

                    if existing_venue:
                        venue_to_update = Venue(
                            venue_id=existing_venue.venue_id, **venue_data
                        )

                        self.venue_service.update_venue(venue_to_update)
                        current_venue_id = existing_venue.venue_id
                    else:
                        venue_to_add = Venue(**venue_data)

                        new_id = self.venue_service.add_new_venue(venue_to_add)

                        current_venue_id = new_id

                    processed_venues.add(venue_name)
                    venue_id_map[venue_name] = current_venue_id

                else:
                    current_venue_id = venue_id_map.get(venue_name)
                    if not current_venue_id:
                        v = self.venue_service.get_by_name(venue_name)
                        if v:
                            current_venue_id = v.venue_id

                # --- 2. INTERN PROCESSING ---
                if intern_name in processed_interns:
                    continue

                existing_intern = self.intern_service.get_by_name(intern_name)
                intern_data = {
                    "name": row["nome"],
                    "registration_number": row["ra"],
                    "venue_id": current_venue_id,
                    "term": row["periodo"],
                    "email": f"aluno{row['ra']}@teste.com",
                    "start_date": row["data_inicio"],
                    "end_date": row["data_fim"],
                    "working_days": row["horarios"],
                }

                if existing_intern:
                    intern_to_update = Intern(
                        intern_id=existing_intern.intern_id, **intern_data
                    )
                    self.intern_service.update_intern(intern_to_update)

                else:
                    intern_to_add = Intern(**intern_data)
                    self.intern_service.add_new_intern(intern_to_add)
                processed_interns.add(intern_name)
