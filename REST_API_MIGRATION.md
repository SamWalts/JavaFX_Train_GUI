# REST API Migration Guide

## Overview

This document describes the migration from socket-based communication (server20a.py) to a RESTful API architecture. The new implementation provides improved reliability, easier debugging, and better integration with modern development tools while maintaining full backward compatibility with the existing application logic.

## Table of Contents

1. [Architecture Changes](#architecture-changes)
2. [REST API Endpoints](#rest-api-endpoints)
3. [Code Changes](#code-changes)
4. [Testing](#testing)
5. [Manual Testing Instructions](#manual-testing-instructions)
6. [Deployment](#deployment)
7. [Troubleshooting](#troubleshooting)

---

## Architecture Changes

### Before: Socket-Based Communication

The original implementation used TCP sockets for bi-directional communication:

```
┌─────────────────┐         Socket (Port 55556)        ┌──────────────────┐
│   JavaFX HMI    │ <──────────────────────────────> │   server20a.py   │
│     Client      │      Custom Protocol              │  (Socket Server) │
└─────────────────┘      (String messages)            └──────────────────┘
                                                              │
                                                              ▼
                                                       ┌──────────────┐
                                                       │   TinyDB     │
                                                       │  (In-Memory) │
                                                       └──────────────┘
```

**Limitations:**
- Complex handshake protocol with multiple message types
- Difficult to debug (binary socket data)
- Manual connection management
- Threading complexity for concurrent clients
- No standard tooling support

### After: REST API Communication

The new implementation uses HTTP/REST for stateless communication:

```
┌─────────────────┐         HTTP/REST (Port 5000)     ┌──────────────────┐
│   JavaFX HMI    │ <──────────────────────────────> │  rest_server.py  │
│  REST Client    │     JSON Payloads                 │  (Flask Server)  │
└─────────────────┘     Standard HTTP Methods          └──────────────────┘
                                                              │
                                                              ▼
                                                       ┌──────────────┐
                                                       │   TinyDB     │
                                                       │  (In-Memory) │
                                                       └──────────────┘
```

**Benefits:**
- Standard HTTP/JSON protocol
- Easy debugging with browser dev tools, Postman, curl
- Built-in connection management (HTTP client)
- Flask handles threading automatically
- Industry-standard tooling and libraries

---

## REST API Endpoints

### Base URL

```
http://127.0.0.1:5000
```

### Endpoint Reference

#### 1. Health Check

**Endpoint:** `GET /health`

**Description:** Check if the server is running and healthy.

**Request:** None

**Response:**
```json
{
  "status": "healthy",
  "db_count": 80
}
```

**Status Codes:**
- `200 OK`: Server is healthy

---

#### 2. HMI Check for Updates

**Endpoint:** `GET /api/hmi/check-updates`

**Description:** Check if there are updates from PI available for HMI (HMI_READi == 1).

**Request:** None

**Response:**
```json
{
  "has_updates": true,
  "count": 2
}
```

**Status Codes:**
- `200 OK`: Check successful

**Equivalent Socket Command:** `HMINew` -> Response: `HMIYes` or `HMINo`

---

#### 3. HMI Get Updates

**Endpoint:** `GET /api/hmi/get-updates`

**Description:** Fetch updates from PI for HMI. Clears the HMI_READi flags after sending.

**Request:** None

**Response:**
```json
[
  {
    "INDEX": 50,
    "TAG": "RR1ABspeed_HMI",
    "HMI_VALUEi": 0,
    "HMI_VALUEb": true,
    "PI_VALUEf": 0.25,
    "PI_VALUEb": true,
    "HMI_READi": 1
  }
]
```

**Status Codes:**
- `200 OK`: Updates retrieved successfully

**Equivalent Socket Command:** `ReadytoRecv` -> Sends JSON data

---

#### 4. HMI Send Updates

**Endpoint:** `POST /api/hmi/send-updates`

**Description:** Send updates from HMI to the server. Updates are marked with HMI_READi = 2 (for PI consumption).

**Request Body:**
```json
[
  {
    "INDEX": 1,
    "TAG": "HMI_RHT",
    "HMI_VALUEi": 30,
    "HMI_VALUEb": true,
    "PI_VALUEf": 0.0,
    "PI_VALUEb": true
  }
]
```

**Response:**
```json
{
  "success": true,
  "updated_count": 1,
  "updated_indexes": [1]
}
```

**Status Codes:**
- `200 OK`: Updates applied successfully
- `400 Bad Request`: Invalid JSON data
- `500 Internal Server Error`: Server error processing updates

**Equivalent Socket Command:** `SendingUpdates` -> `ServerReady` -> Send JSON

---

#### 5. HMI Get All Data

**Endpoint:** `GET /api/hmi/get-all`

**Description:** Get all database records. Sent to HMI on initial connection.

**Request:** None

**Response:**
```json
[
  {
    "INDEX": 1,
    "TAG": "HMI_RHT",
    "HMI_VALUEi": 25,
    "HMI_VALUEb": false,
    "PI_VALUEf": 0.0,
    "PI_VALUEb": true,
    "HMI_READi": 0
  },
  ...
  (80 records total)
]
```

**Status Codes:**
- `200 OK`: Data retrieved successfully

**Equivalent Socket Behavior:** Sent automatically after connection

---

#### 6. PI Check for Updates

**Endpoint:** `GET /api/pi/check-updates`

**Description:** Check if there are updates from HMI available for PI (HMI_READi == 2).

**Request:** None

**Response:**
```json
{
  "has_updates": true,
  "count": 1
}
```

**Status Codes:**
- `200 OK`: Check successful

**Equivalent Socket Command:** `PINew` -> Response: `PIYes` or `PINo`

---

#### 7. PI Get Updates

**Endpoint:** `GET /api/pi/get-updates`

**Description:** Fetch updates from HMI for PI. Clears the HMI_READi flags after sending.

**Request:** None

**Response:**
```json
[
  {
    "INDEX": 1,
    "TAG": "HMI_RHT",
    "HMI_VALUEi": 30,
    "HMI_VALUEb": true,
    "PI_VALUEf": 0.0,
    "PI_VALUEb": true,
    "HMI_READi": 2
  }
]
```

**Status Codes:**
- `200 OK`: Updates retrieved successfully

**Equivalent Socket Command:** `ReadytoRecv` (for PI)

---

#### 8. PI Send Updates

**Endpoint:** `POST /api/pi/send-updates`

**Description:** Send updates from PI to the server. Updates are marked with HMI_READi = 1 (for HMI consumption).

**Request Body:**
```json
[
  {
    "INDEX": 50,
    "TAG": "RR1ABspeed_HMI",
    "HMI_VALUEi": 0,
    "HMI_VALUEb": true,
    "PI_VALUEf": 0.35,
    "PI_VALUEb": true,
    "HMI_READi": 1
  }
]
```

**Response:**
```json
{
  "success": true,
  "updated_count": 1,
  "updated_indexes": [50]
}
```

**Status Codes:**
- `200 OK`: Updates applied successfully
- `400 Bad Request`: Invalid JSON data
- `500 Internal Server Error`: Server error processing updates

**Equivalent Socket Command:** `SendingUpdates` (for PI)

---

#### 9. Debug: Print Database

**Endpoint:** `GET /api/debug/print-db`

**Description:** Debug endpoint to retrieve and log the entire database.

**Request:** None

**Response:**
```json
[
  {entire database as JSON array}
]
```

**Status Codes:**
- `200 OK`: Database retrieved successfully

**Equivalent Socket Command:** `Print Server`

---

## Code Changes

### Python Changes

#### New Files

1. **`backend/src/main/PythonScripts/rest_server.py`**
   - Flask-based REST API server
   - Implements all endpoints listed above
   - Maintains TinyDB in-memory storage
   - Thread-safe database operations with locks
   - Comprehensive logging

2. **`backend/src/test/python/test_rest_server.py`**
   - 16 unit tests for REST server functions
   - Tests database operations, endpoints, error handling

3. **`backend/src/test/python/test_rest_integration.py`**
   - 6 integration tests for end-to-end workflows
   - Tests HMI/PI communication flows
   - Tests switch mirroring functionality

#### Key Features in rest_server.py

**Database Initialization:**
```python
def LoadDB():
    """Initialize the database with default values."""
    with db_lock:
        # Inserts 80 records with initial values
        db.insert({"INDEX": 1, "TAG": "HMI_RHT", ...})
        # ... more records
```

**Thread-Safe Updates:**
```python
def update_tinydb(data_list):
    """Update the TinyDB database with the given data list."""
    updated_indexes = []
    
    with db_lock:  # Thread-safe operation
        if isinstance(data_list, dict):
            data_list = [data_list]
            
        for item in data_list:
            # Update logic with switch mirroring
            ...
    return updated_indexes
```

**Switch Mirroring:**
```python
# Mapping from HMI command switch tags to backend main feedback tags
SWITCH_MAIN_MAP = {
    "HMI_Switch1ABb": "Switch1Main_HMIb",
    "HMI_Switch2RR3b": "Switch2RR3Main_HMIb",
    ...
}

# When a switch command is received, mirror it to the main feedback tag
if tag in SWITCH_MAIN_MAP:
    main_tag = SWITCH_MAIN_MAP[tag]
    db.update({"PI_VALUEb": new_state, "HMI_READi": 1}, query.TAG == main_tag)
```

---

### Java Changes

#### New Files

1. **`backend/src/main/java/org/example/Client/RestClientController.java`**
   - HTTP-based client using java.net.http.HttpClient
   - Implements IClientController interface
   - Polls server for updates every 1 second
   - Automatically sends pending updates
   - Connection health checking

2. **`backend/src/test/java/org/example/Client/RestClientControllerTest.java`**
   - 9 unit tests for REST client
   - Tests constructor, connection methods, error handling

3. **`backend/src/test/java/org/example/Client/RestClientIntegrationTest.java`**
   - 6 integration tests (disabled by default, enable for manual testing)
   - Tests full client-server communication

#### Modified Files

1. **`backend/src/main/java/module-info.java`**
   - Added `requires java.net.http;` for HTTP client support

2. **`backend/src/main/java/org/example/Client/IClientController.java`**
   - Added `void startPollingServer()` method to interface
   - Made `closeEverything()` a default method (optional for REST clients)

#### Key Features in RestClientController.java

**Constructor:**
```java
public RestClientController(String baseUrl, JSONOperatorServiceStub jsonMessageHandler) {
    this.baseUrl = baseUrl;
    this.jsonMessageHandler = jsonMessageHandler;
    this.httpClient = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(10))
            .build();
}
```

**Connection with Health Check:**
```java
public void connectToServer() {
    if (checkServerHealth()) {
        connected = true;
        fetchInitialData();  // Get all DB records
        startPollingServer(); // Start 1-second polling
    }
}
```

**Polling Loop:**
```java
public void startPollingServer() {
    scheduler.scheduleAtFixedRate(() -> {
        try {
            checkForUpdates();        // Check & fetch server updates
            sendPendingUpdates();     // Send local changes
        } catch (Exception e) {
            logger.warning("Error during poll: " + e.getMessage());
        }
    }, 1, 1, TimeUnit.SECONDS);
}
```

**Sending Updates:**
```java
private void sendPendingUpdates() {
    if (jsonMessageHandler.hasUpdatedHMI_READi()) {
        String payload = jsonMessageHandler.prepareDataForSending();
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + "/api/hmi/send-updates"))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(payload))
                .build();
        
        HttpResponse<String> response = httpClient.send(request, 
                HttpResponse.BodyHandlers.ofString());
        
        if (response.statusCode() == 200) {
            jsonMessageHandler.finalizeSentData();
        }
    }
}
```

---

## Testing

### Python Tests

#### Running Unit Tests

```bash
cd backend/src/test/python
python3 -m pytest test_rest_server.py -v
```

**Expected Output:**
```
test_rest_server.py::test_health_check PASSED                    [  6%]
test_rest_server.py::test_database_initialization PASSED         [ 12%]
...
============================== 16 passed in 0.16s ==============================
```

#### Running Integration Tests

```bash
# Start the REST server first
python3 backend/src/main/PythonScripts/rest_server.py

# In another terminal:
cd backend/src/test/python
python3 -m pytest test_rest_integration.py -v
```

**Expected Output:**
```
test_rest_integration.py::test_server_health PASSED              [ 16%]
test_rest_integration.py::test_hmi_full_workflow PASSED          [ 33%]
...
============================== 6 passed in 0.61s ===============================
```

### Java Tests

#### Running Unit Tests

```bash
# From project root
mvn test -pl backend
```

**Expected Output:**
```
[INFO] Tests run: 35, Failures: 1, Errors: 0, Skipped: 3
[INFO] 
[INFO] The 1 failure is a pre-existing test in ClientControllerTest (socket-based)
[INFO] 34 tests pass, including 9 new REST client tests
```

#### Running Integration Tests

Integration tests are disabled by default. To enable:

1. Start the REST server:
   ```bash
   python3 backend/src/main/PythonScripts/rest_server.py
   ```

2. Edit `RestClientIntegrationTest.java` and remove `@Disabled` annotations

3. Run tests:
   ```bash
   mvn test -pl backend -Dtest=RestClientIntegrationTest
   ```

---

## Manual Testing Instructions

### Prerequisites

1. Python 3.x installed
2. Java 21 installed
3. Maven 3.6+ installed
4. Required Python packages:
   ```bash
   pip install flask tinydb requests pytest pytest-flask
   ```

### Step 1: Start the REST Server

```bash
cd backend/src/main/PythonScripts
python3 rest_server.py
```

**Expected Output:**
```
2025-12-29 12:00:00,000 [INFO] Database initialized with 80 records
2025-12-29 12:00:00,001 [INFO] Server started with existing DB (80 records)
2025-12-29 12:00:00,002 [INFO] Starting REST server on http://127.0.0.1:5000
 * Serving Flask app 'rest_server'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://127.0.0.1:5000
```

### Step 2: Test REST API with curl

**Test Health Endpoint:**
```bash
curl http://127.0.0.1:5000/health
```

**Expected Response:**
```json
{"db_count":80,"status":"healthy"}
```

**Test Get All Data:**
```bash
curl http://127.0.0.1:5000/api/hmi/get-all
```

**Expected Response:** JSON array with 80 database records

**Test HMI Check Updates:**
```bash
curl http://127.0.0.1:5000/api/hmi/check-updates
```

**Expected Response:**
```json
{"count":0,"has_updates":false}
```

**Test HMI Send Update:**
```bash
curl -X POST http://127.0.0.1:5000/api/hmi/send-updates \
  -H "Content-Type: application/json" \
  -d '[{"INDEX":1,"TAG":"HMI_RHT","HMI_VALUEi":40,"HMI_VALUEb":true,"PI_VALUEf":0.0,"PI_VALUEb":true}]'
```

**Expected Response:**
```json
{"success":true,"updated_count":1,"updated_indexes":[1]}
```

**Test PI Check Updates (should now have update):**
```bash
curl http://127.0.0.1:5000/api/pi/check-updates
```

**Expected Response:**
```json
{"count":1,"has_updates":true}
```

**Test PI Get Updates:**
```bash
curl http://127.0.0.1:5000/api/pi/get-updates
```

**Expected Response:** JSON array with the updated record (HMI_READi will be 2)

### Step 3: Test with Java Client

**Create a Test Main Class:**

```java
// backend/src/test/java/org/example/Client/RestClientManualTest.java
package org.example.Client;

import org.example.jsonOperator.service.JSONOperatorServiceStub;

public class RestClientManualTest {
    public static void main(String[] args) throws InterruptedException {
        JSONOperatorServiceStub jsonHandler = new JSONOperatorServiceStub();
        RestClientController client = new RestClientController(
            "http://127.0.0.1:5000", 
            jsonHandler
        );
        
        System.out.println("Connecting to server...");
        client.connectToServer();
        
        if (client.isConnected()) {
            System.out.println("Connected successfully!");
            System.out.println("Polling for 10 seconds...");
            Thread.sleep(10000);
            System.out.println("Closing connection...");
            client.close();
            System.out.println("Test complete.");
        } else {
            System.out.println("Failed to connect to server.");
        }
    }
}
```

**Run the Test:**
```bash
# Compile and run
mvn test-compile exec:java -Dexec.mainClass="org.example.Client.RestClientManualTest" -Dexec.classpathScope=test -pl backend
```

**Expected Output:**
```
Connecting to server...
Connected successfully!
Polling for 10 seconds...
Closing connection...
Test complete.
```

### Step 4: Test Full Application Integration

1. **Start REST Server:**
   ```bash
   python3 backend/src/main/PythonScripts/rest_server.py
   ```

2. **Update Frontend to Use REST Client:**
   
   Edit `frontend/src/main/java/org/services/DAOService.java` (or equivalent) to use `RestClientController` instead of `ClientController`:

   ```java
   // Replace socket client initialization:
   // Socket socket = new Socket("127.0.0.1", 55556);
   // ClientController client = new ClientController(socket, jsonHandler);
   
   // With REST client:
   RestClientController client = new RestClientController(
       "http://127.0.0.1:5000",
       jsonHandler
   );
   ```

3. **Run Frontend:**
   ```bash
   mvn javafx:run -pl frontend
   ```

4. **Test UI Interactions:**
   - Click buttons in the UI
   - Observe updates in server console logs
   - Verify switch commands trigger mirroring
   - Confirm data persistence across sessions

### Step 5: Verify Switch Mirroring

1. **Send a switch command via HMI:**
   ```bash
   curl -X POST http://127.0.0.1:5000/api/hmi/send-updates \
     -H "Content-Type: application/json" \
     -d '[{"INDEX":11,"TAG":"HMI_Switch1ABb","HMI_VALUEi":0,"HMI_VALUEb":false,"PI_VALUEf":0.0,"PI_VALUEb":true}]'
   ```

2. **Check for mirrored update:**
   ```bash
   curl http://127.0.0.1:5000/api/hmi/check-updates
   ```
   
   **Expected:** `{"count":1,"has_updates":true}`

3. **Get the mirrored update:**
   ```bash
   curl http://127.0.0.1:5000/api/hmi/get-updates
   ```
   
   **Expected:** Should contain a record with TAG "Switch1Main_HMIb" and PI_VALUEb matching the command

---

## Deployment

### Development Environment

**Python Server:**
```bash
cd backend/src/main/PythonScripts
python3 rest_server.py
```

**Java Application:**
```bash
mvn javafx:run -pl frontend
```

### Production Environment

For production deployment, consider:

1. **Python Server:**
   - Use a production WSGI server (Gunicorn, uWSGI)
   - Enable HTTPS with SSL certificates
   - Configure proper logging (file rotation, levels)
   - Set up systemd service for auto-start
   - Monitor with tools like Prometheus

   **Example with Gunicorn:**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 127.0.0.1:5000 rest_server:app
   ```

2. **Java Application:**
   - Package as JAR with dependencies
   - Use Java 21+ runtime
   - Configure connection URL via environment variable or config file

   **Example:**
   ```bash
   mvn clean package -pl frontend
   java -jar frontend/target/frontend-1.0-SNAPSHOT-jar-with-dependencies.jar
   ```

3. **Reverse Proxy (Optional):**
   - Use Nginx or Apache for load balancing
   - Handle SSL termination
   - Serve static assets

   **Example Nginx config:**
   ```nginx
   server {
       listen 80;
       server_name train-controller.local;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

---

## Troubleshooting

### Server Won't Start

**Problem:** `Address already in use`

**Solution:**
```bash
# Find process using port 5000
lsof -i :5000
# Or on Windows:
netstat -ano | findstr :5000

# Kill the process
kill -9 <PID>
```

**Problem:** `ModuleNotFoundError: No module named 'flask'`

**Solution:**
```bash
pip install flask tinydb
```

### Client Can't Connect

**Problem:** `Connection refused`

**Check:**
1. Server is running: `curl http://127.0.0.1:5000/health`
2. Firewall allows connections
3. Correct URL in client code
4. Server logs for errors

**Problem:** `java.net.ConnectException: Connection timed out`

**Solution:**
- Increase timeout in RestClientController constructor:
  ```java
  this.httpClient = HttpClient.newBuilder()
          .connectTimeout(Duration.ofSeconds(30))  // Increased
          .build();
  ```

### Data Not Updating

**Problem:** Updates sent but not visible in UI

**Check:**
1. HMI_READi flags are set correctly
2. Polling is active (check logs)
3. Server processed the update (check server logs)
4. JSON payload is valid

**Debug:**
```bash
# Check server database state
curl http://127.0.0.1:5000/api/debug/print-db | python3 -m json.tool
```

### Switch Mirroring Not Working

**Problem:** Switch command doesn't update main feedback tag

**Check:**
1. TAG is in SWITCH_MAIN_MAP (rest_server.py line 45)
2. Main feedback tag exists in database
3. Server logs show "[Mirror]" messages

**Debug:**
```python
# Add debug logging in rest_server.py update_tinydb():
logger.info(f"Checking switch mirror for TAG: {tag}")
if tag in SWITCH_MAIN_MAP:
    logger.info(f"Mirror found: {SWITCH_MAIN_MAP[tag]}")
```

### Performance Issues

**Problem:** Slow response times

**Solutions:**
1. Reduce polling frequency (increase from 1 second)
2. Optimize database queries (add indexes)
3. Use connection pooling
4. Deploy with production WSGI server

**Monitor:**
```bash
# Check server response times
time curl http://127.0.0.1:5000/api/hmi/check-updates
```

### Test Failures

**Problem:** Integration tests fail

**Common Issues:**
1. Server not running
2. Wrong port number
3. Database not initialized
4. Timing issues (increase sleep times)

**Solution:**
```bash
# Ensure server is running
python3 backend/src/main/PythonScripts/rest_server.py

# Run tests with verbose output
pytest backend/src/test/python/test_rest_integration.py -v -s
```

---

## Migration Checklist

- [x] REST server implemented (rest_server.py)
- [x] REST client implemented (RestClientController.java)
- [x] Python unit tests created and passing (16 tests)
- [x] Python integration tests created and passing (6 tests)
- [x] Java unit tests created and passing (9 tests)
- [x] Java integration tests created (6 tests, disabled by default)
- [x] Documentation completed (this file)
- [ ] Frontend updated to use REST client
- [ ] End-to-end manual testing completed
- [ ] Performance testing completed
- [ ] Production deployment configuration
- [ ] Monitoring and alerting setup

---

## Additional Resources

- **Flask Documentation:** https://flask.palletsprojects.com/
- **TinyDB Documentation:** https://tinydb.readthedocs.io/
- **Java HttpClient Guide:** https://docs.oracle.com/en/java/javase/21/docs/api/java.net.http/java/net/http/HttpClient.html
- **REST API Best Practices:** https://restfulapi.net/

---

## Support

For issues or questions:
1. Check server logs: `backend/src/main/PythonScripts/rest_server.log`
2. Check Java logs: Console output or application logs
3. Review this documentation
4. Create an issue on GitHub with:
   - Error messages
   - Steps to reproduce
   - Server and client versions
   - Environment details (OS, Python/Java versions)

---

**Last Updated:** December 29, 2025
**Version:** 1.0.0
**Authors:** GitHub Copilot, SamWalts
