from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QGroupBox,
    QPushButton,
    QHBoxLayout,
    QFileDialog,
    QLabel,
)
from PySide6.QtCore import Qt, QSettings, QSize
import qtawesome as qta
from ui.styles import COLORS


class SettingsDialog(QDialog):
    """
    Janela para configurar dados globais do sistema (Cabeçalho do PDF, etc).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurações do Sistema")
        self.resize(550, 400)

        # Estilo
        self.setStyleSheet(f"""
            QDialog {{ background-color: {COLORS["light"]}; }}
            QGroupBox {{ 
                font-weight: bold; 
                border: 1px solid {COLORS["border"]}; 
                border-radius: 6px; 
                margin-top: 10px; 
                padding-top: 15px;
                color: {COLORS["dark"]};
            }}
            QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }}
            
            QLineEdit {{
                background-color: {COLORS["white"]};
                border: 1px solid {COLORS["border"]};
                border-radius: 4px;
                padding: 8px;
                color: {COLORS["dark"]};
            }}
            QLineEdit:focus {{ border: 1px solid {COLORS["primary"]}; }}
        """)

        # Persistência via QSettings (padrão do Qt, salva no Registro/Ini)
        self.settings = QSettings("MyOrganization", "InternManager2026")

        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header
        header = QHBoxLayout()
        icon = QLabel()
        icon.setPixmap(
            qta.icon("fa5s.cog", color=COLORS["medium"]).pixmap(QSize(32, 32))
        )
        lbl_title = QLabel("Parâmetros Gerais")
        lbl_title.setStyleSheet(
            f"font-size: 20px; font-weight: bold; color: {COLORS['dark']};"
        )
        header.addWidget(icon)
        header.addWidget(lbl_title)
        header.addStretch()
        layout.addLayout(header)

        # Grupo: Cabeçalho dos Relatórios
        group = QGroupBox("Personalização dos Relatórios (PDF)")
        form = QFormLayout()
        form.setSpacing(15)

        self.txt_institution = QLineEdit()
        self.txt_institution.setPlaceholderText("Ex: Faculdade de Tecnologia...")

        self.txt_supervisor = QLineEdit()
        self.txt_supervisor.setPlaceholderText("Ex: Prof. Dr. Fulano de Tal")

        self.txt_city = QLineEdit()
        self.txt_city.setPlaceholderText("Ex: São Paulo - SP")

        # Seleção de Logo
        self.txt_logo_path = QLineEdit()
        self.txt_logo_path.setReadOnly(True)
        self.txt_logo_path.setPlaceholderText("Caminho da imagem do logo...")

        btn_logo = QPushButton(" Buscar Imagem")
        btn_logo.setIcon(qta.icon("fa5s.image", color=COLORS["dark"]))
        btn_logo.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_logo.clicked.connect(self.select_logo)

        logo_layout = QHBoxLayout()
        logo_layout.addWidget(self.txt_logo_path)
        logo_layout.addWidget(btn_logo)

        # Labels bold
        def lbl(t):
            lbl_style = QLabel(t)
            lbl_style.setStyleSheet("font-weight: bold;")
            return lbl_style

        form.addRow(lbl("Nome da Instituição:"), self.txt_institution)
        form.addRow(lbl("Nome do Coordenador:"), self.txt_supervisor)
        form.addRow(lbl("Cidade/UF:"), self.txt_city)
        form.addRow(lbl("Logotipo:"), logo_layout)

        group.setLayout(form)
        layout.addWidget(group)
        layout.addStretch()

        # Botões
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setStyleSheet(
            f"background: transparent; color: {COLORS['secondary']}; border: none;"
        )
        btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton(" Salvar Configurações")
        self.btn_save.setIcon(qta.icon("fa5s.save", color="white"))
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS["primary"]}; color: white; border: none; 
                padding: 10px 20px; border-radius: 6px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {COLORS["primary_hover"]}; }}
        """)
        self.btn_save.clicked.connect(self.save_settings)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(self.btn_save)
        layout.addLayout(btn_layout)

    def select_logo(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Logomarca", "", "Imagens (*.png *.jpg *.jpeg)"
        )
        if path:
            self.txt_logo_path.setText(path)

    def _load_data(self):
        # QSettings retorna 'None' se a chave não existir, convertemos para string vazia
        self.txt_institution.setText(
            str(self.settings.value("institution_name", "") or "")
        )
        self.txt_supervisor.setText(
            str(self.settings.value("coordinator_name", "") or "")
        )
        self.txt_city.setText(str(self.settings.value("city_state", "") or ""))
        self.txt_logo_path.setText(str(self.settings.value("logo_path", "") or ""))

    def save_settings(self):
        self.settings.setValue("institution_name", self.txt_institution.text().strip())
        self.settings.setValue("coordinator_name", self.txt_supervisor.text().strip())
        self.settings.setValue("city_state", self.txt_city.text().strip())
        self.settings.setValue("logo_path", self.txt_logo_path.text().strip())

        QMessageBox.information(self, "Salvo", "Configurações atualizadas com sucesso!")
        self.accept()
