from data.database import DatabaseConnector
from core.models.intern import Intern
from typing import Optional, List
from sqlite3 import Connection, Cursor


class InternRepository:
    def __init__(self, db: DatabaseConnector):
        self.db = db
        if db.conn is None or db.cursor is None:
            raise RuntimeError(
                "Repository initialized without a valid database connection."
            )
        self.conn: Connection = db.conn
        self.cursor: Cursor = db.cursor

    def save(self, intern: Intern) -> int:
        if intern.intern_id is not None:
            raise ValueError("Cannot save an intern that already has an ID.")

        # REMOVIDO is_active DAQUI
        sql_query = """
        INSERT INTO interns (
            name, registration_number, term, email, 
            start_date, end_date, venue_id,
            working_days, working_hours
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        # REMOVIDO is_active DAQUI TAMBÉM (Agora são 9 itens)
        data = (
            intern.name,
            intern.registration_number,
            intern.term,
            intern.email,
            intern.start_date,
            intern.end_date,
            intern.venue_id,
            intern.working_days,
            intern.working_hours
        )

        self.cursor.execute(sql_query, data)
        self.conn.commit()

        if self.cursor.lastrowid is None:
            raise RuntimeError("Database failed to generate an ID.")
        return self.cursor.lastrowid

    def update(self, intern: Intern) -> bool:
        if intern.intern_id is None:
            raise ValueError("Cannot update an intern without an ID.")

        sql_query = """
        UPDATE interns SET
            name = ?, registration_number = ?, term = ?, email = ?, 
            start_date = ?, end_date = ?, venue_id = ?,
            working_days = ?, working_hours = ?,
            last_update = strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')
        WHERE intern_id = ?
        """
        data = (
            intern.name,
            intern.registration_number,
            intern.term,
            intern.email,
            intern.start_date,
            intern.end_date,
            intern.venue_id,
            intern.working_days,
            intern.working_hours,
            intern.intern_id,
        )

        self.cursor.execute(sql_query, data)
        self.conn.commit()
        return self.cursor.rowcount > 0

    def get_all(self) -> List[Intern]:
        sql_query = "SELECT * FROM interns ORDER BY name ASC"
        self.cursor.execute(sql_query)
        rows = self.cursor.fetchall()
        return [self._parse_row(row) for row in rows]

    def get_by_id(self, intern_id: int) -> Optional[Intern]:
        sql_query = "SELECT * FROM interns WHERE intern_id = ?"
        self.cursor.execute(sql_query, (intern_id,))
        row = self.cursor.fetchone()
        if row:
            return self._parse_row(row)
        return None

    def get_by_registration_number(self, ra: str) -> Optional[Intern]:
        sql_query = "SELECT * FROM interns WHERE registration_number = ?"
        self.cursor.execute(sql_query, (ra,))
        row = self.cursor.fetchone()
        if row:
            return self._parse_row(row)
        return None

    def delete(self, intern: Intern) -> bool:
        if intern.intern_id is None:
            raise ValueError("Cannot delete an intern without an ID.")

        sql_query = "DELETE FROM interns WHERE intern_id = ?"
        self.cursor.execute(sql_query, (intern.intern_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def _parse_row(self, row) -> Intern:
        # Tenta mapear colunas extras se existirem, senão None
        # O banco antigo pode ter 8 colunas (até venue_id). O novo terá 10 ou mais.
        
        # Mapeamento básico seguro
        i = Intern(
            intern_id=row[0],
            name=row[1],
            registration_number=row[2],
            term=row[3],
            email=row[4],
            start_date=row[5],
            end_date=row[6],
            # venue_id costuma ser o último na estrutura antiga, ou varia.
            # Vamos tentar ler indices com segurança
            venue_id=None,
            working_days=None,
            working_hours=None
        )
        
        # Tenta popular venue_id (geralmente indice 7 ou 9 dependendo da versão)
        # Se você recriou o banco com o código novo, working_days/hours devem estar nos indices 7 e 8
        try:
            if len(row) > 7: i.venue_id = row[7] # Caso antigo
            if len(row) > 8: 
                # Se tem mais colunas, a ordem muda. No SAVE usamos: name...venue, days, hours
                # Mas no SELECT * a ordem é a da criação da tabela.
                # Assumindo criação: ... venue_id, working_days, working_hours
                i.venue_id = row[7]
                i.working_days = row[8]
                i.working_hours = row[9]
        except IndexError:
            pass
            
        return i