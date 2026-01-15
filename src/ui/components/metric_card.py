# src/ui/components/metric_card.py
from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGraphicsDropShadowEffect,
)
from PySide6.QtCore import QSize
from PySide6.QtGui import QColor
import qtawesome as qta
from ui.styles import COLORS


class MetricCard(QFrame):
    """Card Visual para o Dashboard."""

    def __init__(self, title, value, icon_name, color_key="primary"):
        super().__init__()
        self.setStyleSheet(f"""
            MetricCard {{
                background-color: {COLORS["white"]};
                border-radius: 8px;
                border: 1px solid {COLORS["border"]};
            }}
        """)

        # Sombra suave
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Ícone
        lbl_icon = QLabel()
        icon = qta.icon(icon_name, color=COLORS.get(color_key, COLORS["primary"]))
        lbl_icon.setPixmap(icon.pixmap(QSize(48, 48)))
        layout.addWidget(lbl_icon)

        # Textos
        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)

        lbl_title = QLabel(title.upper())
        lbl_title.setStyleSheet(
            f"color: {COLORS['medium']}; font-size: 12px; font-weight: bold;"
        )

        # Guardamos referência ao label de valor para atualizar depois
        self.lbl_value = QLabel(str(value))
        self.lbl_value.setStyleSheet(
            f"color: {COLORS['dark']}; font-size: 28px; font-weight: 900;"
        )

        text_layout.addWidget(lbl_title)
        text_layout.addWidget(self.lbl_value)
        layout.addLayout(text_layout)
        layout.addStretch()

    def set_value(self, value):
        self.lbl_value.setText(str(value))
