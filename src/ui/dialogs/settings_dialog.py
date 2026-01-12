from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QDialogButtonBox,
    QMessageBox,
    QGroupBox,
)
from PySide6.QtCore import QSettings


class SettingsDialog(QDialog):
    """
    Janela para configurar dados globais do sistema (Instituição, Supervisor, etc).
    Usa QSettings para persistência simples (Registro do Windows / .ini).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurações do Sistema")
        self.resize(450, 250)

        # Instância do QSettings (salva com nome da empresa/app)
        self.settings = QSettings("MyOrganization", "InternManager2026")

        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Grupo: Dados Institucionais
        group = QGroupBox("Dados para Documentos (PDF)")
        form = QFormLayout()

        self.txt_institution = QLineEdit()
        self.txt_institution.setPlaceholderText("Ex: Universidade Federal de...")

        self.txt_supervisor = QLineEdit()
        self.txt_supervisor.setPlaceholderText("Ex: Prof. Dr. Rodrigo Noronha")

        self.txt_city = QLineEdit()
        self.txt_city.setPlaceholderText("Ex: Porto Alegre - RS")

        form.addRow("Nome da Instituição:", self.txt_institution)
        form.addRow("Supervisor(a):", self.txt_supervisor)
        form.addRow("Cidade/Estado:", self.txt_city)

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

    def _load_data(self):
        """Carrega os dados salvos anteriormente."""
        inst = self.settings.value("institution_name", "")
        self.txt_institution.setText(str(inst))

        coord = self.settings.value("coordinator_name", "")
        self.txt_supervisor.setText(str(coord))

        city = self.settings.value("city_state", "")
        self.txt_city.setText(str(city))

    def save_settings(self):
        """Salva os dados no sistema."""
        self.settings.setValue("institution_name", self.txt_institution.text().strip())
        self.settings.setValue("coordinator_name", self.txt_supervisor.text().strip())
        self.settings.setValue("city_state", self.txt_city.text().strip())

        QMessageBox.information(self, "Sucesso", "Configurações salvas com sucesso!")
        self.accept()
