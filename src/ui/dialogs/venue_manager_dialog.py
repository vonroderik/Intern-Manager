from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHeaderView,
    QAbstractItemView,
    QMessageBox,
)
from services.venue_service import VenueService
from ui.dialogs.venue_dialog import VenueDialog


class VenueManagerDialog(QDialog):
    def __init__(self, parent, service: VenueService):
        super().__init__(parent)
        self.service = service
        self.setWindowTitle("Gerenciar Locais de Estágio")
        self.resize(700, 400)

        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Tabela
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Local", "Supervisor", "Telefone"])

        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.doubleClicked.connect(self.edit_venue)

        layout.addWidget(self.table)

        # Botões
        btn_layout = QHBoxLayout()
        self.btn_new = QPushButton("➕ Novo Local")
        self.btn_edit = QPushButton("✏️ Editar")
        self.btn_del = QPushButton("🗑️ Excluir")

        self.btn_new.setStyleSheet("background-color: #4CAF50; color: white;")
        self.btn_del.setStyleSheet("color: #d9534f; border: 1px solid #d9534f;")

        self.btn_new.clicked.connect(self.new_venue)
        self.btn_edit.clicked.connect(self.edit_venue)
        self.btn_del.clicked.connect(self.delete_venue)

        btn_layout.addWidget(self.btn_new)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_del)
        layout.addLayout(btn_layout)

    def _load_data(self):
        self.venues = self.service.get_all()
        self.table.setRowCount(0)

        for row, venue in enumerate(self.venues):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(venue.venue_id)))
            self.table.setItem(row, 1, QTableWidgetItem(venue.venue_name))
            self.table.setItem(row, 2, QTableWidgetItem(venue.supervisor_name or "-"))
            self.table.setItem(row, 3, QTableWidgetItem(venue.supervisor_phone or "-"))

    def get_selected_venue(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return None

        row_idx = rows[0].row()
        item_id = self.table.item(row_idx, 0)

        if item_id is None:
            return None

        venue_id = int(item_id.text())

        # Busca segura na lista
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
            "Confirmar",
            f"Excluir '{venue.venue_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                self.service.delete_venue(venue)
                self._load_data()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao excluir: {e}")
