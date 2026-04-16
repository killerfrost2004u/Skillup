# 🚀 Skillup

![GitHub repo size](https://img.shields.io/github/repo-size/killerfrost2004u/Skillup)
![GitHub contributors](https://img.shields.io/github/contributors/killerfrost2004u/Skillup)
![GitHub stars](https://img.shields.io/github/stars/killerfrost2004u/Skillup?style=social)
![GitHub fork](https://img.shields.io/github/forks/killerfrost2004u/Skillup?style=social)

**Skillup** is a comprehensive web-based e-learning platform designed to bridge the gap between learning resources and professional goals. It combines structured learning tracks, progress tracking, and an integrated AI assistant to provide a personalized educational experience.

## 📖 Overview

In an era of information overload, **Skillup** helps learners stay focused by providing a clean, intuitive interface to manage courses and visualize progress. Whether you are a self-taught developer or a university student, Skillup acts as your personal learning companion.

The platform features a robust backend powered by **Flask** and **SQL Server**, coupled with an intelligent chatbot integration running entirely on **Local LLMs** to ensure data privacy and eliminate API costs.

## 🌟 Key Features

* **🤖 Local AI Learning Assistant:** Integrated Chatbot powered by local LLMs (like **Mistral** and **Llama 3**) via **Ollama**. It answers student queries in real-time, including Arabic language support, without relying on costly external APIs.
* **📊 Smart Progress Tracking:** Tracks video and playlist completion rates using a hybrid system (SQL & JSON), visualizing growth via dynamic dashboards.
* **🔐 Secure Authentication:** User registration and login system protected by **JWT (JSON Web Tokens)**.
* **🛣️ Structured Learning Tracks:** Curated paths for Frontend, Backend, Python, Full Stack, and Software Testing.
* **📂 Resource Management:** Dynamic handling of courses, lectures, and educational resources.
* **📱 Responsive Design:** Fully optimized interface using HTML5, CSS3, and Bootstrap for desktop and mobile.
* **📰 Tech Blog:** Integrated blog section featuring the latest trends in AI, Programming, and Soft Skills.

## 🛠️ Tech Stack

### Frontend
* **Languages:** HTML5, CSS3, JavaScript
* **Libraries:** Bootstrap, Swiper.js (for sliders), LottieFiles (for animations), FontAwesome
* **Styling:** Custom CSS with responsive layouts

### Backend
* **Framework:** Flask (Python)
* **AI Integration:** Local execution via Ollama (`http://localhost:11434/api/generate`), utilizing the Requests library for communication. Can be easily extended with LangChain or RAG pipelines.
* **Authentication:** PyJWT
* **Utilities:** Flask-CORS, Python-Dotenv

### Database
* **RDBMS:** Microsoft SQL Server
* **Driver:** PyODBC
* **Data Storage:** Hybrid approach using SQL Tables for user data and JSON for lightweight progress caching.

## ⚡ Getting Started

Follow these instructions to get the project up and running on your local machine.

### Prerequisites
Ensure you have the following installed:
* [Python 3.x](https://www.python.org/downloads/)
* [SQL Server](https://www.microsoft.com/en-us/sql-server/sql-server-downloads) (Express or Developer edition)
* [Git](https://git-scm.com/)
* [Ollama](https://ollama.com/) (For running local AI models)

### Installation

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/killerfrost2004u/Skillup.git](https://github.com/killerfrost2004u/Skillup.git)
    cd Skillup
    ```

2.  **Set up the Database**
    * Open SQL Server Management Studio (SSMS).
    * Run the script located in `Data Base/Tabels.sql` to create the `skill_up` database and necessary tables (`Users`, `Courses`, `Tracks`, etc.).

3.  **Start Local AI (Ollama)**
    * Ensure Ollama is running on your machine.
    * Pull the required model (e.g., Mistral or Llama 3) by running:
      ```bash
      ollama run mistral
      ```

4.  **Backend Setup**
    Navigate to the backend directory:
    ```bash
    cd Backend
    ```
    Install Python dependencies:
    ```bash
    pip install -r ../requirements.txt
    ```

5.  **Environment Configuration**
    Create a `.env` file in the `Backend` directory and add your database and JWT credentials:
    ```env
    DB_SERVER=localhost\SQLEXPRESS
    DB_NAME=skill_up
    DB_USERNAME=your_db_user
    DB_PASSWORD=your_db_password
    DB_TRUSTED_CONNECTION=yes
    JWT_SECRET=your_super_secret_key
    ```

6.  **Run the Application**
    Start the Flask server:
    ```bash
    python app.py
    ```
    The API will run at `http://localhost:5000`.

7.  **Launch Frontend**
    Open `frontend/SKILL UP.html` in your browser or use the "Live Server" extension in VS Code.

## 📡 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/register` | Register a new user |
| `POST` | `/login` | Authenticate user and receive JWT |
| `POST` | `/chat` | Send message to Local Ollama AI Bot |
| `GET` | `/test-ollama` | Test connection to the local LLM server |
| `GET` | `/courses` | Retrieve list of available courses |
| `POST` | `/api/progress/save` | Save video completion status |
| `GET` | `/api/progress/<id>/<playlist>` | Get specific playlist progress |

## 🤝 Collaborators

This project is brought to you by an amazing team of developers:

* **Ibrahim Yasser** - [@killerfrost2004u](https://github.com/killerfrost2004u)
* **Osama Hilalia** - [@osamahilalia-cmd](https://github.com/osamahilalia-cmd)
* **Dina Kamel** - [@dinaaakamelll-ctrl](https://github.com/dinaaakamelll-ctrl)
* **Baraa Mostafa** - [@baraa244](https://github.com/baraa244)
* **Aya Mohammed** - [@aya878](https://github.com/aya878)
* **Sara Osama**
* **Eslam EL-Araby**

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---
*If you find this project useful, please give it a star on GitHub! ⭐️*
