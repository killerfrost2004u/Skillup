# SkillUp Backend: Architectural, Patterns & Testing Guide

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

### A. Singleton Pattern (Creational)
*   **Where:** `DatabaseManager` in `Backend/data/db.py`
*   **How:** Uses `__new__` to ensure only **one instance** of the manager exists in the entire app.
*   **Why:** Creating database connection pools is expensive. Singleton ensures we reuse one manager and one configuration centrally across the application.

### B. Adapter Pattern (Structural)
*   **Where:** `DatabaseAdapter`, `SQLiteAdapter`, `PostgresAdapter` in `Backend/data/db.py`
*   **How:** The `DatabaseManager` acts as a Factory that creates the correct adapter based on the environment.
*   **Why:** SQLite and Postgres use different syntax (e.g., `?` vs `%s`). The Adapter Pattern "translates" these differences so the rest of your code can use a single, unified method: `execute_query`.

### C. Dependency Injection (Structural)
*   **Where:** `UserRepository`, `AuthService`, and `app.py` (The Composition Root).
*   **How:** Instead of classes creating their own dependencies (e.g., a repository importing a global DB instance), dependencies are passed into their `__init__` methods.
*   **Why:** Prevents tight coupling. Because `AuthService` takes a `user_repo` parameter, we can easily pass a *fake* repository during testing.

### D. Observer Pattern (Behavioral)
*   **Where:** `CourseService` and `CompletionLogger` in `Backend/services/course_service.py`.
*   **How:** `CourseService` maintains a list of "Observers." When progress is saved, it "notifies" them.
*   **Why:** Decouples side-effects. The `CompletionLogger` is an observer. If you later want to add an "Email Notification" feature upon course completion, you just create a new Observer class and add it in `app.py`. You don't have to change the `save_progress` function itself!

### E. Strategy Pattern (Behavioral)
*   **Where:** `ChatStrategy`, `OpenAIStrategy`, `OllamaStrategy`, and `AIChatService` in `Backend/services/course_service.py`.
*   **How:** We define a common interface (`ChatStrategy`). The specific AI provider (OpenAI vs. local Ollama) is chosen in `app.py` and passed to `AIChatService`.
*   **Why:** Adheres to the **Open/Closed Principle**. If you want to add Anthropic or Gemini later, you just create a new `GeminiStrategy` class. You do *not* have to modify `AIChatService`.

---

## 3. Unit Testing & Validation Strategy

The project utilizes the `unittest` framework (located in `Backend/tests/`) to ensure reliability. The tests strictly follow three core principles:

### A. Isolation (Mocking)
Tests must isolate the exact unit of work. When testing the `AuthService`, we do not want to connect to a real database, because a database failure would cause the service test to fail, hiding the true source of the bug.
*   **How:** We use `unittest.mock.Mock()`.
```python
# In test_auth_service.py
def setUp(self):
    self.mock_user_repo = Mock() # A fake database
    self.auth_service = AuthService(self.mock_user_repo) # Inject the fake
```

### B. Verification (Happy Paths)
Verification answers the question: *"Does the code run without crashing when given correct input?"*
*   **How:** We assert that methods return the expected success codes and call the underlying functions correctly.
```python
def test_register_user_success(self):
    # Setup the fake DB to return "None" (meaning email is available)
    self.mock_user_repo.get_by_email.return_value = None
    
    result = self.auth_service.register_user("test", "test@test.com", "pass")
    
    # Verify the code succeeded
    self.assertEqual(result["status"], 201)
    # Verify the service actually told the DB to save the user
    self.mock_user_repo.create.assert_called_once()
```

### C. Validation (Business Rules)
Validation answers the question: *"Does the software meet the actual business requirements and stop bad behavior?"*
*   **How:** We deliberately give the system bad data and assert that it correctly blocks the action.
```python
def test_register_user_existing_email(self):
    # Validation: Ensure duplicate emails are blocked.
    # Setup fake DB to pretend the email exists
    self.mock_user_repo.get_by_email.return_value = {"email": "test@test.com"}

    result = self.auth_service.register_user("test", "test@test.com", "pass")
    
    # Assert the system stopped the user
    self.assertEqual(result["status"], 400)
    # CRITICAL: Assert the database create method was NEVER called.
    self.mock_user_repo.create.assert_not_called()
```

---
**To run the test suite:**
```bash
python -m unittest discover Backend/tests
```
