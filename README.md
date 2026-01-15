# Intern Manager

A desktop application for managing academic internships.

[![Status](https://img.shields.io/badge/Status-In_Development-blue?style=for-the-badge)](https://github.com/mellorn/intern-manager)
[![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-Qt_for_Python-41CD52?style=for-the-badge&logo=qt&logoColor=white)](https://www.qt.io/qt-for-python)
[![uv](https://img.shields.io/badge/Manager-uv-purple?style=for-the-badge)](https://github.com/astral-sh/uv)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE.md)

---

## About the Project

**Intern Manager** is a desktop application designed to streamline the administration of internship programs. It manages student information, practice locations (such as hospitals and clinics), supervisors, and automates document generation and grade calculation based on weighted criteria.

The application is built using the **Repository Pattern** with **Dependency Injection**, which creates a decoupled, testable, and maintainable codebase.

---

## Core Features

*   **Intern Management:** Full CRUD (Create, Read, Update, Delete) operations with data validation for student records.
*   **Venue Management:** Manage internship locations and their supervisors.
*   **Meeting Scheduling:** Track meetings and attendance.
*   **Evaluation System:**
    *   Customizable, weighted grading criteria.
    *   Automatic calculation of averages and final status (Pass/Fail).
    *   A user-friendly interface for grade entry.
*   **Document Generation:** Automatically create essential documents like contracts and attendance sheets.
*   **Batch Import:** Process `.csv` files to add or update multiple records at once using an "upsert" logic.
*   **Data Persistence:** Uses a local SQLite database for simplicity and portability.

---

## Technologies and Prerequisites

To run this project, you will need the following software installed:

*   **Python 3.13+**
*   **uv:** A fast Python package installer and resolver.
    *   *Installation instructions can be found at [uv.astral.sh](https://uv.astral.sh/).*
*   **Git**

---

## How to Run the Project

Follow the steps below to set up and run the application locally.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/mellorn/intern-manager.git
    cd intern-manager
    ```

2.  **Create a virtual environment:**
    This command will create a `.venv` directory in the project folder.
    ```bash
    uv venv
    ```

3.  **Activate the virtual environment:**
    -   On Windows (PowerShell):
        ```powershell
        .venv\Scripts\Activate.ps1
        ```
    -   On macOS/Linux:
        ```bash
        source .venv/bin/activate
        ```

4.  **Install dependencies:**
    This command installs the project dependencies from the `uv.lock` file.
    ```bash
    uv sync
    ```

5.  **Run the application:**
    ```bash
    uv run python src/main.py
    ```

---

## Project Architecture

The project is organized into a modular structure to promote maintainability and scalability.

```
src/
├── core/
│   └── models/          # Domain entities (e.g., Intern, Venue, Grade)
├── data/
│   └── database.py      # Database connector (SQLite)
├── repository/          # Data Access Layer
├── services/            # Service Layer (Business Logic)
├── ui/                  # Presentation Layer (PySide6 / Qt)
│   ├── dialogs/         # Form dialogs (Add/Edit)
│   └── main_window.py   # Main application window
├── utils/               # Utility modules (validators, etc.)
└── main.py              # Application entry point and Dependency Injection setup
```

The architecture is composed of distinct layers:

-   **`core`**: Contains the fundamental data structures (models) of the application.
-   **`data`**: Manages the database connection.
-   **`repository`**: Mediates between the domain and data mapping layers using a collection-like interface for accessing domain objects.
-   **`services`**: Contains the business logic of the application.
-   **`ui`**: The graphical user interface, built with PySide6.

---

## License

This project is licensed under the MIT License. See the [LICENSE.md](LICENSE.md) file for more details.

---

## Developed by

Rodrigo Mello
mellornm@gmail.com
