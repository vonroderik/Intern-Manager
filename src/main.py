# Arquivo: src/main.py

from data.database import DatabaseConnector
from repository.intern_repo import InternRepository
from core.models.intern import Intern
from core.models.venue import Venue
from typing import Optional
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def main():
    print("--- 🛠️ INICIANDO O TESTE DE INFRAESTRUTURA E PERSISTÊNCIA ---")

    # 1. TESTE DA CAMADA INFRA: Criação da Conexão e do DB
    # Isso também garante que a leitura do create_db.sql funcione
    try:
        db_connector = DatabaseConnector()
        print(
            "✅ 1. Conexão com o banco de dados estabelecida. (DB e tabelas criadas se não existiam)"
        )
    except Exception as e:
        print(f"❌ ERRO GRAVE na Conexão/Criação do DB: {e}")
        return

    # 2. TESTE DA CAMADA REPOSITÓRIO: Injeção de Dependência
    repo = InternRepository(db_connector)
    print("✅ 2. InternRepository inicializado com sucesso.")

    # 3. TESTE DA CAMADA MODELO & SALVAMENTO: Criando um novo Intern
    # (Usando o modelo atualizado com 'term' e respeitando a ordem de argumentos)
    print("\n--- TESTANDO INSERÇÃO ---")


    venue_to_save = Venue(
    venue_name="Miracle Store",
    supervisor_name="Gabriela Golubinski",
    email="gabi@miraclestore.com",
    phone="5194157618",
    address="Rua Teste, 123" # Incluí o endereço
)

    # 2. SQL INSERT para a Venue
    sql_insert_venue = """
    INSERT INTO venues (venue_name, address, supervisor_name, email, phone) 
    VALUES (?, ?, ?, ?, ?)
    """
    venue_data = (
        venue_to_save.venue_name,
        venue_to_save.address,
        venue_to_save.supervisor_name,
        venue_to_save.email,
        venue_to_save.phone
    )

    # 3. Execução e Commit
    db_connector.cursor.execute(sql_insert_venue, venue_data)
    db_connector.conn.commit()
    novo_estagiario1 = Intern(
            name="Alex Ellwanger Pereira",
            registration_number=1833550,
            term="2026-1",
            email="alexellwanger2019@gmail.com",
            start_date="2025-09-29",
            end_date="2025-12-13",
            working_days="Segunda a Sexta",
            working_hours="14:00 as 20:00",
            venue_id=1,  # Assumimos que a Venue ID será inserida depois, ou é nula.
        )

    novo_estagiario2 = Intern(
        name="Rodrigo Mello",
        registration_number=2025002,
        term="2026-1",
        email="teste.ficticio@universidade.br",
        start_date="2026-03-01",
        end_date="2026-09-01",
        working_days="Segunda a Sexta",
        working_hours="08h às 14h",
        venue_id=None,  # Assumimos que a Venue ID será inserida depois, ou é nula.
    )
    # 4. SALVAR NO DB
    print(f"Tentando salvar: {novo_estagiario1.name}...")

    intern_id = repo.save(novo_estagiario1)
    intern_id = repo.save(novo_estagiario2)

    if intern_id:
        print(f"✅ 3. Salvamento bem-sucedido! ID gerado no banco: {intern_id}")
        print(
            f"O objeto Python (novo_estagiario.intern_id) também foi atualizado para: {novo_estagiario1.intern_id}"
        )
    else:
        print("❌ ERRO: Falha ao salvar o estagiário (ID não retornado).")

    print("\n--- FIM DO TESTE ---")


if __name__ == "__main__":
    # Garanta que você está no diretório 'src' quando rodar:
    # python main.py
    main()
