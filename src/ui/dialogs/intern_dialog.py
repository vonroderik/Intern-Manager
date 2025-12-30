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
    """
    Dialog window for creating or editing an Intern record.

    This dialog handles the data entry for personal and academic information.
    When editing an existing intern, the Registration Number (RA) field is
    locked to preserve data integrity (and your sanity).

    Attributes:
        intern (Optional[Intern]): The intern object being edited, or None if creating new.
    """

    def __init__(self, parent=None, intern: Optional[Intern] = None):
        """
        Initializes the dialog.

        Args:
            parent (QWidget): Parent widget.
            intern (Optional[Intern]): Intern object to edit. If None, the dialog
                starts in 'Create' mode with empty fields.
        """
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

        self.main_layout.addLayout(self.form_layout)

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
        """
        Populates the form fields with data from the provided Intern object.

        Sets the RA (Registration Number) field to Read-Only to prevent
        primary key modifications during updates.
        """
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

    def get_data(self) -> Intern:
        """
        Retrieves user input from the form widgets.

        Converts QDate objects to ISO 8601 strings (YYYY-MM-DD) suitable
        for database storage.

        Returns:
            dict: A dictionary containing the raw form data.
        """
        current_id = self.intern.intern_id if self.intern else None
                
        return Intern(
                intern_id=current_id,
                name=self.txt_name.text().strip(),
                registration_number=self.txt_ra.text().strip(),
                email=self.txt_email.text().strip() or None, # Converte string vazia para None
                term=self.txt_term.text().strip(),
                start_date=self.date_start.date().toString("yyyy-MM-dd"),
                end_date=self.date_end.date().toString("yyyy-MM-dd"),
                # Adicione working_hours/days se tiver os campos na tela
                )