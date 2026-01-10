from typing import Optional
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLineEdit,
    QDialogButtonBox,
    QVBoxLayout,
    QMessageBox,
)
from core.models.venue import Venue


class VenueDialog(QDialog):
    """
    Formulário para criar ou editar um Local de Estágio (Venue).
    """

    def __init__(self, parent=None, venue: Optional[Venue] = None):
        super().__init__(parent)
        self.venue = venue
        self.setWindowTitle("Local de Estágio" if venue else "Novo Local")
        self.resize(400, 250)
        self._setup_ui()

        if self.venue:
            self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.txt_name = QLineEdit()
        self.txt_address = QLineEdit()
        self.txt_supervisor = QLineEdit()
        self.txt_email = QLineEdit()
        self.txt_phone = QLineEdit()

        form.addRow("Nome do Local *:", self.txt_name)
        form.addRow("Endereço:", self.txt_address)
        form.addRow("Supervisor:", self.txt_supervisor)
        form.addRow("E-mail:", self.txt_email)
        form.addRow("Telefone:", self.txt_phone)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _load_data(self):
        if not self.venue:
            return
        self.txt_name.setText(self.venue.venue_name)
        self.txt_address.setText(self.venue.venue_address or "")
        self.txt_supervisor.setText(self.venue.supervisor_name or "")
        self.txt_email.setText(self.venue.supervisor_email or "")
        self.txt_phone.setText(self.venue.supervisor_phone or "")

    def validate_and_accept(self):
        if not self.txt_name.text().strip():
            QMessageBox.warning(self, "Erro", "O Nome do Local é obrigatório.")
            return

        # Validar supervisor também se quiser, mas vou deixar opcional por enquanto
        self.accept()

    def get_data(self) -> Venue:
        v_id = self.venue.venue_id if self.venue else None

        return Venue(
            venue_id=v_id,
            venue_name=self.txt_name.text().strip(),
            venue_address=self.txt_address.text().strip() or None,
            supervisor_name=self.txt_supervisor.text().strip() or None,
            supervisor_email=self.txt_email.text().strip() or None,
            supervisor_phone=self.txt_phone.text().strip() or None,
        )
