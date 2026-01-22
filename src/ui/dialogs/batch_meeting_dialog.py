from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QCheckBox,
    QPushButton,
    QDateEdit,
    QMessageBox,
    QComboBox,
)
from PySide6.QtCore import Qt, QDate
import qtawesome as qta
from ui.styles import COLORS
from core.models.meeting import Meeting


class BatchMeetingDialog(QDialog):
    def __init__(self, parent, intern_service, meeting_service, venue_service):
        super().__init__(parent)
        self.intern_service = intern_service
        self.meeting_service = meeting_service
        self.venue_service = venue_service
        self.interns = []

        self.setWindowTitle("Agendar Reunião em Grupo")
        self.setMinimumSize(500, 600)
        self.setStyleSheet(f"background-color: {COLORS['light']};")

        self._setup_ui()
        self._load_interns()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Título
        lbl = QLabel("Nova Reunião Coletiva")
        lbl.setStyleSheet(
            f"font-size: 20px; font-weight: bold; color: {COLORS['primary']};"
        )
        layout.addWidget(lbl)

        # Filtro de Local
        filter_layout = QHBoxLayout()
        self.combo_venue = QComboBox()
        self.combo_venue.addItem("Todos os Locais", None)
        for v in self.venue_service.get_all():
            self.combo_venue.addItem(v.venue_name, v.venue_id)
        self.combo_venue.currentIndexChanged.connect(self._filter_list)

        filter_layout.addWidget(QLabel("Filtrar por Local:"))
        filter_layout.addWidget(self.combo_venue)
        layout.addLayout(filter_layout)

        # Lista de Alunos (Checkable)
        lbl_sel = QLabel("Selecione os participantes:")
        layout.addWidget(lbl_sel)

        self.list_interns = QListWidget()

        # --- CSS CORRIGIDO PARA O QUADRADINHO ---
        self.list_interns.setStyleSheet(f"""
            QListWidget {{
                background-color: {COLORS["white"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 4px;
                outline: none;
            }}
            QListWidget::item {{
                color: {COLORS["dark"]};
                padding: 8px;
                border-bottom: 1px solid {COLORS["light"]};
            }}
            QListWidget::item:hover {{
                background-color: #F0F0F0;
            }}
            
            /* O Indicador (Quadradinho) */
            QListWidget::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {COLORS["medium"]}; /* Borda cinza quando não marcado */
                border-radius: 4px;
                background-color: {COLORS["white"]};
                margin-right: 10px;
            }}
            
            /* Quando passa o mouse por cima do quadradinho */
            QListWidget::indicator:hover {{
                border-color: {COLORS["primary"]};
            }}

            /* Quando está MARCADO (Checked) */
            QListWidget::indicator:checked {{
                background-color: {COLORS["primary"]}; /* Fundo Azul */
                border-color: {COLORS["primary"]};     /* Borda Azul */
                /* O Qt Fusion desenha um "v" branco automaticamente sobre cores escuras */
            }}
        """)
        # ----------------------------------------

        layout.addWidget(self.list_interns)

        # Checkbox "Marcar Todos"
        self.chk_all = QCheckBox("Selecionar Todos")
        self.chk_all.stateChanged.connect(self._toggle_all)
        layout.addWidget(self.chk_all)

        # Data da Reunião
        date_layout = QHBoxLayout()
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        self.date_edit.setStyleSheet(
            f"padding: 5px; background-color: {COLORS['white']};"
        )

        date_layout.addWidget(QLabel("Data da Reunião:"))
        date_layout.addWidget(self.date_edit)
        layout.addLayout(date_layout)

        # Botão Salvar
        self.btn_save = QPushButton(" Confirmar Agendamento")
        self.btn_save.setIcon(qta.icon("fa5s.check-double", color="white"))
        self.btn_save.setStyleSheet(f"""
            QPushButton {{ background-color: {COLORS["success"]}; color: white; padding: 12px; border-radius: 6px; font-weight: bold; border: none; }}
            QPushButton:hover {{ background-color: #0E6A0E; }}
        """)
        self.btn_save.clicked.connect(self._save_batch)
        layout.addWidget(self.btn_save)

    def _load_interns(self):
        self.all_interns_data = self.intern_service.get_all_interns()
        self._filter_list()

    def _filter_list(self):
        venue_id = self.combo_venue.currentData()
        self.list_interns.clear()

        for intern in self.all_interns_data:
            if venue_id is None or intern.venue_id == venue_id:
                item = QListWidgetItem(
                    f"{intern.name} (RA: {intern.registration_number or 'S/RA'})"
                )

                # Configurações de Item
                item.setData(Qt.ItemDataRole.UserRole, intern.intern_id)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Unchecked)

                self.list_interns.addItem(item)

    def _toggle_all(self, state):
        for i in range(self.list_interns.count()):
            item = self.list_interns.item(i)
            # 2 = Checked, 0 = Unchecked
            is_checked = state == Qt.CheckState.Checked.value or state == 2
            item.setCheckState(
                Qt.CheckState.Checked if is_checked else Qt.CheckState.Unchecked
            )

    def _save_batch(self):
        selected_ids = []
        for i in range(self.list_interns.count()):
            item = self.list_interns.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected_ids.append(item.data(Qt.ItemDataRole.UserRole))

        if not selected_ids:
            QMessageBox.warning(self, "Atenção", "Nenhum aluno selecionado!")
            return

        date_str = self.date_edit.date().toString("yyyy-MM-dd")

        count = 0
        try:
            for iid in selected_ids:
                meeting = Meeting(
                    intern_id=iid, meeting_date=date_str, is_intern_present=True
                )
                # CORREÇÃO DO NOME DO MÉTODO AQUI:
                self.meeting_service.add_new_meeting(meeting)
                count += 1

            QMessageBox.information(
                self, "Sucesso", f"{count} reuniões agendadas com sucesso!"
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao criar reuniões: {e}")
