# token-insights-server

## Project Structure

token-insights-server/
├── app/
│ ├── **init**.py # App package initialization
│ ├── main.py # Entry point for FastAPI server
│ ├── api/ # API-specific logic
│ │ ├── **init**.py
│ │ ├── routes.py # Define your API routes here
│ ├── core/ # Core logic, utilities, configurations
│ │ ├── **init**.py
│ │ ├── config.py # Configuration management
│ │ ├── dependencies.py # Shared dependencies (e.g., database sessions)
│ ├── models/ # Database models
│ │ ├── **init**.py
│ │ ├── token.py # Example model
│ ├── services/ # Business logic
│ │ ├── **init**.py
│ │ ├── token_service.py # Example service
│ ├── db/ # Database connection and ORM setup
│ │ ├── **init**.py
│ │ ├── base.py # Database base class and session creation
├── tests/ # Unit and integration tests
│ ├── **init**.py
│ ├── test_main.py # Example test
├── pyproject.toml # Poetry project configuration
├── poetry.lock # Poetry lockfile

v0.2.0

    - Session Management

v 0.3.0

    - Context Awareness

v0.4.0

    - Multiprocessing
    ```bash
    gunicorn app.main:app --config process_manager.py
    ```

poetry run uvicorn app.main:app --reload

source $(poetry env info --path)/bin/activate

Sign this message to authenticate with Dexx: f1e0c2a07d719ac9b1f853098fa236a3a0a60db7063a7f3a92b03d42397c9aa7


~~1. Perform smart blockchain lookup from the return~~
~~2. Clean up process tools~~
2.1 Check for multiple tookens and att the token in priority as the token's metadata in the response
3. Complete discovery function tools
4. Release API


Always keep the main token in question upto date and first in the asset list


https://finrl.readthedocs.io/en/latest/start/three_layer/agents.html