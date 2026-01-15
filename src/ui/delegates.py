# src/ui/delegates.py
from PySide6.QtWidgets import QStyledItemDelegate, QStyle
from PySide6.QtGui import QColor, QPainter, QBrush, QPainterPath
from PySide6.QtCore import Qt
from ui.styles import COLORS

class StatusDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        text = index.data()
        if not text:
            super().paint(painter, option, index)
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.fillRect(option.rect, QColor(COLORS["white"])) 

        # Define cores da pílula
        bg_color = QColor(COLORS["secondary"])
        text_color = QColor(COLORS["white"])
        
        lower_text = str(text).lower()
        if "concluído" in lower_text or "ativo" in lower_text:
            bg_color = QColor(COLORS["success"])
        elif "pendente" in lower_text or "reprovado" in lower_text:
            bg_color = QColor(COLORS["danger"])
        elif "andamento" in lower_text:
            bg_color = QColor(COLORS["primary"])
        elif "cancelado" in lower_text:
            bg_color = QColor(COLORS["dark"])

        # Pílula
        rect = option.rect.adjusted(15, 8, -15, -8)
        path = QPainterPath()
        path.addRoundedRect(rect, 10, 10)
        
        painter.fillPath(path, QBrush(bg_color))

        # Texto
        painter.setPen(text_color)
        font = painter.font()
        font.setBold(True)
        font.setPointSize(9)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(text))

        painter.restore()