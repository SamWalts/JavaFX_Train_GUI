package org.services;

import javafx.application.Platform;
import javafx.beans.value.ChangeListener;
import javafx.beans.value.ObservableValue;
import org.viewScreens.App;

public final class NavigationService {
    private static final NavigationService INSTANCE = new NavigationService();

    private final UIStateService uiStateService = UIStateService.getInstance();
    private final ChangeListener<Boolean> waitingListener;

    private boolean listenerRegistered = false;
    private String pendingTarget = null;

    private NavigationService() {
        waitingListener = new ChangeListener<Boolean>() {
            @Override
            public void changed(ObservableValue<? extends Boolean> observable,
                                Boolean oldValue,
                                Boolean newValue) {
                if (Boolean.FALSE.equals(newValue) && pendingTarget != null) {
                    navigateNow(pendingTarget);
                    pendingTarget = null;
                }
            }
        };
    }

    public static NavigationService getInstance() {
        return INSTANCE;
    }

    /**
     * Navigate immediately if not waiting; otherwise defer until waiting becomes false.
     */
    public void navigateWhenServerReady(String targetId) {
        if (targetId == null || targetId.isEmpty()) return;

        if (!uiStateService.waitingForServerProperty().get()) {
            navigateNow(targetId);
            return;
        }

        pendingTarget = targetId;
        registerListenerIfNeeded();
    }

    /**
     * Immediate navigation to the given FXML view id.
     */
    public void navigateNow(String targetId) {
        if (targetId == null || targetId.isEmpty()) return;

        Runnable action = new Runnable() {
            @Override
            public void run() {
                try {
                    App.setRoot(targetId);
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        };

        if (Platform.isFxApplicationThread()) {
            action.run();
        } else {
            Platform.runLater(action);
        }
    }

    private void registerListenerIfNeeded() {
        if (!listenerRegistered) {
            uiStateService.waitingForServerProperty().addListener(waitingListener);
            listenerRegistered = true;
        }
    }
}
