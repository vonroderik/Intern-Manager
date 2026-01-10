from typing import Optional
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QDoubleSpinBox,
    QDialogButtonBox,
    QMessageBox,
)
from core.models.evaluation_criteria import EvaluationCriteria


class CriteriaDialog(QDialog):
    """
    Form to Create or Edit an Evaluation Criterion.
    """

    def __init__(self, parent=None, criteria: Optional[EvaluationCriteria] = None):
        super().__init__(parent)
        self.criteria = criteria
        self.setWindowTitle("Editar Critério" if criteria else "Novo Critério")
        self.resize(400, 200)
        self._setup_ui()

        if self.criteria:
            self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.txt_name = QLineEdit()
        self.spin_weight = QDoubleSpinBox()
        self.spin_weight.setRange(0.1, 10.0)
        self.spin_weight.setSingleStep(0.5)

        self.txt_description = QLineEdit()

        form.addRow("Nome do Critério:", self.txt_name)
        form.addRow("Peso (Nota Máx):", self.spin_weight)
        form.addRow("Descrição:", self.txt_description)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _load_data(self):
        if not self.criteria:
            return

        self.txt_name.setText(self.criteria.name)
        self.spin_weight.setValue(self.criteria.weight)
        if self.criteria.description:
            self.txt_description.setText(self.criteria.description)

    def validate_and_accept(self):
        if not self.txt_name.text().strip():
            QMessageBox.warning(self, "Erro", "O nome é obrigatório.")
            return
        self.accept()

    def get_data(self) -> EvaluationCriteria:
        c_id = self.criteria.criteria_id if self.criteria else None

        return EvaluationCriteria(
            criteria_id=c_id,
            name=self.txt_name.text().strip(),
            weight=self.spin_weight.value(),
            description=self.txt_description.text().strip(),
        )
