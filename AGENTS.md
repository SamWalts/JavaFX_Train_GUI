# JavaFX Train GUI - AI Agent Guide

## System Architecture
This project controls model trains via a JavaFX GUI communicating with a local Python REST server.
- **Frontend**: JavaFX 21 with FXML views and Singleton services.
- **Backend (Java)**: REST client handling JSON synchronization.
- **Backend (Python)**: Flask server (`rest_server.py`) managing hardware state in `TinyDB`.
- **Launch**: Java app automatically spawns the Python server via `RestServerLauncher`.

## Critical Workflows
- **Build**: `mvn clean install` handles both modules.
- **Run App**: `mvn javafx:run -pl frontend` (Requires Python venv setup).
- **Test**: `mvn test`. **Note**: Tests use `--enable-preview`.
- **Python Setup**:
  ```bash
  cd backend/src/main/PythonScripts && python3 -m venv .venv
  source .venv/bin/activate && pip install -r requirements.txt
  ```

## Key Patterns & Conventions
- **HMI Data Structure**: The source of truth is a JSON object shared across languages.
  - Example: `{"INDEX": 1, "TAG": "Speed", "HMI_VALUEi": 50, "HMI_READi": 0}`
  - **Change Protocol**: UI updates `HMI_VALUE*` and sets `HMI_READi = 0` (pending). Python server processes and sets `HMI_READi = 2` (acknowledged).
- **Service Access**: All services are Singletons.
  - Usage: `UIStateService.getInstance().addHMIChangeListener(...)`
- **Threading**:
  - UI mutations: Always wrap in `Platform.runLater(() -> ...)`
  - Network I/O: Handled asynchronously by `RestClientController`.
- **Dependency Injection**: None used; rely on `Factory` and `Singleton` patterns manually.

## Important Files
- **State Logic**: `frontend/src/main/java/org/services/UIStateService.java`
- **Comms**: `backend/src/main/java/org/example/Client/RestClientController.java`
- **Server**: `backend/src/main/PythonScripts/rest_server.py`
- **Data Def**: `rest_server.db.json` (defines all HMI tags/indices).
- **Rules**: `.github/copilot-instructions.md` (detailed coding standards).

