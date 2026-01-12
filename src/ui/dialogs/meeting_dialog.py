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
    QDateEdit,
    QCheckBox,
    QLabel,
    QWidget,
)
from PySide6.QtCore import Qt, QDate
from core.models.intern import Intern
from core.models.meeting import Meeting
from services.meeting_service import MeetingService


class MeetingDialog(QDialog):
    """
    Controle de Supervísão (Datas e Presença).
    """

    def __init__(self, parent, intern: Intern, service: MeetingService):
        super().__init__(parent)
        self.intern = intern
        self.service = service

        self.setWindowTitle(f"Reuniões: {self.intern.name}")
        self.resize(500, 400)

        self._setup_ui()
        self.load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # --- Área de Inserção ---
        top_panel = QWidget()
        top_panel.setStyleSheet("background-color: #f0f0f0; border-radius: 5px;")
        top_layout = QHBoxLayout(top_panel)

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("dd/MM/yyyy")

        self.chk_present = QCheckBox("Aluno Presente?")
        self.chk_present.setChecked(True)

        self.btn_add = QPushButton("Lançar")
        self.btn_add.setStyleSheet(
            "background-color: #0078D7; color: white; font-weight: bold;"
        )
        self.btn_add.clicked.connect(self.add_meeting)

        top_layout.addWidget(QLabel("Data:"))
        top_layout.addWidget(self.date_edit)
        top_layout.addWidget(self.chk_present)
        top_layout.addWidget(self.btn_add)

        layout.addWidget(top_panel)

        # --- Tabela ---
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Data", "Presença"])
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        layout.addWidget(self.table)

        # --- Botão Excluir ---
        self.btn_del = QPushButton("🗑️ Excluir Selecionado")
        self.btn_del.setStyleSheet("color: #d9534f; border: 1px solid #ccc;")
        self.btn_del.clicked.connect(self.delete_meeting)
        layout.addWidget(self.btn_del)

    def load_data(self):
        if self.intern.intern_id is None:
            return

        meetings = self.service.get_meetings_by_intern(self.intern.intern_id)
        self.table.setRowCount(0)

        for row, meeting in enumerate(meetings):
            self.table.insertRow(row)

            # ID
            self.table.setItem(row, 0, QTableWidgetItem(str(meeting.meeting_id)))

            # Data
            # Slice para inverter YYYY-MM-DD -> DD/MM/YYYY ou usar QDate
            date_str = meeting.meeting_date
            try:
                d = QDate.fromString(date_str, "yyyy-MM-dd")
                if d.isValid():
                    date_str = d.toString("dd/MM/yyyy")
            except Exception:
                pass

            self.table.setItem(row, 1, QTableWidgetItem(date_str))

            # Presença
            status = "Presente" if meeting.is_intern_present else "FALTA"
            item_status = QTableWidgetItem(status)
            item_status.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            if not meeting.is_intern_present:
                item_status.setForeground(Qt.GlobalColor.red)
                item_status.setFont(self.table.font())

            self.table.setItem(row, 2, item_status)

    def add_meeting(self):
        if self.intern.intern_id is None:
            QMessageBox.warning(self, "Erro", "Salve o aluno antes de lançar reuniões.")
            return

        # Pega data no formato ISO para o banco
        iso_date = self.date_edit.date().toString("yyyy-MM-dd")
        is_present = self.chk_present.isChecked()

        new_meeting = Meeting(
            intern_id=self.intern.intern_id,
            meeting_date=iso_date,
            is_intern_present=is_present,
        )

        try:
            self.service.add_new_meeting(new_meeting)
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao salvar: {e}")

    def delete_meeting(self):
        row = self.table.currentRow()
        if row < 0:
            return

        confirm = QMessageBox.question(
            self,
            "Apagar",
            "Remover este registro?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.No:
            return

        # Pegando o ID da coluna 0
        item_id = self.table.item(row, 0)
        if not item_id:
            return

        meeting_id = int(item_id.text())

        try:
            # Chama o serviço passando APENAS o INT
            self.service.delete_meeting(meeting_id)
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao excluir: {e}")
