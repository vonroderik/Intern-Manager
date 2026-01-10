from typing import Optional
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLineEdit,
    QDialogButtonBox,
    QVBoxLayout,
    QDateEdit,
    QComboBox,  # Adicionado
)
from PySide6.QtCore import QDate
from core.models.intern import Intern
from services.venue_service import VenueService  # Adicionado


class InternDialog(QDialog):
    """
    Dialog window for creating or editing an Intern record.
    Includes Venue selection via ComboBox.
    """

    def __init__(
        self, parent, venue_service: VenueService, intern: Optional[Intern] = None
    ):
        """
        Initializes the dialog.

        Args:
            parent: Parent widget.
            venue_service: Service to fetch available venues.
            intern: Intern object to edit (None for create).
        """
        super().__init__(parent)
        self.intern = intern
        self.venue_service = venue_service

        self.setWindowTitle("Ficha do Estagiário")
        self.setMinimumWidth(400)

        self._setup_ui()

        # Carrega os locais na combobox
        self.load_venues()

        # Se for edição, preenche os campos
        if self.intern:
            self.load_data()

    def _setup_ui(self):
        """Configures the visual elements."""
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.form_layout = QFormLayout()

        # Input Widgets
        self.txt_name = QLineEdit()
        self.txt_ra = QLineEdit()
        self.txt_email = QLineEdit()
        self.txt_term = QLineEdit()
        self.combo_venue = QComboBox()

        # Date Widgets
        self.date_start = QDateEdit()
        self.date_start.setCalendarPopup(True)
        self.date_start.setDisplayFormat("dd/MM/yyyy")
        self.date_start.setDate(QDate.currentDate())

        self.date_end = QDateEdit()
        self.date_end.setCalendarPopup(True)
        self.date_end.setDisplayFormat("dd/MM/yyyy")
        self.date_end.setDate(QDate.currentDate().addMonths(6))

        # Adding rows to form
        self.form_layout.addRow("Nome Completo:", self.txt_name)
        self.form_layout.addRow("RA (Matrícula):", self.txt_ra)
        self.form_layout.addRow("E-mail:", self.txt_email)
        self.form_layout.addRow("Semestre:", self.txt_term)
        self.form_layout.addRow("Local de Estágio:", self.combo_venue)  # Nova linha
        self.form_layout.addRow("Início do Estágio:", self.date_start)
        self.form_layout.addRow("Previsão de Fim:", self.date_end)

        self.main_layout.addLayout(self.form_layout)

        # Buttons
        buttons = (
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.main_layout.addWidget(self.button_box)

    def load_venues(self):
        """
        Fetches venues from the database and populates the ComboBox.
        """
        self.combo_venue.clear()
        self.combo_venue.addItem("Selecione um local...", None)

        try:
            venues = self.venue_service.get_all()
            for v in venues:
                self.combo_venue.addItem(v.venue_name, v.venue_id)
        except Exception as e:
            print(f"Erro ao carregar locais: {e}")

    def load_data(self):
        """
        Populates the form fields with data from the provided Intern object.
        """

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

        # Selecionar o Local correto na ComboBox
        if hasattr(self.intern, "venue_id") and self.intern.venue_id:
            index = self.combo_venue.findData(self.intern.venue_id)
            if index >= 0:
                self.combo_venue.setCurrentIndex(index)

        # Trava o RA na edição
        self.txt_ra.setReadOnly(True)
        self.txt_ra.setToolTip("O RA não pode ser alterado após a criação.")

    def get_data(self) -> Intern:
        """
        Retrieves user input and returns an Intern object.
        Includes the selected venue_id.
        """
        current_id = self.intern.intern_id if self.intern else None

        # Pega o ID armazenado no item selecionado da combobox
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
