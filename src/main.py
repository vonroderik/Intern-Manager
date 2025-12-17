from data.database import DatabaseConnector
from core.models.venue import Venue
from core.models.intern import Intern
from repository.venue_repo import VenueRepository
from repository.intern_repo import InternRepository
from services.venue_service import VenueService
from services.intern_service import InternService


def main():
    db = DatabaseConnector()
    v_service = VenueService(VenueRepository(db))
    i_service = InternService(InternRepository(db))

    dados_manuais = [
        {
            "nome": "Alex Ellwanger Pereira",
            "ra": 1833550,
            "local": "Miracle Store",
            "sup": "Gabriela Golubinski",
            "email": "gabigolubinski@hotmail.com",
            "ini": "29/09/2025",
            "fim": "13/12/2025",
        },
        {
            "nome": "Hellen Gouvea Schmidt",
            "ra": 1928926,
            "local": "Tassia Triboli Saúde",
            "sup": "Tassia Triboli",
            "email": "tassia.triboli@outlook.com",
            "ini": "06/08/2025",
            "fim": "05/12/2025",
        },
        {
            "nome": "Isadora Bitencourt",
            "ra": 1933829,
            "local": "Clinitá",
            "sup": "Alana Sebastiany",
            "email": "alana@clinitas.com",
            "ini": "01/08/2025",
            "fim": "26/11/2025",
        },
        {
            "nome": "Julian Benito Garcia",
            "ra": 1944929,
            "local": "Espaço Facial",
            "sup": "Josiele Maiara",
            "email": "biomed.josielemaiara@gmail.com",
            "ini": "01/08/2025",
            "fim": "13/12/2025",
        },
        {
            "nome": "Larissa de Freitas",
            "ra": 1931492,
            "local": "Clínica Wasser",
            "sup": "Paula Taís",
            "email": "paula@wasser.com",
            "ini": "04/08/2025",
            "fim": "19/12/2025",
        },
        {
            "nome": "Laura Chinazzo Altmann",
            "ra": 1929568,
            "local": "Luv Clinic",
            "sup": "Larissa Kayser",
            "email": "larissa@luvclinic.com",
            "ini": "21/07/2025",
            "fim": "13/11/2025",
        },
        {
            "nome": "Laura Reichert Freitas",
            "ra": 1930812,
            "local": "Emagrecentro",
            "sup": "Marines Silva",
            "email": "emagrecentro@gmail.com",
            "ini": "21/07/2025",
            "fim": "13/12/2025",
        },
    ]

    for item in dados_manuais:
        try:
            # Gerencia Venue
            existing_v = v_service.repo.get_by_name(item["local"])
            if existing_v:
                v_id = existing_v.venue_id
            else:
                v_id = v_service.add_new_venue(
                    Venue(
                        venue_name=item["local"],
                        supervisor_name=item["sup"],
                        supervisor_email=item["email"],
                    )
                )

            # Gerencia Intern
            i_service.add_new_intern(
                Intern(
                    name=item["nome"],
                    registration_number=item["ra"],
                    term="5º Módulo",
                    email=f"aluno{item['ra']}@teste.com",
                    start_date=item["ini"],
                    end_date=item["fim"],
                    venue_id=v_id,
                )
            )
            print(f"✅ {item['nome']} salvo com sucesso!")
        except Exception as e:
            print(f"❌ Erro em {item['nome']}: {e}")


if __name__ == "__main__":
    main()
