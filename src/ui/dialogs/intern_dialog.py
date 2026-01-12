from typing import Optional
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLineEdit,
    QDialogButtonBox,
    QVBoxLayout,
    QDateEdit,
    QComboBox,
    QMessageBox,  # Importante para xingar o usuário
)
from PySide6.QtCore import QDate
from core.models.intern import Intern
from services.venue_service import VenueService
from utils.validations import validate_date_range  # <--- A estrela do show


class InternDialog(QDialog):
    """
    Dialog window for creating or editing an Intern record.
    Includes Venue selection and Logic Validation.
    """

    def __init__(
        self, parent, venue_service: VenueService, intern: Optional[Intern] = None
    ):
        super().__init__(parent)
        self.intern = intern
        self.venue_service = venue_service

        self.setWindowTitle("Ficha do Estagiário")
        self.setMinimumWidth(400)

        self._setup_ui()
        self.load_venues()

        if self.intern:
            self.load_data()

    def _setup_ui(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.form_layout = QFormLayout()

        self.txt_name = QLineEdit()
        self.txt_ra = QLineEdit()
        self.txt_email = QLineEdit()
        self.txt_term = QLineEdit()
        self.combo_venue = QComboBox()

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
        self.form_layout.addRow("Local de Estágio:", self.combo_venue)
        self.form_layout.addRow("Início do Estágio:", self.date_start)
        self.form_layout.addRow("Previsão de Fim:", self.date_end)

        self.main_layout.addLayout(self.form_layout)

        # Buttons
        buttons = (
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box = QDialogButtonBox(buttons)

        # MUDANÇA CRÍTICA: Conectamos ao método customizado validate_and_save, não direto ao accept
        self.button_box.accepted.connect(self.validate_and_save)
        self.button_box.rejected.connect(self.reject)

        self.main_layout.addWidget(self.button_box)

    def load_venues(self):
        self.combo_venue.clear()
        self.combo_venue.addItem("Selecione um local...", None)
        try:
            venues = self.venue_service.get_all()
            for v in venues:
                self.combo_venue.addItem(v.venue_name, v.venue_id)
        except Exception as e:
            print(f"Erro ao carregar locais: {e}")

    def load_data(self):
        if self.intern is None:
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

        if hasattr(self.intern, "venue_id") and self.intern.venue_id:
            index = self.combo_venue.findData(self.intern.venue_id)
            if index >= 0:
                self.combo_venue.setCurrentIndex(index)

        self.txt_ra.setReadOnly(True)
        self.txt_ra.setToolTip("O RA não pode ser alterado após a criação.")

    def validate_and_save(self):
        """
        Valida os dados antes de fechar o diálogo.
        Impede o fechamento se as datas estiverem incoerentes.
        """
        # 1. Validação de Campos Obrigatórios (Básico)
        if not self.txt_name.text().strip():
            QMessageBox.warning(self, "Erro", "O nome do aluno é obrigatório.")
            return

        if not self.txt_ra.text().strip():
            QMessageBox.warning(self, "Erro", "O RA é obrigatório.")
            return

        # 2. Validação Lógica de Datas (Usando sua lib)
        start_str = self.date_start.date().toString("dd/MM/yyyy")
        end_str = self.date_end.date().toString("dd/MM/yyyy")

        try:
            validate_date_range(start_str, end_str)
        except ValueError as e:
            QMessageBox.warning(self, "Datas Inválidas", str(e))
            return  # Aborta o salvamento

        # Se passou por tudo, aceita e fecha
        self.accept()

    def get_data(self) -> Intern:
        current_id = self.intern.intern_id if self.intern else None
        selected_venue_id = self.combo_venue.currentData()

        return Intern(
            intern_id=current_id,
            name=self.txt_name.text().strip(),
            registration_number=self.txt_ra.text().strip(),
            email=self.txt_email.text().strip() or None,
            term=self.txt_term.text().strip(),
            start_date=self.date_start.date().toString("yyyy-MM-dd"),
            end_date=self.date_end.date().toString("yyyy-MM-dd"),
            venue_id=selected_venue_id,
        )
