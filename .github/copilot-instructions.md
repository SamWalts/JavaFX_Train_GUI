# GitHub Copilot Instructions for JavaFX Train GUI

## Project Overview

This is a **JavaFX-based Train Control GUI** application that interfaces with hardware controllers (Raspberry Pi) running Python scripts to control model trains, trams, and track switches. The project uses a client-server architecture with JSON-based communication.

### Architecture

- **Frontend Module**: JavaFX GUI application with FXML-based UI screens
- **Backend Module**: Client connection handling and JSON data operations
- **Python Scripts**: Hardware control scripts that run on Raspberry Pi

### Technology Stack

- **Language**: Java 21 (with preview features enabled)
- **UI Framework**: JavaFX 21
- **Build Tool**: Maven (multi-module project)
- **Testing**: JUnit 5, Mockito
- **Data Format**: JSON (Jackson library)
- **Python**: Version 3.x for Raspberry Pi hardware control scripts

## Project Structure

```
JavaFX_Train_GUI/
├── backend/
│   ├── src/main/java/
│   │   ├── org/example/Client/        # Socket client for server communication
│   │   └── org/example/jsonOperator/  # JSON data handling (DAO, DTO, Service)
│   ├── src/main/PythonScripts/        # Raspberry Pi control scripts
│   └── src/test/java/                 # Backend unit tests
├── frontend/
│   ├── src/main/java/
│   │   ├── org/services/              # Singleton services (DAO, UI state, navigation)
│   │   ├── org/viewModels/            # Screen controllers
│   │   └── org/viewScreens/           # Main application class
│   ├── src/main/resources/            # FXML files and assets
│   └── src/test/java/                 # Frontend unit tests
└── pom.xml                            # Parent POM
```

## Build and Test

### Building the Project

```bash
# Build all modules
mvn clean install

# Build specific module
mvn clean install -pl backend
mvn clean install -pl frontend
```

### Running Tests

```bash
# Run all tests
mvn test

# Run specific test class
mvn test -Dtest=UIStateServiceTest -pl frontend
mvn test -Dtest=JSONServiceTests -pl backend

# Skip tests during build
mvn clean install -DskipTests
```

### Running the Application

```bash
# From the frontend module
cd frontend
mvn javafx:run
```

## Coding Standards and Conventions

### Java Code Style

1. **Java Version**: Use Java 21 features; preview features are enabled
2. **Naming Conventions**:
   - Classes: PascalCase (e.g., `UIStateService`)
   - Methods: camelCase (e.g., `markPending()`)
   - Constants: UPPER_SNAKE_CASE (e.g., `MAX_RETRIES`)
   - Variables: camelCase with meaningful names
   
3. **Design Patterns**:
   - **Singleton Pattern**: Used for service classes (DAOService, UIStateService, NavigationService)
   - **Factory Pattern**: Used for client creation (ClientFactory)
   - **Observer Pattern**: Used for HMI data change notifications

4. **Service Classes**: 
   - Must be thread-safe (services are singletons)
   - Should have private constructors
   - Provide `getInstance()` method
   - Initialize resources in constructor or lazy initialization

### Testing Standards

1. **Test Framework**: Use JUnit 5 (`@Test`, `@BeforeEach`, `@AfterEach`)
2. **Test Naming**: Descriptive names like `testMethodName_condition_expectedBehavior`
3. **Test Organization**:
   - Setup in `@BeforeEach`
   - Cleanup in `@AfterEach`
   - One assertion concept per test
   - Test both happy paths and edge cases (null, empty, invalid inputs)

4. **Mocking**: Use Mockito for external dependencies
5. **Coverage**: Aim for comprehensive coverage of public APIs

### JSON Data Handling

- **HMI Data Structure**: Each entry contains:
  - `INDEX`: Unique identifier
  - `TAG`: Variable name/label
  - `HMI_VALUEi`: Integer value from HMI
  - `HMI_VALUEb`: Boolean value from HMI
  - `PI_VALUEf`: Float value from Raspberry Pi
  - `PI_VALUEb`: Boolean value from Raspberry Pi
  - `HMI_READi`: Acknowledgment flag (0=not sent, 1=sent, 2=acknowledged)

- **Data Flow**: 
  1. User interacts with JavaFX GUI
  2. Frontend updates HMI values and marks as pending
  3. Backend sends data to Python server (Raspberry Pi)
  4. Python acknowledges by setting `HMI_READi` to 2
  5. Frontend clears pending status upon acknowledgment

### Python Scripts

- **Purpose**: Hardware control on Raspberry Pi
- **Libraries**: 
  - `socket`: Network communication
  - `serial`: Arduino/hardware communication  
  - `gpiozero`: GPIO control
  - `pygame`: Sound effects
  - `tinydb`: In-memory database
  - `threading`: Concurrent operations

- **Convention**: Database entries use same structure as Java JSON format
- **Server Communication**: Socket-based with JSON message exchange

## Module-Specific Guidelines

### Backend Module

- **Client Package**: Handles socket connections to Python server
  - Singleton pattern for ClientController
  - Callback interface for message handling
  - Factory for client creation

- **JSON Operator Package**:
  - `dao`: Data access objects for JSON file I/O
  - `dto`: Data transfer objects (HMIData)
  - `service`: Business logic for JSON operations, queue management

- **Testing**: Mock file I/O and socket connections in tests

### Frontend Module

- **Services**:
  - `DAOService`: Manages JSON data access layer
  - `UIStateService`: Tracks pending UI changes and server acknowledgments
  - `NavigationService`: Handles screen navigation with server wait states

- **View Models**: Controllers for FXML screens (trainScreen, tramScreen, utilitiesScreen)

- **FXML Guidelines**:
  - Use `fx:id` for component references
  - Controllers should extend/implement appropriate interfaces
  - Keep business logic in services, not controllers

## Common Tasks

### Adding a New HMI Control

1. Add entry to JSON data structure in both Java and Python
2. Update FXML with new UI component
3. Add controller method to handle user interaction
4. Update UIStateService to track pending state
5. Add corresponding test cases

### Adding a New Service

1. Create service class with private constructor
2. Implement singleton pattern with `getInstance()`
3. Add thread-safety if needed (synchronized methods or concurrent collections)
4. Create comprehensive unit tests
5. Update TEST_COVERAGE.md

### Debugging Connection Issues

1. Check Python server is running on Raspberry Pi
2. Verify socket connection (default: 127.0.0.1:55555)
3. Monitor `HMI_READi` values for acknowledgment
4. Check console output for connection errors
5. Verify JSON message format matches expected structure

## Important Notes

- **Thread Safety**: Services are singletons and may be accessed from JavaFX Application Thread and background threads
- **JavaFX Threading**: UI updates must happen on JavaFX Application Thread (use `Platform.runLater()`)
- **Preview Features**: Compiler and Surefire plugin are configured with `--enable-preview`
- **Module System**: Project uses Java Platform Module System (see `module-info.java`)
- **Test Files**: Ignore pre-existing test failure in `ClientControllerTest.testReceiveHMINoMessage`

## References

- [JavaFX Documentation](https://openjfx.io/)
- [JUnit 5 User Guide](https://junit.org/junit5/docs/current/user-guide/)
- [Mockito Documentation](https://javadoc.io/doc/org.mockito/mockito-core/latest/org/mockito/Mockito.html)
- Project test coverage: See `TEST_COVERAGE.md`

## Questions or Issues?

When working on this codebase:
- Check existing test patterns before writing new tests
- Follow the singleton pattern for new service classes
- Ensure thread safety for concurrent access
- Keep JSON data structure synchronized between Java and Python
- Test both JavaFX UI interactions and backend data operations
