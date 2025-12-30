# 🎓 Intern Manager 2026

![Status](https://img.shields.io/badge/Status-Em_Desenvolvimento-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyQt6](https://img.shields.io/badge/PyQt6-Qt_for_Python-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![uv](https://img.shields.io/badge/Gerenciador-uv-purple?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)


> Um sistema de desktop robusto para a gestão completa de estágios acadêmicos, desde o cadastro de alunos até a avaliação final.

---

## 🎯 Sobre o Projeto

O **Intern Manager 2026** é uma aplicação desktop desenvolvida para simplificar e centralizar a gestão de programas de estágio. O sistema gerencia o cadastro de alunos, locais de prática (hospitais, clínicas), supervisores e automatiza a geração de documentos e o cálculo de notas com base em critérios ponderados.

A arquitetura foi desenhada seguindo o padrão **Repository Pattern** com **Injeção de Dependência**, garantindo um código desacoplado, testável e de fácil manutenção.

---

## ✨ Funcionalidades Principais

*   **👥 Gestão de Estagiários:** CRUD completo com validações de dados (RA, datas).
*   **🏥 Gestão de Locais (Venues):** Cadastro de locais de estágio e seus respectivos supervisores.
*   **🗓️ Agendamento de Reuniões:** Controle de reuniões e presenças.
*   **📊 Sistema de Avaliação:**
    *   Critérios de nota personalizáveis com pesos.
    *   Cálculo automático de média e status (Aprovado/Reprovado).
    *   Interface de lançamento de notas amigável.
*   **📄 Geração de Documentos:** Criação automática de "kits" de documentos essenciais (Contratos, Fichas de Frequência, etc.).
*   **📥 Importação em Lote:** Processamento de arquivos `.csv` para adicionar ou atualizar múltiplos registros de uma só vez (lógica de *Upsert*).
*   **🗄️ Persistência de Dados:** Uso de banco de dados SQLite local para simplicidade e portabilidade.

---

## 🛠️ Tecnologias e Pré-requisitos

Para executar este projeto, você precisará ter os seguintes softwares instalados:

*   **Python 3.11+**
*   **uv:** Um instalador e gerenciador de pacotes Python extremamente rápido.
    *   *Instrução de instalação em [uv.astral.sh](https://uv.astral.sh/)*.
*   **Git**

---

## 🚀 Como Executar o Projeto

Siga os passos abaixo para configurar e rodar a aplicação localmente.

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/intern-manager.git
cd intern-manager

# 2. Crie o ambiente virtual com uv
# (Isso criará uma pasta .venv no diretório)
uv venv

# 3. Ative o ambiente virtual
# No Windows (PowerShell):
.venv\Scripts\Activate.ps1
# No macOS/Linux:
source .venv/bin/activate

# 4. Instale as dependências a partir do arquivo de lock
uv sync

# 5. Rode a aplicação
uv run python src/main.py
```

---

## 🏛️ Arquitetura do Projeto

O projeto segue uma estrutura modular estrita para facilitar a manutenção e escalar de forma organizada.

```text
src/
├── core/
│   └── models/          # Entidades de domínio (Intern, Venue, Grade...)
├── data/
│   ├── database.py      # Conector do banco de dados (SQLite)
├── repository/          # Camada de Acesso a Dados (Data Access Layer)
├── services/            # Camada de Serviço (Regras de Negócio)
├── ui/                  # Camada de Apresentação (PyQt6 / Qt)
│   ├── dialogs/         # Janelas de formulário (Adicionar/Editar)
│   └── main_window.py   # Janela principal da aplicação
├── utils/               # Módulos utilitários (validadores, etc.)
└── main.py              # Ponto de entrada e Injeção de Dependências
```

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE.md) para mais detalhes.
