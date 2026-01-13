from typing import Optional
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLineEdit,
    QDialogButtonBox,
    QVBoxLayout,
    QDateEdit,
    QComboBox,
    QMessageBox,
    QHBoxLayout,
    QPushButton,
)
from PySide6.QtCore import QDate
from core.models.intern import Intern
from services.venue_service import VenueService
from ui.dialogs.venue_dialog import VenueDialog
from utils.validations import validate_date_range


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

        # Venue Selection (Com botão Quick Add)
        self.combo_venue = QComboBox()

        self.venue_container = QHBoxLayout()
        self.venue_container.addWidget(self.combo_venue)

        self.btn_add_venue = QPushButton("➕")
        self.btn_add_venue.setFixedWidth(30)
        self.btn_add_venue.setToolTip("Cadastrar novo local agora")
        self.btn_add_venue.clicked.connect(self.quick_add_venue)

        self.venue_container.addWidget(self.btn_add_venue)

        # Dates
        self.date_start = QDateEdit()
        self.date_start.setCalendarPopup(True)
        self.date_start.setDate(QDate.currentDate())

        self.date_end = QDateEdit()
        self.date_end.setCalendarPopup(True)
        self.date_end.setDate(QDate.currentDate().addMonths(6))

        # Term
        self.combo_term = QComboBox()
        terms = [f"{y}/{s}" for y in range(2024, 2030) for s in [1, 2]]
        self.combo_term.addItems(terms)

        self.form_layout.addRow("Nome Completo:", self.txt_name)
        self.form_layout.addRow("RA (Matrícula):", self.txt_ra)
        self.form_layout.addRow("E-mail:", self.txt_email)
        self.form_layout.addRow("Local de Estágio:", self.venue_container)
        self.form_layout.addRow("Semestre:", self.combo_term)
        self.form_layout.addRow("Data Início:", self.date_start)
        self.form_layout.addRow("Data Término:", self.date_end)

        self.main_layout.addLayout(self.form_layout)

        # Buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.save_data)
        self.buttons.rejected.connect(self.reject)
        self.main_layout.addWidget(self.buttons)

    def load_venues(self):
        """Carrega lista de locais do banco."""
        current_data = self.combo_venue.currentData()
        self.combo_venue.clear()

        self.combo_venue.addItem("--- Selecione ---", None)
        venues = self.venue_service.get_all()
        for v in venues:
            self.combo_venue.addItem(v.venue_name, v.venue_id)

        if current_data:
            index = self.combo_venue.findData(current_data)
            if index >= 0:
                self.combo_venue.setCurrentIndex(index)

    def quick_add_venue(self):
        """Abre o diálogo de local, salva e atualiza o combo."""
        dialog = VenueDialog(self)
        if dialog.exec():
            try:
                new_venue_data = dialog.get_data()

                # CORREÇÃO 1: O método correto no seu service é 'add_new_venue', não 'create'
                new_id = self.venue_service.add_new_venue(new_venue_data)

                self.load_venues()

                index = self.combo_venue.findData(new_id)
                if index >= 0:
                    self.combo_venue.setCurrentIndex(index)

            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao adicionar local: {e}")

    def load_data(self):
        """Preenche campos na edição."""
        if not self.intern:
            return

        # Garante que seja string, mesmo que venha None ou Int do banco
        self.txt_name.setText(str(self.intern.name or ""))

        # AQUI ERA O ERRO: Adicionamos str() em volta
        self.txt_ra.setText(str(self.intern.registration_number or ""))

        self.txt_email.setText(self.intern.email or "")
        self.combo_term.setCurrentText(self.intern.term)

        if self.intern.venue_id:
            idx = self.combo_venue.findData(self.intern.venue_id)
            if idx >= 0:
                self.combo_venue.setCurrentIndex(idx)

        if self.intern.start_date:
            self.date_start.setDate(
                QDate.fromString(self.intern.start_date, "yyyy-MM-dd")
            )
        if self.intern.end_date:
            self.date_end.setDate(QDate.fromString(self.intern.end_date, "yyyy-MM-dd"))

    def save_data(self):
        """
        Valida os dados e aceita o fechamento.
        """
        if not self.txt_name.text().strip():
            QMessageBox.warning(self, "Erro", "O nome do aluno é obrigatório.")
            return

        if not self.txt_ra.text().strip():
            QMessageBox.warning(self, "Erro", "O RA é obrigatório.")
            return

        start_str = self.date_start.date().toString("dd/MM/yyyy")
        end_str = self.date_end.date().toString("dd/MM/yyyy")

        try:
            validate_date_range(start_str, end_str)
        except ValueError as e:
            QMessageBox.warning(self, "Datas Inválidas", str(e))
            return

        self.accept()

    def get_data(self) -> Intern:
        current_id = self.intern.intern_id if self.intern else None
        selected_venue_id = self.combo_venue.currentData()

        # CORREÇÃO 3: Removemos 'status=...' pois é uma property calculada, não um campo.
        return Intern(
            intern_id=current_id,
            name=self.txt_name.text().strip(),
            registration_number=self.txt_ra.text().strip(),
            email=self.txt_email.text().strip(),
            venue_id=selected_venue_id,
            term=self.combo_term.currentText(),
            start_date=self.date_start.date().toString("yyyy-MM-dd"),
            end_date=self.date_end.date().toString("yyyy-MM-dd"),
        )
