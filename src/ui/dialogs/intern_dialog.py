from typing import Optional
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLineEdit,
    QDialogButtonBox,
    QVBoxLayout,
    QDateEdit,
)
from PySide6.QtCore import QDate
from core.models.intern import Intern


class InternDialog(QDialog):

    def __init__(self, parent=None, intern: Optional[Intern] = None):
        super().__init__(parent)
        self.intern = intern

        self.setWindowTitle("Ficha do Estagiário")
        self.setMinimumWidth(400)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.form_layout = QFormLayout()

        self.txt_name = QLineEdit()
        self.txt_ra = QLineEdit()
        self.txt_email = QLineEdit()
        self.txt_term = QLineEdit()

        self.date_start = QDateEdit()
        self.date_start.setCalendarPopup(True)
        self.date_start.setDisplayFormat("dd/MM/yyyy")
        self.date_start.setDate(QDate.currentDate())

        self.date_end = QDateEdit()
        self.date_end.setCalendarPopup(True)
        self.date_end.setDisplayFormat("dd/MM/yyyy")
        self.date_end.setDate(QDate.currentDate().addMonths(6))

        self.form_layout.addRow("Nome Completo:", self.txt_name)
        self.form_layout.addRow("RA (Matrícula):", self.txt_ra)
        self.form_layout.addRow("E-mail:", self.txt_email)
        self.form_layout.addRow("Semestre:", self.txt_term)
        self.form_layout.addRow("Início do Estágio:", self.date_start)
        self.form_layout.addRow("Previsão de Fim:", self.date_end)

        self.main_layout.addLayout(self.form_layout)  # Usando main_layout aqui

        buttons = (
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons = QDialogButtonBox(buttons)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.main_layout.addWidget(self.buttons)

        if self.intern:
            self.load_data()

    def load_data(self):
        """Pega os dados do objeto Intern e joga na tela"""
        if not self.intern:
            return

        self.txt_name.setText(self.intern.name)
        self.txt_ra.setText(str(self.intern.registration_number))
        self.txt_email.setText(self.intern.email or "")
        self.txt_term.setText(self.intern.term or "")

        if self.intern.start_date:
            self.date_start.setDate(
                QDate.fromString(self.intern.start_date, "yyyy-MM-dd")
            )

        if self.intern.end_date:
            self.date_end.setDate(QDate.fromString(self.intern.end_date, "yyyy-MM-dd"))

        self.txt_ra.setReadOnly(True)
        self.txt_ra.setToolTip("O RA não pode ser alterado após a criação.")

    def get_data(self) -> dict:
        """Pega o que o usuário digitou e retorna um dicionário"""
        return {
            "name": self.txt_name.text().strip(),
            "registration_number": self.txt_ra.text().strip(),
            "email": self.txt_email.text().strip(),
            "term": self.txt_term.text().strip(),
            "start_date": self.date_start.date().toString("yyyy-MM-dd"),
            "end_date": self.date_end.date().toString("yyyy-MM-dd"),
        }
