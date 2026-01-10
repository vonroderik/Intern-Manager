from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QPushButton,
    QTextEdit,
    QMessageBox,
    QWidget,
    QHBoxLayout,
)
from PySide6.QtCore import Qt
from core.models.intern import Intern
from core.models.observation import Observation
from services.observation_service import ObservationService


class ObservationDialog(QDialog):
    def __init__(self, parent, intern: Intern, service: ObservationService):
        super().__init__(parent)
        self.intern = intern
        self.service = service

        self.setWindowTitle(f"Observações: {self.intern.name}")
        self.resize(500, 600)

        self._setup_ui()
        self.load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # --- Histórico ---
        layout.addWidget(QLabel("Histórico:"))
        self.list_widget = QListWidget()
        self.list_widget.setWordWrap(True)
        layout.addWidget(self.list_widget)

        # Botão deletar item selecionado
        self.btn_del = QPushButton("🗑️ Apagar Selecionada")
        self.btn_del.setStyleSheet(
            "color: #d9534f; border: 1px solid #ccc; padding: 5px;"
        )
        self.btn_del.clicked.connect(self.delete_selected)
        layout.addWidget(self.btn_del)

        # Divisória
        line = QWidget()
        line.setFixedHeight(1)
        line.setStyleSheet("background-color: #ccc; margin: 10px 0;")
        layout.addWidget(line)

        # --- Nova Observação ---
        layout.addWidget(QLabel("Nova anotação:"))

        self.txt_new = QTextEdit()
        self.txt_new.setPlaceholderText(
            "Escreva aqui (ex: Esqueceu o jaleco pela 3ª vez...)"
        )
        self.txt_new.setMaximumHeight(100)
        layout.addWidget(self.txt_new)

        # Botões de Ação
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("💾 Salvar")
        self.btn_close = QPushButton("Fechar")

        self.btn_save.setStyleSheet(
            "background-color: #0078D7; color: white; font-weight: bold; padding: 8px;"
        )

        self.btn_save.clicked.connect(self.save_observation)
        self.btn_close.clicked.connect(self.accept)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_close)
        btn_layout.addWidget(self.btn_save)
        layout.addLayout(btn_layout)

    def load_data(self):
        self.list_widget.clear()

        # CORREÇÃO 1: Verificação explícita do ID para o Pylance não chorar
        if self.intern.intern_id is None:
            self.list_widget.addItem("Erro: Estagiário não salvo no banco (sem ID).")
            self.btn_save.setEnabled(False)
            return

        obs_list = self.service.get_intern_observations(self.intern.intern_id)

        for obs in obs_list:
            date_display = obs.last_update if obs.last_update else "Recente"
            text = f"[{date_display}]\n{obs.observation}"

            item = QListWidgetItem(text)

            # CORREÇÃO 2: Caminho correto do Enum no PySide6 (Qt.ItemDataRole.UserRole)
            item.setData(Qt.ItemDataRole.UserRole, obs)

            self.list_widget.addItem(item)

    def save_observation(self):
        # CORREÇÃO 1 (Replay): Garantindo que o ID existe antes de salvar
        if self.intern.intern_id is None:
            QMessageBox.warning(
                self, "Erro", "Não é possível salvar observações para um aluno sem ID."
            )
            return

        content = self.txt_new.toPlainText().strip()
        if not content:
            return

        new_obs = Observation(
            intern_id=self.intern.intern_id,  # Agora o Pylance sabe que aqui é um int seguro
            observation=content,
        )

        try:
            self.service.add_new_observation(new_obs)
            self.txt_new.clear()
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao salvar: {e}")

    def delete_selected(self):
        item = self.list_widget.currentItem()
        if not item:
            return

        # CORREÇÃO 2 (Replay): Usando o caminho completo do Enum para recuperar o objeto
        obs_obj = item.data(Qt.ItemDataRole.UserRole)

        # Validando se recuperou um objeto Observation de verdade (segurança extra)
        if not isinstance(obs_obj, Observation):
            return

        confirm = QMessageBox.question(
            self,
            "Confirmar",
            "Tem certeza que deseja apagar essa anotação?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                self.service.delete_observation(obs_obj)
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao deletar: {e}")
