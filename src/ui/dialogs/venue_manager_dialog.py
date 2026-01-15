from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QHeaderView,
    QAbstractItemView, QMessageBox, QLabel, QFrame, QWidget
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QPalette
import qtawesome as qta

from services.venue_service import VenueService
from ui.dialogs.venue_dialog import VenueDialog
from ui.styles import COLORS

class VenueManagerDialog(QDialog):
    def __init__(self, parent, service: VenueService):
        super().__init__(parent)
        self.service = service
        self.setWindowTitle("Gerenciar Locais de Estágio")
        self.resize(750, 500)

        # Estilo Base do Dialog
        self.setStyleSheet(f"QDialog {{ background-color: {COLORS['light']}; }}")

        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # --- Cabeçalho ---
        header = QHBoxLayout()
        icon_lbl = QLabel()
        icon_lbl.setPixmap(qta.icon('fa5s.hospital-user', color=COLORS['primary']).pixmap(QSize(32, 32)))
        
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        lbl_title = QLabel("Locais de Estágio")
        lbl_title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {COLORS['dark']};")
        lbl_sub = QLabel("Gerencie hospitais, clínicas e parceiros conveniados.")
        lbl_sub.setStyleSheet(f"font-size: 12px; color: {COLORS['secondary']};")
        
        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_sub)
        header.addWidget(icon_lbl)
        header.addLayout(title_box)
        header.addStretch()
        layout.addLayout(header)

        # --- Barra de Ferramentas ---
        toolbar = QHBoxLayout()
        
        self.btn_new = QPushButton(" Novo Local")
        self.btn_new.setIcon(qta.icon('fa5s.plus', color='white'))
        self.btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_new.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']}; color: white; border: none; 
                padding: 8px 15px; border-radius: 6px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {COLORS['primary_hover']}; }}
        """)
        self.btn_new.clicked.connect(self.new_venue)
        
        self.btn_edit = QPushButton(" Editar")
        self.btn_edit.setIcon(qta.icon('fa5s.pen', color=COLORS['dark']))
        self.btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_edit.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['white']}; color: {COLORS['dark']}; border: 1px solid {COLORS['border']}; 
                padding: 8px 15px; border-radius: 6px; font-weight: 600;
            }}
            QPushButton:hover {{ background-color: {COLORS['light']}; }}
        """)
        self.btn_edit.clicked.connect(self.edit_venue)

        self.btn_del = QPushButton(" Excluir")
        self.btn_del.setIcon(qta.icon('fa5s.trash-alt', color=COLORS['danger']))
        self.btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_del.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['white']}; color: {COLORS['danger']}; border: 1px solid {COLORS['border']}; 
                padding: 8px 15px; border-radius: 6px; font-weight: 600;
            }}
            QPushButton:hover {{ background-color: #F8D7DA; border: 1px solid #F5C6CB; }}
        """)
        self.btn_del.clicked.connect(self.delete_venue)

        toolbar.addWidget(self.btn_new)
        toolbar.addWidget(self.btn_edit)
        toolbar.addStretch()
        toolbar.addWidget(self.btn_del)
        layout.addLayout(toolbar)

        # --- Tabela ---
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Local", "Supervisor", "Telefone"])
        self.table.setColumnHidden(0, True) # Oculta ID

        # Configuração da Paleta (Cor de Seleção)
        palette = self.table.palette()
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#BBDEFB")) # Azul Suave
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(COLORS['dark']))
        self.table.setPalette(palette)

        # Estilo CSS da Tabela
        self.table.setStyleSheet(f"""
            QTableWidget {{ 
                background-color: {COLORS['white']}; 
                border-radius: 8px; 
                border: 1px solid {COLORS['border']};
                gridline-color: transparent;
                outline: none;
                alternate-background-color: #FAFAFA;
            }}
            QHeaderView::section {{
                background-color: {COLORS['white']};
                color: {COLORS['medium']};
                padding: 8px;
                border: none;
                border-bottom: 2px solid {COLORS['light']};
                font-weight: bold;
            }}
            QTableWidget::item:hover {{
                background-color: #E0E0E0;
                color: {COLORS['dark']};
            }}
            QTableWidget::item:selected {{
                background-color: #BBDEFB;
                color: {COLORS['dark']};
                border: none;
            }}
        """)

        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.doubleClicked.connect(self.edit_venue)

        layout.addWidget(self.table)
        
        # Botão Fechar
        btn_close = QPushButton("Fechar")
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet(f"background: transparent; color: {COLORS['secondary']}; border: none;")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignRight)

    def _load_data(self):
        self.venues = self.service.get_all()
        self.table.setRowCount(0)

        for row, venue in enumerate(self.venues):
            self.table.insertRow(row)
            self.table.setRowHeight(row, 45)
            
            self.table.setItem(row, 0, QTableWidgetItem(str(venue.venue_id)))
            
            # Nome em Negrito
            item_name = QTableWidgetItem(venue.venue_name)
            font = item_name.font(); font.setBold(True); item_name.setFont(font)
            self.table.setItem(row, 1, item_name)
            
            self.table.setItem(row, 2, QTableWidgetItem(venue.supervisor_name or "-"))
            self.table.setItem(row, 3, QTableWidgetItem(venue.supervisor_phone or "-"))

    def get_selected_venue(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return None

        # Pylance Guard: Item pode ser None
        item_id = self.table.item(rows[0].row(), 0)
        if item_id is None:
            return None

        venue_id = int(item_id.text())

        # Busca segura na lista (assumindo que self.venues está sincronizado)
        return next((v for v in self.venues if v.venue_id == venue_id), None)

    def new_venue(self):
        dialog = VenueDialog(self)
        if dialog.exec():
            try:
                self.service.add_new_venue(dialog.get_data())
                self._load_data()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao salvar: {e}")

    def edit_venue(self):
        venue = self.get_selected_venue()
        if not venue:
            QMessageBox.warning(self, "Atenção", "Selecione um local para editar.")
            return

        dialog = VenueDialog(self, venue)
        if dialog.exec():
            try:
                self.service.update_venue(dialog.get_data())
                self._load_data()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao atualizar: {e}")

    def delete_venue(self):
        venue = self.get_selected_venue()
        if not venue:
            return

        confirm = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir '{venue.venue_name}'?\nIsso pode afetar alunos vinculados!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                self.service.delete_venue(venue)
                self._load_data()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao excluir: {e}")