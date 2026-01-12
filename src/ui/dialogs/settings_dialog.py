from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QDialogButtonBox,
    QMessageBox,
    QGroupBox,
    QPushButton,
    QHBoxLayout,
    QFileDialog,
)
from PySide6.QtCore import QSettings


class SettingsDialog(QDialog):
    """
    Janela para configurar dados globais do sistema.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurações do Sistema")
        self.resize(500, 350)  # Aumentei um pouco para caber o logo

        # Atenção aqui: Tem que ser igualzinho no ReportService
        self.settings = QSettings("MyOrganization", "InternManager2026")

        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Grupo: Dados Institucionais
        group = QGroupBox("Cabeçalho dos Relatórios")
        form = QFormLayout()

        self.txt_institution = QLineEdit()
        self.txt_institution.setPlaceholderText("Ex: Universidade Federal de...")

        self.txt_supervisor = QLineEdit()
        self.txt_supervisor.setPlaceholderText("Ex: Prof. Rodrigo Noronha de Mello")

        self.txt_city = QLineEdit()
        self.txt_city.setPlaceholderText("Ex: Porto Alegre - RS")

        # --- NOVO: Seletor de Logo ---
        self.txt_logo_path = QLineEdit()
        self.txt_logo_path.setPlaceholderText("Caminho da imagem (PNG/JPG)...")
        self.txt_logo_path.setReadOnly(True)  # Para o usuário não digitar bobagem

        self.btn_logo = QPushButton("📁 Escolher Logo")
        self.btn_logo.clicked.connect(self.select_logo)

        # Layout horizontal para o campo de logo + botão
        logo_layout = QHBoxLayout()
        logo_layout.addWidget(self.txt_logo_path)
        logo_layout.addWidget(self.btn_logo)
        # -----------------------------

        form.addRow("Instituição:", self.txt_institution)
        form.addRow("Coordenação:", self.txt_supervisor)
        form.addRow("Cidade/UF:", self.txt_city)
        form.addRow("Logomarca:", logo_layout)

        group.setLayout(form)
        layout.addWidget(group)

        # Botões
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.save_settings)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def select_logo(self):
        """Abre dialogo para pegar imagem."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Logomarca", "", "Imagens (*.png *.jpg *.jpeg)"
        )
        if path:
            self.txt_logo_path.setText(path)

    def _load_data(self):
        """Carrega os dados salvos anteriormente."""
        # Se retornar None ou objeto vazio, converte para string vazia
        self.txt_institution.setText(
            str(self.settings.value("institution_name", "") or "")
        )
        self.txt_supervisor.setText(
            str(self.settings.value("coordinator_name", "") or "")
        )
        self.txt_city.setText(str(self.settings.value("city_state", "") or ""))
        self.txt_logo_path.setText(str(self.settings.value("logo_path", "") or ""))

    def save_settings(self):
        """Salva os dados no sistema."""
        self.settings.setValue("institution_name", self.txt_institution.text().strip())
        self.settings.setValue("coordinator_name", self.txt_supervisor.text().strip())
        self.settings.setValue("city_state", self.txt_city.text().strip())
        self.settings.setValue("logo_path", self.txt_logo_path.text().strip())

        QMessageBox.information(self, "Sucesso", "Configurações salvas e aplicadas!")
        self.accept()
