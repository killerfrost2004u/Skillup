# 🚀 Skillup

![GitHub repo size](https://img.shields.io/github/repo-size/killerfrost2004u/Skillup)
![GitHub contributors](https://img.shields.io/github/contributors/killerfrost2004u/Skillup)
![GitHub stars](https://img.shields.io/github/stars/killerfrost2004u/Skillup?style=social)

**Skillup** is a high-performance, web-based e-learning platform designed to provide structured learning paths, real-time progress tracking, and an integrated local AI assistant. Built with professional software engineering principles, Skillup offers a seamless educational experience for self-taught developers and students alike.

---

## 📖 Table of Contents
- [🌟 Key Features](#-key-features)
- [🏗️ Architecture & Design Patterns](#️-architecture--design-patterns)
- [🛠️ Tech Stack](#️-tech-stack)
- [📂 Project Structure](#-project-structure)
- [⚡ Getting Started](#-getting-started)
- [📡 API Endpoints](#-api-endpoints)
- [🧪 Testing](#-testing)
- [🤝 Collaborators](#-collaborators)
- [📄 License](#-license)

---

## 🌟 Key Features

*   **🤖 Local AI Learning Assistant:** Integrated Chatbot powered by local LLMs (Mistral/Llama 3) via **Ollama**. Ensures data privacy and eliminates API costs.
*   **📊 Smart Progress Tracking:** Dynamic progress visualization using a hybrid SQL/Local Storage system. Includes sequential lecture unlocking (90% watch time requirement).
*   **🔐 Secure Authentication:** JWT-based user registration and login system with persistent sessions.
*   **🛣️ Structured Learning Tracks:** Curated paths for Frontend, Backend, Python, and Software Development.
- **📱 Responsive & Interactive UI:** Modern interface built with CSS Glassmorphism, Neumorphism, and Lottie animations.
*   **📰 Tech Blog:** Integrated blog featuring the latest trends in AI, Programming, and Soft Skills.

---

## 🏗️ Architecture & Design Patterns

The backend follows a **4-Layered Clean Architecture** to ensure maintainability and scalability:

1.  **API Layer (`/api`):** Handles HTTP requests and JSON responses. Framework-independent design.
2.  **Service Layer (`/services`):** Implements core business logic (Auth, Progress rules, AI strategies).
3.  **Data Access Layer (`/data/repository`):** Centralizes all SQL queries.
4.  **Infrastructure Layer (`/data/db`):** Manages low-level database connections.

### Integrated Design Patterns:
-   **Singleton:** `DatabaseManager` ensures a single connection pool.
-   **Adapter:** Supports both **SQLite** (local) and **PostgreSQL** (production) seamlessly.
-   **Dependency Injection:** Services receive repositories via constructors for easier mocking.
-   **Observer:** Automatically logs/notifies upon course completion.
-   **Strategy:** Dynamic AI provider switching (OpenAI vs. Local Ollama).

---

## 🛠️ Tech Stack

### Frontend
- **Core:** HTML5, Vanilla JavaScript, CSS3
- **Styling:** Custom CSS (Glassmorphism), FontAwesome
- **Animations:** LottieFiles, Swiper.js, Particles.js
- **State Management:** UserStore (Singleton Pattern)

### Backend
- **Framework:** Flask (Python)
- **AI Integration:** Ollama (Local execution)
- **Authentication:** PyJWT
- **Utilities:** Flask-CORS, Python-Dotenv

### Database
- **Adapters:** SQLite (default) and PostgreSQL
- **Schema Management:** Manual scripts for SQL Server and Postgres

---

## 📂 Project Structure

```text
Skillup/
├── Backend/                 # Flask Core
│   ├── api/                 # Blueprint Routes
│   ├── data/                # DB & Repository Patterns
│   ├── services/            # Business Logic
│   └── tests/               # Unit Test Suite
├── frontend/                # Vanilla JS Web App
│   ├── course-player.js     # Main Player Logic
│   └── index.html           # Landing Page
├── Data Base/               # SQL Scripts (Postgres/MSSQL)
├── api/                     # Vercel Serverless Entry
└── requirements.txt         # Python Dependencies
```

---

## ⚡ Getting Started

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com/) (For AI features)
- Node.js (Optional, for Live Server)

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/killerfrost2004u/Skillup.git
    cd Skillup
    ```

2.  **Set up Virtual Environment**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Configure Environment**
    Create a `.env` file in the root:
    ```env
    JWT_SECRET=your_secret_key
    PORT=5000
    # DATABASE_URL=postgresql://user:pass@host/db  # Optional for Postgres
    ```

4.  **Run the Server**
    ```bash
    cd Backend
    python app.py
    ```

5.  **Launch Frontend**
    Open `frontend/index.html` using VS Code Live Server or any static file server.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/register` | User Registration |
| `POST` | `/login` | Authentication & JWT Issuance |
| `POST` | `/chat` | AI Query (requires Ollama) |
| `GET` | `/courses` | Fetch Course Catalog |
| `POST` | `/api/progress/save` | Update Video/Playlist Progress |
| `GET` | `/get-progress/<user_id>` | Retrieve User Dashboard Stats |

---

## 🧪 Testing

The project includes a robust suite of unit tests using `unittest` and `mock`.

**To run backend tests:**
```bash
python -m unittest discover Backend/tests
```

---

## 🤝 Collaborators

- **Ibrahim Yasser** - [@killerfrost2004u](https://github.com/killerfrost2004u) (Backend)
- **Osama Hilalia** - [@osamahilalia-cmd](https://github.com/osamahilalia-cmd) (Frontend/UI)
- **Dina Kamel** - [@dinaaakamelll-ctrl](https://github.com/dinaaakamelll-ctrl) (Frontend/UI)
- **Baraa Mostafa** - [@baraa244](https://github.com/baraa244) (Data)
- **Aya Mohammed** - [@aya878](https://github.com/aya878) (Backend)
- **Sara Osama** (Architecture Design)
- **Eslam EL-Araby** (Data)

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
