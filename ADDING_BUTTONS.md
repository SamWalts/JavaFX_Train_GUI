# Adding New Buttons to the JavaFX Train GUI

This document provides a comprehensive guide on how to add new buttons to the JavaFX Train GUI project. New buttons must wait for backend acknowledgment before allowing further interactions.

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Step-by-Step Guide](#step-by-step-guide)
3. [Complete Example](#complete-example)
4. [Backend Acknowledgment Flow](#backend-acknowledgment-flow)
5. [Testing](#testing)

## Architecture Overview

The button implementation follows this flow:

```
FXML (UI Definition)
    ↓
Controller (TrainController.java)
    ↓
ViewModel (TrainViewModel.java)
    ↓
DAOService (Data Access)
    ↓
UIStateService (Acknowledgment Tracking)
    ↓
Backend (Python/Server)
```

### Key Components

1. **FXML File** - Defines the UI layout and button appearance
2. **Controller** - Binds UI elements to ViewModel actions
3. **ViewModel** - Contains business logic and state management
4. **DAOService** - Manages data synchronization with backend
5. **UIStateService** - Tracks pending operations and backend acknowledgments
6. **HmiData** - Data transfer object containing button state and metadata

## Step-by-Step Guide

### Step 1: Define the Button in FXML

Add your button to the appropriate FXML file (e.g., `trainScreen.fxml`):

```xml
<Button fx:id="MyNewButton" 
        layoutX="100.0" 
        layoutY="100.0" 
        mnemonicParsing="false" 
        text="My New Button">
    <font>
        <Font size="24.0" />
    </font>
</Button>
```

**Key attributes:**
- `fx:id` - Unique identifier used to reference the button in the controller
- `layoutX`, `layoutY` - Position on the screen
- `text` - Button label

### Step 2: Add Button Reference in Controller

In your controller class (e.g., `TrainController.java`), add:

```java
@FXML private Button MyNewButton;
```

### Step 3: Create Action Method in ViewModel

In your ViewModel class (e.g., `TrainViewModel.java`), add an action method:

```java
/**
 * Action for MyNewButton. Toggles the button state and waits for backend ACK.
 * @param tag The HMI data tag associated with this button
 */
public void handleMyNewButton(String tag) {
    findDataByTag(tag).ifPresent(data -> {
        boolean currentState = data.getHmiValueb() != null && data.getHmiValueb();
        
        // Mark this operation as pending - this prevents UI changes until ACK
        UIStateService.getInstance().markPending(Set.of(String.valueOf(data.getIndex())));
        
        // Update the data
        data.setHmiValueb(!currentState);
        data.setHmiReadi(1);  // Signal to backend that HMI has updated this value (pending ACK)
        
        // Putting the data back triggers the listener and notifies the backend
        daoService.getHmiDataMap().put(String.valueOf(data.getIndex()), data);
    });
}
```

### Step 4: Bind Button Action in Controller

In the controller's `initialize()` method, bind the button to the ViewModel action:

```java
@FXML
private void initialize() {
    this.viewModel = new TrainViewModel();
    
    // Bind button action to ViewModel
    MyNewButton.setOnAction(event -> viewModel.handleMyNewButton("HMI_MyNewButtonb"));
    
    // ... rest of initialization
}
```

### Step 5: Register Button with Backend

Ensure the backend database has an entry for your button. The Python backend uses TinyDB with entries like:

```python
{
    "INDEX": 20,
    "TAG": "HMI_MyNewButtonb",
    "HMI_VALUEb": False,
    "HMI_VALUEi": 1,
    "PI_VALUEb": False,
    "PI_VALUEf": 0.0,
    "HMI_READi": 1
}
```

## Complete Example

Here's a complete example of adding a "Train Light" button:

### 1. FXML (trainScreen.fxml)

```xml
<Button fx:id="TrainLight" 
        layoutX="1078.0" 
        layoutY="500.0" 
        mnemonicParsing="false" 
        text="Train Light">
    <font>
        <Font size="24.0" />
    </font>
</Button>
```

### 2. Controller (TrainController.java)

```java
public class TrainController {
    private TrainViewModel viewModel;
    
    @FXML private Button TrainLight;
    
    @FXML
    private void initialize() {
        this.viewModel = new TrainViewModel();
        
        // Bind the train light button
        TrainLight.setOnAction(event -> viewModel.toggleTrainLight("HMI_TrainLightb"));
        
        System.out.println("TrainController initialized and bound to TrainViewModel.");
    }
}
```

### 3. ViewModel (TrainViewModel.java)

```java
public class TrainViewModel implements HMIControllerInterface {
    private final DAOService daoService;
    
    public TrainViewModel() {
        this.daoService = DAOService.getInstance();
        new HMIChangeListener(daoService.getHmiJsonDao(), this);
    }
    
    /**
     * Toggle the train light on/off and wait for backend acknowledgment.
     */
    public void toggleTrainLight(String tag) {
        findDataByTag(tag).ifPresent(data -> {
            boolean currentState = data.getHmiValueb() != null && data.getHmiValueb();
            
            // Mark as pending - blocks further UI interactions
            UIStateService.getInstance().markPending(Set.of(String.valueOf(data.getIndex())));
            
            // Toggle the state
            data.setHmiValueb(!currentState);
            
            // Set HMI_READi to 2 to signal HMI update to backend
            data.setHmiReadi(1);
            
            // Trigger backend update
            daoService.getHmiDataMap().put(String.valueOf(data.getIndex()), data);
            
            System.out.println("[TrainViewModel] Train light toggled to: " + !currentState);
        });
    }
    
    private Optional<HmiData> findDataByTag(String tag) {
        return daoService.getHmiDataMap().values().stream()
                .filter(d -> tag.equals(d.getTag()))
                .findFirst();
    }
    
    @Override
    public void onMapUpdate(String key, Object oldValue, Object newValue) {
        if (!(newValue instanceof HmiData)) return;
        HmiData data = (HmiData) newValue;
        
        // Check for backend acknowledgment
        UIStateService.getInstance().checkAck(key, data);
        
        // Handle other updates...
    }
}
```

### 4. Backend Database Entry

Add to the Python backend's database initialization:

```python
PIdb.insert({
    "INDEX": 20,
    "TAG": "HMI_TrainLightb",
    "HMI_VALUEb": False,
    "HMI_VALUEi": 1,
    "PI_VALUEb": False,
    "PI_VALUEf": 0.0,
    "HMI_READi": 1
})
```

## Backend Acknowledgment Flow

The backend acknowledgment system ensures data synchronization between the frontend and backend:

### How It Works

1. **User Clicks Button** → Controller calls ViewModel action
2. **ViewModel Marks Pending** → `UIStateService.markPending()` is called with the data key(s)
3. **Data Updated** → HMI_READi is set to 2, signaling frontend initiated the change
4. **Backend Receives Update** → Python server processes the change
5. **Backend Acknowledges** → Backend sets HMI_READi to 1 (or 0/null) after processing
6. **Frontend Detects ACK** → `UIStateService.checkAck()` removes the key from pending set
7. **UI Unblocked** → When all pending keys are acknowledged, `waitingForServer` becomes false

### UIStateService Methods

```java
// Mark operations as pending (call before updating data)
UIStateService.getInstance().markPending(Set.of(dataKey));

// Check for acknowledgment (called automatically in onMapUpdate)
UIStateService.getInstance().checkAck(key, updatedHmiData);

// Check if waiting for server
boolean isWaiting = UIStateService.getInstance().isWaitingForServer();
```

### HMI_READi Values

- `0` - Not sent
- `1` - Sent (frontend updated/pending)
- `2` - Acknowledged by backend

**Important:** The backend sets HMI_READi to 2 to acknowledge.

## Testing

### Manual Testing

1. **Build the project:**
   ```bash
   mvn clean install
   ```

2. **Start the backend server:**
   ```bash
   python backend/src/main/PythonScripts/server20a.py
   ```

3. **Run the frontend:**
   ```bash
   mvn -pl frontend javafx:run
   ```

4. **Test the button:**
   - Click the button
   - Observe console output for "[UIState] Pending started for keys=..."
   - Wait for "[UIState] ACK received for key=..."
   - Verify "[UIState] All ACKed. Waiting cleared."

### Unit Testing

Create a test in `frontend/src/test/java/org/viewModels/`:

```java
@Test
void testButtonToggleAndAck() {
    // Setup
    TrainViewModel viewModel = new TrainViewModel();
    UIStateService uiStateService = UIStateService.getInstance();
    
    // Action - Toggle button
    viewModel.toggleTrainLight("HMI_TrainLightb");
    
    // Verify - Should be waiting for server
    assertTrue(uiStateService.isWaitingForServer());
    
    // Simulate backend acknowledgment
    HmiData ackData = new HmiData();
    ackData.setHmiReadi(1);
    uiStateService.checkAck("20", ackData);
    
    // Verify - Should no longer be waiting
    assertFalse(uiStateService.isWaitingForServer());
}
```

## Common Pitfalls

1. **Forgetting to mark pending** → UI won't block and may allow duplicate actions
2. **Wrong TAG name** → Button won't find its data in the map
3. **Missing backend entry** → Button will have no data to update
4. **Backend not clearing HMI_READi** → UI will remain blocked indefinitely
5. **Not calling checkAck in onMapUpdate** → Acknowledgments won't be detected

## Best Practices

1. **Always use `markPending()`** before updating data
2. **Use descriptive TAG names** following the pattern: `HMI_<Feature><Type>b` (e.g., `HMI_TrainLightb`)
3. **Set HMI_READi to 2** when frontend initiates a change
4. **Implement proper error handling** in case backend doesn't respond
5. **Log state changes** for debugging
6. **Test with backend disconnected** to verify timeout/error behavior
7. **Use consistent naming** across FXML, Controller, ViewModel, and Backend

## Additional Resources

- **UIStateService.java** - Manages pending operations and ACKs
- **TrainViewModel.java** - Example ViewModel implementation
- **TrainController.java** - Example Controller implementation
- **HmiData.java** - Data structure definition
- **DAOService.java** - Data access layer

## Summary

Adding a new button requires:
1. ✅ Define button in FXML with unique fx:id
2. ✅ Add @FXML reference in Controller
3. ✅ Create action method in ViewModel
4. ✅ Bind button to action in Controller's initialize()
5. ✅ Call `markPending()` before data update
6. ✅ Set `HMI_READi = 2` when updating data
7. ✅ Ensure backend has matching database entry
8. ✅ Verify backend clears HMI_READi after processing

The key requirement is that **buttons must wait for backend acknowledgment** using the `UIStateService` to ensure data consistency between frontend and backend.
