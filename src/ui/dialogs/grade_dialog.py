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
    QLineEdit,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeyEvent
from core.models.intern import Intern
from core.models.grade import Grade
from services.evaluation_criteria_service import EvaluationCriteriaService
from services.grade_service import GradeService


# --- COMPONENTE INTELIGENTE ---
class SmartGradeInput(QDoubleSpinBox):
    """
    Um SpinBox educado que:
    1. Entende ponto como vírgula.
    2. Seleciona tudo ao clicar (para digitar por cima fácil).
    3. Remove as setas feias (opcional).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        # Remove as setinhas (se quiser elas de volta, apague esta linha)
        self.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
        # Alinha o texto à esquerda ou direita? Direita é padrão numérico.
        self.setAlignment(Qt.AlignmentFlag.AlignRight)

    def focusInEvent(self, event):
        """Ao ganhar foco (clique ou Tab), seleciona todo o texto."""
        super().focusInEvent(event)
        # O Timer é um hack necessário do Qt para garantir a seleção após o evento de foco
        QTimer.singleShot(0, self.selectAll)

    def keyPressEvent(self, event: QKeyEvent):
        """Troca Ponto por Vírgula na marra."""
        if event.text() == ".":
            # Simula a digitação de uma vírgula
            new_event = QKeyEvent(
                QKeyEvent.Type.KeyPress,
                Qt.Key.Key_Comma,
                Qt.KeyboardModifier.NoModifier,
                ",",
            )
            super().keyPressEvent(new_event)
        else:
            super().keyPressEvent(event)


# --- FIM DO COMPONENTE ---


class GradeDialog(QDialog):
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

        self.setWindowTitle(f"Avaliação: {self.intern.name}")
        self.setMinimumWidth(450)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # 1. Cabeçalho
        lbl_info = QLabel(
            f"Lançamento de notas para o RA: {self.intern.registration_number}"
        )
        lbl_info.setStyleSheet("color: gray; font-style: italic;")
        self.main_layout.addWidget(lbl_info)

        # 2. Formulário
        self.form_layout = QFormLayout()
        # Dica de UX: Espaço maior entre as linhas para não clicar errado
        self.form_layout.setVerticalSpacing(15)

        self.form_widget = QWidget()
        self.form_widget.setLayout(self.form_layout)
        self.main_layout.addWidget(self.form_widget)

        # 3. Total
        self.lbl_total = QLabel("Nota Final: 0.0")
        self.lbl_total.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #2196F3; margin-top: 10px;"
        )
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.main_layout.addWidget(self.lbl_total)

        # 4. Botões
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

                # USA O NOSSO COMPONENTE INTELIGENTE AGORA
                spinner = SmartGradeInput()

                max_val = float(criterion.weight)
                spinner.setRange(0, max_val)
                spinner.setSingleStep(0.5)

                # Preenche valor
                current_val = grade_map.get(c_id, 0.0)
                spinner.setValue(float(current_val))

                spinner.valueChanged.connect(self.calculate_total)

                self.inputs[c_id] = spinner

                # Estiliza o Label para ficar mais legível
                lbl_text = f"{criterion.name} <span style='color:gray; font-size:10px;'>(Max: {max_val})</span>"
                label = QLabel(lbl_text)

                self.form_layout.addRow(label, spinner)

            self.calculate_total()

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao carregar critérios: {e}")
            self.reject()

    def calculate_total(self):
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
