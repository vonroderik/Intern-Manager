import csv
from pathlib import Path
from services.intern_service import InternService
from services.venue_service import VenueService
from services.document_service import DocumentService
from core.models.venue import Venue
from core.models.intern import Intern
from core.models.document import Document


class ImportService:
    """
    Service responsible for importing internship data from a CSV file.
    """

    def __init__(
        self,
        intern_service: InternService,
        venue_service: VenueService,
        document_service: DocumentService,
    ):
        self.intern_service = intern_service
        self.venue_service = venue_service
        self.document_service = document_service

    def read_file(self, filename: str | Path) -> None:
        """
        Reads a CSV file and imports its contents into the system.
        """
        processed_venues = set()
        processed_interns = set()
        venue_id_map: dict[str, int] = {}

        DEFAULT_DOCS = [
            "Contrato de EStágio",
            "Ficha de Frequência",
            "Diário de Campo",
            "Projeto de Intervenção",
            "Avaliação do Supervisor Local - Física",
            "Avaliação do Supervisor Local - Carreiras",
        ]

        encoding = "utf-8-sig"

        try:
            with open(filename, "r", newline="", encoding=encoding) as csv_file:
                sample = csv_file.read(2048)
                csv_file.seek(0)

                try:
                    dialect = csv.Sniffer().sniff(sample)
                    delimiter = dialect.delimiter
                except csv.Error:
                    delimiter = ";"

                reader = csv.DictReader(csv_file, delimiter=delimiter)

                line_count = 0
                for row in reader:
                    line_count += 1

                    venue_name = row.get("local", "").strip()
                    intern_name = row.get("nome", "").strip()
                    ra_raw = row.get("ra", "").strip()

                    if not intern_name or not ra_raw:
                        print(
                            f"AVISO: Linha {line_count} ignorada (Nome ou RA vazios)."
                        )
                        continue

                    raw_sup_email = row.get("email_supervisor")
                    email_supervisor_limpo = (
                        raw_sup_email.strip() if raw_sup_email else None
                    )

                    current_venue_id: int | None = None

                    # --------------------------------------------------
                    # 1. VENUE PROCESSING
                    # --------------------------------------------------
                    if venue_name and venue_name not in processed_venues:
                        existing_venue = self.venue_service.repo.get_by_name(venue_name)

                        venue_data = {
                            "venue_name": venue_name,
                            "supervisor_name": row.get("nome_supervisor", "").strip(),
                            "supervisor_email": email_supervisor_limpo,
                            "supervisor_phone": row.get(
                                "telefone_supervisor", ""
                            ).strip(),
                        }

                        if existing_venue:
                            venue_to_update = Venue(
                                venue_id=existing_venue.venue_id, **venue_data
                            )
                            self.venue_service.update_venue(venue_to_update)
                            current_venue_id = existing_venue.venue_id
                        else:
                            venue_to_add = Venue(**venue_data)
                            current_venue_id = self.venue_service.add_new_venue(
                                venue_to_add
                            )

                        if current_venue_id is None:
                            v = self.venue_service.repo.get_by_name(venue_name)
                            if v:
                                current_venue_id = v.venue_id

                        if current_venue_id is None:
                            raise RuntimeError(
                                f"Erro Crítico: Não foi possível obter ID para o local '{venue_name}'"
                            )

                        processed_venues.add(venue_name)
                        venue_id_map[venue_name] = current_venue_id
                    elif venue_name:
                        current_venue_id = venue_id_map.get(venue_name)
                        if not current_venue_id:
                            venue = self.venue_service.repo.get_by_name(venue_name)
                            if venue:
                                current_venue_id = venue.venue_id

                    # --------------------------------------------------
                    # 2. INTERN PROCESSING
                    # --------------------------------------------------
                    if intern_name in processed_interns:
                        continue

                    existing_intern = self.intern_service.repo.get_by_name(intern_name)

                    intern_data = {
                        "name": intern_name,
                        "registration_number": str(ra_raw),
                        "venue_id": current_venue_id,
                        "term": row.get("periodo", "").strip(),
                        "email": row.get("email", None),
                        "start_date": row.get("data_inicio", "").strip(),
                        "end_date": row.get("data_fim", "").strip(),
                        "working_hours": row.get("horarios", "").strip(),
                    }

                    if existing_intern:
                        intern_to_update = Intern(
                            intern_id=existing_intern.intern_id, **intern_data
                        )
                        self.intern_service.update_intern(intern_to_update)
                    else:
                        intern_to_add = Intern(**intern_data)
                        new_intern_id = self.intern_service.add_new_intern(
                            intern_to_add
                        )

                        if new_intern_id:
                            print(f"   -> Gerando documentos para: {intern_name}")
                            for doc_name in DEFAULT_DOCS:
                                new_doc = Document(
                                    intern_id=new_intern_id,
                                    document_name=doc_name,
                                    is_completed=False,
                                )
                                self.document_service.add_new_document(new_doc)

                    processed_interns.add(intern_name)

            print(f"Importação concluída. {line_count} linhas processadas.")

        except Exception as e:
            print(f"ERRO DE LEITURA: {e}")
            raise
