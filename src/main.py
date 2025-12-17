from data.database import DatabaseConnector
from core.models.venue import Venue
from core.models.intern import Intern
from core.models.meeting import Meeting
from core.models.document import Document
from core.models.comment import Comment

from repository.venue_repo import VenueRepository
from repository.intern_repo import InternRepository
from repository.meeting_repo import MeetingRepository
from repository.document_repo import DocumentRepository
from repository.comment_repo import CommentRepository

from services.venue_service import VenueService
from services.intern_service import InternService
from services.meeting_service import MeetingService
from services.document_service import DocumentService
from services.comment_service import CommentService

import random
from datetime import datetime, timedelta

def generate_fake_data(intern_id: int, start_date_str: str, 
                       meeting_service: MeetingService, 
                       doc_service: DocumentService, 
                       comment_service: CommentService):
    """
    Injeta dados fictícios (Meeting, Document, Comment) em um estagiário
    para fins de teste de estresse do sistema.
    """
    
    # --- 1. Criar Reuniões (Placebos) ---
    # Tenta criar uma reunião 7 dias após o início
    try:
        dt_start = datetime.strptime(start_date_str, "%d/%m/%Y")
        meeting_date = dt_start + timedelta(days=7)
        meeting_str = meeting_date.strftime("%d/%m/%Y") # Formato UI
        
        # Randomiza se o aluno foi (80% de chance de ir, afinal eles precisam de nota)
        present = random.choice([True, True, True, True, False])
        
        meeting_service.add_new_meeting(
            Meeting(
                intern_id=intern_id,
                meeting_date=meeting_str,
                is_intern_present=present
            )
        )
    except Exception as e:
        print(f"   ⚠️ Falha ao criar reunião fake: {e}")

    # --- 2. Criar Documentos (Burocracia) ---
    docs_template = [
        "Termo de Compromisso de Estágio (TCE)",
        "Plano de Atividades",
        "Apólice de Seguro",
        "Ficha de Frequência Mensal"
    ]
    
    for doc_name in docs_template:
        try:
            is_done = random.choice([True, False]) # 50/50, clássico de aluno
            doc_service.add_new_document(
                Document(
                    intern_id=intern_id,
                    document_name=doc_name,
                    is_completed=is_done
                )
            )
        except Exception as e:
            print(f"   ⚠️ Falha ao criar documento fake ({doc_name}): {e}")

    # --- 3. Criar Comentários (Fofoca Acadêmica) ---
    comments_pool = [
        "Aluno demonstra interesse, mas mexe muito no celular.",
        "Excelente técnica de pipetagem (metafórica, já que é estética).",
        "Chegou atrasado duas vezes, culpo o trânsito.",
        "Precisa melhorar a postura profissional com pacientes.",
        "Destaque da turma, merece estrelinha."
    ]
    
    try:
        comment_text = random.choice(comments_pool)
        comment_service.add_new_comment(
            Comment(
                intern_id=intern_id,
                comment=comment_text
            )
        )
    except Exception as e:
        print(f"   ⚠️ Falha ao criar comentário fake: {e}")


def main():
    db = DatabaseConnector()
    
    # Inicializando a "equipe médica" (Services)
    v_service = VenueService(VenueRepository(db))
    i_service = InternService(InternRepository(db))
    m_service = MeetingService(MeetingRepository(db))
    d_service = DocumentService(DocumentRepository(db))
    c_service = CommentService(CommentRepository(db))

    # Seus dados reais (Pacientes Zero)
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
            "wd": "segunda a sexta",
            "fim": "13/12/2025",
        },
        {
    "nome": "Estagiário Teste Sem WD",
    "ra": 999999, # Um RA novo que não está no banco
    "local": "Miracle Store",
    "sup": "Gabriela",
    "email": "teste@teste.com",
    "ini": "29/09/2025",
    "fim": "13/12/2025"
    # Note que NÃO tem a chave "wd" aqui
}
    ]

    print("--- INICIANDO PROTOCOLO DE POPULAÇÃO ---")

    for item in dados_manuais:
        try:
            # 1. Gerencia Venue (Local)
            existing_v = v_service.repo.get_by_name(item["local"])
            if existing_v:
                v_id = existing_v.venue_id
                print(f"🏥 Local existente encontrado: {item['local']}")
            else:
                v_id = v_service.add_new_venue(
                    Venue(
                        venue_name=item["local"],
                        supervisor_name=item["sup"],
                        supervisor_email=item["email"],
                    )
                )
                print(f"✨ Novo local criado: {item['local']}")

            # 2. Gerencia Intern (Estagiário)
            # Tenta buscar pelo RA primeiro para evitar erro de UNIQUE constraint
            existing_i = i_service.repo.get_by_registration_number(item["ra"])
            
            if existing_i:
                intern_id = existing_i.intern_id
                print(f"👤 Estagiário já existe: {item['nome']} (ID: {intern_id})")
            else:
                intern_id = i_service.add_new_intern(
                    Intern(
                        name=item["nome"],
                        registration_number=item["ra"],
                        term="5º Módulo",
                        email=f"aluno{item['ra']}@teste.com",
                        start_date=item["ini"],
                        end_date=item["fim"],
                        working_days=item.get("wd"),
                        venue_id=v_id,
                    )
                )
                print(f"👶 Novo estagiário nascido: {item['nome']} (ID: {intern_id})")

            # 3. Injeta os dados fictícios (Meeting, Doc, Comment)
            # Só pra garantir que temos um ID válido
            if intern_id:
                generate_fake_data(intern_id, item["ini"], m_service, d_service, c_service)
                print(f"   💉 Dados complementares injetados em {item['nome']}")

        except Exception as e:
            print(f"❌ ERRO CRÍTICO no processamento de {item['nome']}: {e}")

    print("--- PROTOCOLO FINALIZADO ---")

if __name__ == "__main__":
    main()