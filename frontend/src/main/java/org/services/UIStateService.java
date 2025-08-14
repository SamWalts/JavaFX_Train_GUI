// java
package org.services;

import javafx.beans.property.SimpleBooleanProperty;

public class UIStateService {
    private static final UIStateService instance = new UIStateService();
    private final SimpleBooleanProperty isWaitingForServer = new SimpleBooleanProperty(false);

    private UIStateService() {}

    public static UIStateService getInstance() {
        return instance;
    }

    // Existing property getter
    public SimpleBooleanProperty isWaitingForServer() {
        return isWaitingForServer;
    }

    // New accessor to match controller usage
    public SimpleBooleanProperty waitingForServerProperty() {
        return isWaitingForServer;
    }

    public void setWaitingForServer(boolean waiting) {
        isWaitingForServer.set(waiting);
    }
}