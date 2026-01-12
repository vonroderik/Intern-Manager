from typing import Dict
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QDialogButtonBox,
    QLabel,
    QDoubleSpinBox,
    QMessageBox,
    QWidget,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeyEvent
from core.models.intern import Intern
from core.models.grade import Grade
from services.evaluation_criteria_service import EvaluationCriteriaService
from services.grade_service import GradeService


class SmartGradeInput(QDoubleSpinBox):
    """
    A customized QDoubleSpinBox with enhanced UX for grade entry.

    Features:
    - Auto-selects text upon receiving focus to facilitate overwriting.
    - Automatically converts '.' to ',' to support numpad usage in locales
      that use commas as decimal separators.
    - Hides standard increment/decrement buttons for a cleaner interface.
    - Aligns text to the right.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
        self.setAlignment(Qt.AlignmentFlag.AlignRight)

    def focusInEvent(self, event):
        """
        Selects all text when the widget gains focus (via click or Tab).
        Uses a singleShot timer to ensure selection happens after Qt's internal processing.
        """
        super().focusInEvent(event)
        QTimer.singleShot(0, self.selectAll)

    def keyPressEvent(self, event: QKeyEvent):
        """
        Intercepts key presses to enforce specific input behaviors.

        Specifically, converts the period (.) key into a comma (,) to prevent
        validation errors in locales where comma is the decimal separator.
        """
        if event.text() == ".":
            new_event = QKeyEvent(
                QKeyEvent.Type.KeyPress,
                Qt.Key.Key_Comma,
                Qt.KeyboardModifier.NoModifier,
                ",",
            )
            super().keyPressEvent(new_event)
        else:
            super().keyPressEvent(event)


class GradeDialog(QDialog):
    """
    Dialog window for entering and editing intern grades.

    This dialog dynamically generates input fields based on the currently
    active evaluation criteria. It calculates the total score in real-time
    and handles persistence via the GradeService.

    Attributes:
        intern (Intern): The intern being evaluated.
        criteria_service (EvaluationCriteriaService): Service to fetch criteria.
        grade_service (GradeService): Service to fetch and save grades.
        inputs (Dict[int, SmartGradeInput]): Mapping of criteria_id to input widgets.
    """

    def __init__(
        self,
        parent,
        intern: Intern,
        criteria_service: EvaluationCriteriaService,
        grade_service: GradeService,
    ):
        super().__init__(parent)
        self.intern = intern
        self.criteria_service = criteria_service
        self.grade_service = grade_service

        self.inputs: Dict[int, SmartGradeInput] = {}

        # Header
        self.setWindowTitle(f"Avaliação: {self.intern.name}")
        self.setMinimumWidth(450)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        lbl_info = QLabel(
            f"Lançamento de notas para o RA: {self.intern.registration_number}"
        )
        lbl_info.setStyleSheet("color: gray; font-style: italic;")
        self.main_layout.addWidget(lbl_info)

        # Form
        self.form_layout = QFormLayout()
        self.form_layout.setVerticalSpacing(15)

        self.form_widget = QWidget()
        self.form_widget.setLayout(self.form_layout)
        self.main_layout.addWidget(self.form_widget)

        # Total
        self.lbl_total = QLabel("Nota Final: 0.0")
        self.lbl_total.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #2196F3; margin-top: 10px;"
        )
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.main_layout.addWidget(self.lbl_total)

        # Buttons
        buttons = (
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.save_grades)
        self.button_box.rejected.connect(self.reject)
        self.main_layout.addWidget(self.button_box)

        self.populate_fields()

    def populate_fields(self):
        """
        Fetches active criteria and existing grades to build the form dynamically.

        For each criterion, a SmartGradeInput is created. If a grade already
        exists for that criterion, the input is pre-filled.
        """
        try:
            criteria_list = self.criteria_service.list_active_criteria()
            existing_grades = self.grade_service.get_grades_by_intern(
                self.intern.intern_id or 0
            )

            grade_map = {
                g.criteria_id: g.value
                for g in existing_grades
                if g.criteria_id is not None
            }

            for criterion in criteria_list:
                c_id = criterion.criteria_id
                if c_id is None:
                    continue

                spinner = SmartGradeInput()

                max_val = float(criterion.weight)
                spinner.setRange(0, max_val)
                spinner.setSingleStep(0.5)

                current_val = grade_map.get(c_id, 0.0)
                spinner.setValue(float(current_val))

                spinner.valueChanged.connect(self.calculate_total)

                self.inputs[c_id] = spinner

                lbl_text = f"{criterion.name} <span style='color:gray; font-size:10px;'>(Max: {max_val})</span>"
                label = QLabel(lbl_text)

                self.form_layout.addRow(label, spinner)

            self.calculate_total()

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao carregar critérios: {e}")
            self.reject()

    def calculate_total(self):
        """
        Sums the values of all inputs and updates the total label.

        Changes the label color to Green (Pass) or Red (Fail) based on a
        threshold of 7.0.
        """
        total = sum(spinner.value() for spinner in self.inputs.values())
        self.lbl_total.setText(f"Nota Final: {total:.2f}")

        if total >= 7.0:
            self.lbl_total.setStyleSheet(
                "font-size: 18px; font-weight: bold; color: #4CAF50; margin-top: 10px;"
            )
        else:
            self.lbl_total.setStyleSheet(
                "font-size: 18px; font-weight: bold; color: #F44336; margin-top: 10px;"
            )

    def save_grades(self):
        """
        Collects data from all inputs and persists them using the GradeService.

        Constructs a list of Grade objects and sends them for batch processing.
        Provides user feedback via QMessageBox upon success or failure.
        """
        grades_to_save = []

        for c_id, spinner in self.inputs.items():
            value = spinner.value()
            grades_to_save.append(
                Grade(
                    intern_id=self.intern.intern_id,  # type: ignore
                    criteria_id=c_id,
                    value=value,
                )
            )

        try:
            self.grade_service.save_batch_grades(grades_to_save)
            QMessageBox.information(self, "Sucesso", "Notas lançadas com sucesso!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Não foi possível salvar: {e}")
