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

## Building Native Installers

The project includes a GitHub Actions workflow to build native installers for Windows, macOS, and Linux.

### Manual Trigger

1. Go to the **Actions** tab in GitHub
2. Select **Build Release Installers**
3. Click **Run workflow**
4. Download the installer artifacts when complete

### Tag-based Release

Create and push a version tag to automatically build installers:

```bash
git tag v1.0.0
git push origin v1.0.0
```

The installers will be built and uploaded as artifacts with the version in the filename:
- Windows: `TrainGUI-windows-x64-1.0.0.exe`
- macOS: `TrainGUI-macos-x64-1.0.0.dmg`
- Linux: `TrainGUI-linux-x64-1.0.0.deb`

Each installer includes:
- JavaFX frontend with bundled Java runtime (no Java installation required)
- Python backend as a standalone executable (no Python installation required)
- All necessary dependencies

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
