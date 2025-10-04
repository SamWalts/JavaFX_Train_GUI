# JavaFX Train GUI

A JavaFX-based graphical user interface for controlling a model train system with real-time synchronization to a Python backend.

## Project Structure

- **frontend/** - JavaFX frontend application
- **backend/** - Java backend services and Python control scripts
- **docs/** - Documentation

## Documentation

- **[Adding Buttons Guide](ADDING_BUTTONS.md)** - Comprehensive guide on how to add new buttons to the project with backend acknowledgment

## Building the Project

```bash
mvn clean install
```

## Running the Application

1. Start the backend server:
   ```bash
   python backend/src/main/PythonScripts/server20a.py
   ```

2. Run the frontend:
   ```bash
   mvn -pl frontend javafx:run
   ```

## Requirements

- Java 21+
- Maven 3.6+
- Python 3.x (for backend)

## Architecture

The application uses a multi-layer architecture:
- **View Layer** (FXML) - UI definition
- **Controller Layer** - UI event handling
- **ViewModel Layer** - Business logic and state management
- **Service Layer** - Data access and synchronization
- **Backend Layer** - Python-based hardware control

## Contributing

When adding new features, especially UI buttons, please refer to the [Adding Buttons Guide](ADDING_BUTTONS.md) to ensure proper implementation with backend acknowledgment.
