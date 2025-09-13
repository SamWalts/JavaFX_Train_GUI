// java
package org.services;

import javafx.beans.property.BooleanProperty;
import javafx.beans.property.SimpleBooleanProperty;
import org.example.jsonOperator.dto.HmiData;

import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

public final class UIStateService {

    private static final UIStateService INSTANCE = new UIStateService();

    private final BooleanProperty waitingForServer = new SimpleBooleanProperty(false);
    private final Set<String> pendingKeys = ConcurrentHashMap.newKeySet();

    private UIStateService() { }

    public static UIStateService getInstance() {
        return INSTANCE;
    }

    public BooleanProperty waitingForServerProperty() {
        return waitingForServer;
    }

    public boolean isWaitingForServer() {
        return waitingForServer.get();
    }

    // Called before sending updates. This is to mark all the keys we expect ACKs for.
    public void markPending(Set<String> keys) {
        if (keys == null || keys.isEmpty()) return;
        pendingKeys.addAll(keys);
        if (!pendingKeys.isEmpty() && !waitingForServer.get()) {
            waitingForServer.set(true);
            System.out.println("[UIState] Pending started for keys=" + pendingKeys);
        } else {
            System.out.println("[UIState] Pending added; keys=" + pendingKeys);
        }
    }

    // Called on every map update from backend/server
    // Consider an ACK when server-side data for key is observed with HMI_READi != 2
    public void checkAck(String key, HmiData updated) {
        if (key == null || updated == null) return;

        if (pendingKeys.contains(key)) {
            Integer readi = updated.getHmiReadi();
            boolean acked = readi == null || readi != 2;

            if (acked) {
                pendingKeys.remove(key);
                System.out.println("[UIState] ACK received for key=" + key + " (HMI_READi=" + readi + ")");
            }
        }

        if (pendingKeys.isEmpty() && waitingForServer.get()) {
            waitingForServer.set(false);
            System.out.println("[UIState] All ACKed. Waiting cleared.");
        }
    }

    // Utility for tests or resets
    public void clearAllPending() {
        pendingKeys.clear();
        if (waitingForServer.get()) {
            waitingForServer.set(false);
            System.out.println("[UIState] Pending cleared manually.");
        }
    }

    public Set<String> getPendingSnapshot() {
        return Set.copyOf(pendingKeys);
    }
}
