from typing import Optional
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QLabel,
    QPushButton,
    QDoubleSpinBox,
    QFrame,
)
from PySide6.QtCore import Qt, QSize
import qtawesome as qta

from core.models.evaluation_criteria import EvaluationCriteria
from ui.styles import COLORS


class CriteriaDialog(QDialog):
    """
    Formulário para Criar ou Editar um Critério de Avaliação.
    """

    def __init__(self, parent=None, criteria: Optional[EvaluationCriteria] = None):
        super().__init__(parent)
        self.criteria = criteria
        self.setWindowTitle("Editar Critério" if criteria else "Novo Critério")
        self.setMinimumWidth(400)

        # Estilo CSS
        self.setStyleSheet(f"""
            QDialog {{ background-color: {COLORS["white"]}; }}
            
            QLabel {{ 
                color: {COLORS["medium"]}; 
                font-size: 12px; 
                font-weight: bold; 
                margin-top: 5px;
            }}
            
            QLineEdit, QDoubleSpinBox {{
                background-color: {COLORS["light"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                color: {COLORS["dark"]};
            }}
            QLineEdit:focus, QDoubleSpinBox:focus {{ 
                background-color: {COLORS["white"]};
                border: 1px solid {COLORS["primary"]}; 
            }}
            
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
                width: 0px; 
                border: none;
            }}
        """)

        self._setup_ui()
        if self.criteria:
            self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # --- Cabeçalho ---
        header = QHBoxLayout()
        icon_lbl = QLabel()
        icon_lbl.setPixmap(
            qta.icon("fa5s.clipboard-list", color=COLORS["primary"]).pixmap(
                QSize(28, 28)
            )
        )

        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        lbl_title = QLabel("Dados do Critério")
        lbl_title.setStyleSheet(f"font-size: 16px; color: {COLORS['dark']}; margin: 0;")

        title_box.addWidget(lbl_title)
        header.addWidget(icon_lbl)
        header.addLayout(title_box)
        header.addStretch()
        layout.addLayout(header)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"color: {COLORS['border']};")
        layout.addWidget(line)

        # --- Campos ---
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("Ex: Prova Teórica, Seminário...")

        self.spin_weight = QDoubleSpinBox()
        self.spin_weight.setRange(0.0, 10.0)
        self.spin_weight.setSingleStep(0.5)
        self.spin_weight.setSuffix(" pts")
        self.spin_weight.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spin_weight.setStyleSheet(
            f"color: {COLORS['primary']}; font-weight: bold; font-size: 16px;"
        )

        self.txt_description = QLineEdit()
        self.txt_description.setPlaceholderText("Detalhes opcionais...")

        layout.addWidget(QLabel("Nome do Critério *"))
        layout.addWidget(self.txt_name)

        layout.addWidget(QLabel("Peso (Nota Máxima)"))
        layout.addWidget(self.spin_weight)

        layout.addWidget(QLabel("Descrição"))
        layout.addWidget(self.txt_description)

        layout.addStretch()

        # --- Botões ---
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["light"]}; color: {COLORS["medium"]}; border: none;
                padding: 10px 20px; border-radius: 6px; font-weight: 600;
            }}
            QPushButton:hover {{ background-color: #E1DFDD; color: {COLORS["dark"]}; }}
        """)
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton("Salvar")
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setIcon(qta.icon("fa5s.check", color="white"))
        self.btn_save.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["primary"]}; color: white; border: none;
                padding: 10px 25px; border-radius: 6px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {COLORS["primary_hover"]}; }}
        """)
        self.btn_save.clicked.connect(self.validate_and_accept)

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        layout.addLayout(btn_layout)

    def _load_data(self):
        if not self.criteria:
            return
        self.txt_name.setText(self.criteria.name)
        self.spin_weight.setValue(self.criteria.weight)
        if self.criteria.description:
            self.txt_description.setText(self.criteria.description)

    def validate_and_accept(self):
        if not self.txt_name.text().strip():
            self.txt_name.setPlaceholderText("NOME É OBRIGATÓRIO!")
            self.txt_name.setFocus()
            return
        self.accept()

    def get_data(self) -> EvaluationCriteria:
        c_id = self.criteria.criteria_id if self.criteria else None

        # CORREÇÃO: Argumento 'is_active' removido, pois não existe no modelo
        return EvaluationCriteria(
            criteria_id=c_id,
            name=self.txt_name.text().strip(),
            weight=self.spin_weight.value(),
            description=self.txt_description.text().strip(),
        )
