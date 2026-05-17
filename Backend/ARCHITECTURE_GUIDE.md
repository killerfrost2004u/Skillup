# SkillUp Backend: Architectural & Design Patterns Guide

This document explains the professional software engineering principles applied to the SkillUp backend. Use this as a reference for studying and maintaining the system.

---

## 1. The Layered Architecture (Clean Architecture)

We moved from a single "God Object" (`app.py`) to a **4-Layered Architecture**. This separates concerns and ensures that a change in one area (like the database) doesn't break another (like the API routes).

### Layer 1: API Layer (`Backend/api/routes.py`)
*   **Role:** The "Entry/Exit" gate.
*   **Responsibilities:** Handles HTTP requests, parses JSON, and returns JSON responses.
*   **Key Decision:** It does **not** know about SQL. It only talks to the **Service Layer**.
*   **Why:** If you want to switch from Flask to FastAPI or another framework, you only change this layer.

### Layer 2: Service Layer (`Backend/services/`)
*   **Role:** The "Brain" of the application.
*   **Files:** `auth_service.py`, `course_service.py`.
*   **Responsibilities:** Implements Business Logic (e.g., "Is the watch time >= 90%?", "Generate a JWT token").
*   **Why:** This layer is framework-independent. It focuses purely on the rules of your educational platform.

### Layer 3: Data Access Layer (`Backend/data/repository.py`)
*   **Role:** The "Librarian."
*   **Responsibilities:** The only place where SQL queries (`SELECT`, `INSERT`, etc.) are written.
*   **Why:** Business logic shouldn't be cluttered with SQL strings. By centralizing queries here, we make them easy to audit and optimize.

### Layer 4: Infrastructure Layer (`Backend/data/db.py`)
*   **Role:** The "Plumber."
*   **Responsibilities:** Manages the actual connection to SQLite or PostgreSQL and handles low-level driver details.

---

## 2. Integrated Design Patterns

### A. Singleton Pattern (`Backend/data/db.py`)
*   **Applied to:** `DatabaseManager` class.
*   **How:** Uses `__new__` to ensure only **one instance** of the manager exists in the entire app.
*   **Why:** Creating database connection pools is expensive. Singleton ensures we reuse one manager and one configuration centrally.

### B. Factory & Adapter Patterns (`Backend/data/db.py`)
*   **Applied to:** `DatabaseAdapter` and its children (`SQLiteAdapter`, `PostgresAdapter`).
*   **How:** The `DatabaseManager` acts as a **Factory** that creates the correct adapter based on the environment (Local vs. Production).
*   **Why:** SQLite and Postgres use different syntax (e.g., `?` vs `%s`). The **Adapter Pattern** "translates" these differences so the rest of your code can use a single, unified method: `execute_query`.

### C. Repository Pattern (`Backend/data/repository.py`)
*   **Applied to:** `UserRepository`, `CourseRepository`.
*   **How:** Instead of services calling the database directly, they call methods like `user_repo.get_by_id()`.
*   **Why:** It creates a "buffer" between your data source and your logic. This makes it possible to mock the data during unit testing.

### D. Dependency Injection (`Backend/app.py` & `services/`)
*   **Applied to:** Service constructors.
*   **How:** In `app.py`, we instantiate the `user_repo` and "inject" it into the `AuthService` constructor.
*   **Why:** It prevents tight coupling. The `AuthService` doesn't *create* its own repository; it is *given* one. This is the gold standard for testability.

### E. Observer Pattern (`Backend/services/course_service.py`)
*   **Applied to:** Progress tracking.
*   **How:** `CourseService` maintains a list of "Observers." When progress is saved, it "notifies" them.
*   **Why:** Decoupling side-effects. For example, the `CompletionLogger` is an observer. If you later want to add an "Email Notification" feature, you just create a new Observer class and add it in `app.py`. You don't have to change the `save_progress` function itself!

---

## Summary Table

| File | Pattern/Layer | Why? |
| :--- | :--- | :--- |
| `app.py` | **Composition Root** | Where all objects are created and wired together (Dependency Injection). |
| `api/routes.py` | **API Layer** | Keeps the HTTP logic separate from the "Brain." |
| `services/auth_service.py` | **Service Layer** | Pure business logic; doesn't know about databases or HTTP. |
| `data/db.py` | **Adapter + Singleton** | Unifies different database drivers into one simple interface. |
| `data/repository.py` | **Repository Layer** | Centralizes SQL so queries aren't scattered everywhere. |

---

### Study Tip:
Look at `Backend/services/course_service.py`. Notice how it defines a `ProgressObserver` class? This is an **Interface**. Any class that follows this "contract" can be plugged into the system. This is the **Open/Closed Principle**: The system is *open* for extension (new observers) but *closed* for modification (you don't change the service logic).
