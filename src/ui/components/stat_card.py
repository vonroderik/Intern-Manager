from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


class StatCard(QFrame):
    """
    Um card estilizado para exibir métricas (KPIs).
    Ex: Total de Alunos, Documentos Pendentes, etc.
    """

    def __init__(self, title: str, value: str, color: str = "#0078D7", icon: str = ""):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)

        # Estilo CSS do Card
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 10px;
                border-left: 5px solid {color};
            }}
            QLabel {{ border: none; background: transparent; }}
        """)

        # Sombra para dar profundidade (Material Design vibes)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)

        self.setFixedSize(220, 100)  # Tamanho fixo para ficar uniforme

        layout = QVBoxLayout(self)

        self.lbl_value = QLabel(value)
        self.lbl_value.setStyleSheet(
            f"font-size: 28px; font-weight: bold; color: {color};"
        )
        self.lbl_value.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.lbl_title = QLabel(f"{icon} {title}")
        self.lbl_title.setStyleSheet("font-size: 14px; color: #666; font-weight: 500;")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignLeft)

        layout.addWidget(self.lbl_value)
        layout.addWidget(self.lbl_title)

    def update_value(self, new_value: str):
        self.lbl_value.setText(str(new_value))
