# KEW&J National Railroad — Train Control GUI

A JavaFX desktop app that controls a model train layout via a Python REST server
middlelayer, with a Raspberry Pi backend driving the physical hardware.

```
┌─────────────────────────┐        ┌──────────────────────┐        ┌─────────────────┐
│  JavaFX GUI  (Java 21)  │◄──────►│  REST Server (Python)│◄──────►│  Raspberry Pi   │
│  frontend/              │  HTTP  │  rest_server.py       │  HTTP  │  GPIO / Arduino │
└─────────────────────────┘        └──────────────────────┘        └─────────────────┘
```

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Run in Development (IntelliJ / Maven)](#run-in-development)
3. [Build a Native Installer Locally](#build-a-native-installer-locally)
4. [Build via GitHub Actions (CI/CD)](#build-via-github-actions)
5. [Adding a New Screen](#adding-a-new-screen)
6. [Project Structure](#project-structure)
7. [Further Reading](#further-reading)

---

## Prerequisites

### For development (run in IntelliJ or `mvn javafx:run`)

| Tool | Version | Install |
|---|---|---|
| Java JDK | 21 | [Temurin](https://adoptium.net) |
| Maven | 3.8+ | `brew install maven` |
| Python | 3.11+ | `brew install python@3.13` |

### Additional tools for building native installers

| Tool | Platform | Install |
|---|---|---|
| Xcode Command Line Tools | macOS | `xcode-select --install` |
| WiX Toolset 3.x | Windows | `choco install wixtoolset` |
| fakeroot + dpkg | Linux | `sudo apt-get install fakeroot dpkg` |

---

## Run in Development

This is the fastest way to run the app — no installer needed.

### 1. Set up the Python virtual environment (first time only)

```bash
cd backend/src/main/PythonScripts
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the Java app

```bash
# From the project root
mvn javafx:run -pl frontend
```

The app will automatically:
- Find `rest_server.py` next to the `.venv`
- Launch it using `.venv/bin/python3`
- Wait up to 30 seconds for the server to be healthy
- Open the GUI

> You do **not** need to start the Python server manually. `RestServerLauncher`
> handles it. When you close the GUI, the server process is also shut down.

### 3. Run tests

```bash
mvn test                        # all modules
mvn test -pl backend            # backend only
mvn test -pl frontend           # frontend only
```

---

## Build a Native Installer Locally

This produces a `.dmg` (macOS), `.msi` (Windows), or `.deb` (Linux) that can
be installed on any machine — **no Java or Python required** on the target machine.

### One command

```bash
./build-all.sh
```

The script runs these five steps in order:

| Step | What happens | Output |
|---|---|---|
| 1 | PyInstaller freezes `rest_server.py` | `dist/rest_server` single binary |
| 2 | Binary is copied to `packaging/` staging dir | `packaging/rest_server` |
| 3 | Maven builds fat JAR + copies deps | `frontend/target/libs/` |
| 4 | `jlink` carves a trimmed JRE (~80 MB) | `frontend/target/runtime/` |
| 5 | `jpackage` bundles everything into an installer | `frontend/target/installer/` |

### If you want to run steps individually

```bash
# Step 1+2 — freeze Python server and stage it
cd backend/src/main/PythonScripts
source .venv/bin/activate
pyinstaller rest_server.spec --noconfirm
cd ../../../../
cp backend/src/main/PythonScripts/dist/rest_server packaging/rest_server
chmod +x packaging/rest_server

# Step 3 — Maven build
mvn clean package -DskipTests -pl backend,frontend

# Step 4 — jlink (delete old runtime first if re-running)
rm -rf frontend/target/runtime
mvn exec:exec@jlink -pl frontend

# Step 5 — jpackage
mvn exec:exec@jpackage -pl frontend

# Open the installer
open frontend/target/installer/TrainControl-1.0.0.dmg   # macOS
```

### What gets bundled inside the installer

```
TrainControl.app/
└── Contents/
    ├── MacOS/TrainControl          ← Java launcher
    ├── runtime/                    ← Trimmed JRE (no Java needed on target machine)
    ├── app/
    │   ├── TrainControl-1.0.0.jar  ← Fat JAR (app + all deps)
    │   └── *.jar                   ← JavaFX native JARs
    └── rest_server                 ← Frozen Python server (no Python needed)
```

---

## Build via GitHub Actions (CI/CD)

### How it works

Every push to `main` (or any pull request targeting `main`) automatically
triggers `.github/workflows/build.yml`. It runs **three jobs in parallel**:

```
push to main
     │
     ├── macos-latest  → TrainControl-1.0.0.dmg
     ├── windows-latest → TrainControl-1.0.0.msi
     └── ubuntu-latest  → traincontrol_1.0.0-1_amd64.deb
```

Each job:
1. Checks out your code
2. Freezes `rest_server.py` with PyInstaller
3. Builds the Java fat JAR with Maven
4. Runs `jlink` to create a trimmed JRE
5. Runs `jpackage` to produce the native installer
6. Uploads the installer as a downloadable artifact (kept for 30 days)

### Download an installer from GitHub

1. Go to your repo → **Actions** tab
2. Click the latest **"Build Native Installers"** workflow run
3. Scroll to **Artifacts** at the bottom
4. Download `installer-macos-latest`, `installer-windows-latest`, or
   `installer-ubuntu-latest`

### Do I need to do anything after adding a new screen?

**No.** Just push to `main`:

```bash
git add .
git commit -m "feat: add new YardScreen"
git push origin main
```

GitHub Actions handles everything else. The next workflow run will produce
fresh installers with your new screen included. You never need to touch
`build-all.sh`, `rest_server.spec`, `pom.xml`, or `build.yml` just to add
UI screens — those only change if you add new Python dependencies or
change the packaging configuration.

---

## Adding a New Screen

Adding a screen is a four-file change. It does **not** require any changes to
the build pipeline.

### 1. Create the FXML layout

```
frontend/src/main/resources/org/viewScreens/YardScreen.fxml
```

Use an existing screen like `trainScreen.fxml` as a template. Make sure the
`fx:controller` attribute points to your new controller class:

```xml
<BorderPane fx:controller="org.viewScreens.YardController" ...>
```

### 2. Create the controller

```
frontend/src/main/java/org/viewScreens/YardController.java
```

```java
public class YardController implements Cleanable {

    @Override
    public void cleanup() {
        // stop any background threads or timers here
    }
}
```

### 3. Navigate to the new screen

From any existing controller, call:

```java
App.setRoot("YardScreen");
```

Or use `NavigationService` if you need to wait for server acknowledgment first.

### 4. Add HMI data entries (if the screen has controls)

Add new entries to `PiHmiDict.json` in both:
- `backend/src/main/resources/PiHmiDict.json`
- `backend/src/main/PythonScripts/rest_server.db.json`

Each entry follows this shape:

```json
{
  "INDEX": 42,
  "TAG": "YARD_SWITCH_1",
  "HMI_VALUEi": 0,
  "HMI_VALUEb": false,
  "PI_VALUEf": 0.0,
  "PI_VALUEb": false,
  "HMI_READi": 0
}
```

Then push — GitHub Actions will build the updated installers automatically.

---

## Project Structure

```
JavaFX_Train_GUI/
├── build-all.sh                  ← One-command local build
├── packaging/
│   └── rest_server               ← Staged frozen Python binary (git-ignored)
├── .github/workflows/
│   └── build.yml                 ← CI/CD: builds .dmg/.msi/.deb on every push
│
├── backend/
│   └── src/main/
│       ├── java/org/example/
│       │   ├── Client/           ← REST client (talks to Python server)
│       │   └── jsonOperator/     ← DAO / DTO / Service for JSON data
│       └── PythonScripts/
│           ├── rest_server.py    ← Python REST server (Flask + TinyDB)
│           ├── rest_server.spec  ← PyInstaller build recipe
│           ├── requirements.txt  ← Desktop Python deps (Flask, TinyDB)
│           └── requirements-pi.txt ← Pi-only deps (GPIO, pygame, serial)
│
├── frontend/
│   ├── pom.xml                   ← Maven: shade + jlink + jpackage config
│   └── src/main/
│       ├── java/org/
│       │   ├── services/
│       │   │   ├── RestServerLauncher.java  ← Auto-starts Python server
│       │   │   ├── DAOService.java
│       │   │   ├── UIStateService.java
│       │   │   └── NavigationService.java
│       │   ├── viewModels/       ← Screen view-models
│       │   └── viewScreens/
│       │       ├── App.java      ← JavaFX entry point
│       │       └── *Controller.java
│       └── resources/org/viewScreens/
│           └── *.fxml            ← Screen layouts
│
└── PI_SETUP.md                   ← Raspberry Pi hardware setup guide
```

---

## Further Reading

| Document | Contents |
|---|---|
| [ADDING_BUTTONS.md](ADDING_BUTTONS.md) | Detailed guide: adding buttons with backend acknowledgment |
| [REST_API_MIGRATION.md](REST_API_MIGRATION.md) | REST API architecture, endpoints, troubleshooting |
| [PI_SETUP.md](PI_SETUP.md) | Raspberry Pi hardware wiring, venv setup, systemd auto-start |
| [TEST_COVERAGE.md](TEST_COVERAGE.md) | Unit test coverage by module |
