package org.example.jsonOperator.dao;

import java.util.Map;
import java.util.concurrent.*;

public class ListenerConcurrentMap<K, V> extends ConcurrentHashMap<K, V> {
    private final CopyOnWriteArrayList<Listener<K, V>> listeners;
    private final ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor();

    // Debounce configuration
    private static final long DEBOUNCE_DELAY_MS = 50;

    // Pending updates for debounced batch notification
    private final ConcurrentHashMap<K, V> pendingPuts = new ConcurrentHashMap<>();
    private final ConcurrentHashMap<K, V> pendingRemoves = new ConcurrentHashMap<>();
    private ScheduledFuture<?> pendingNotification;

    public ListenerConcurrentMap(Map<? extends K, ? extends V> m) {
        super(m);
        this.listeners = new CopyOnWriteArrayList<>();
        addListener(new DefaultListener());
    }

    public ListenerConcurrentMap() {
        this.listeners = new CopyOnWriteArrayList<>();
        addListener(new DefaultListener());
    }

    public void addListener(Listener<K, V> listener) {
        if (listener != null) {
            listeners.add(listener);
        }
    }

    public void removeListener(Listener<K, V> listener) {
        listeners.remove(listener);
    }

    /**
     * Returns the number of registered listeners (excluding default listener).
     * Useful for debugging listener leaks.
     */
    public int getListenerCount() {
        return listeners.size();
    }

    /**
     * Removes all listeners except the default one.
     * Useful for cleanup.
     */
    public void clearNonDefaultListeners() {
        listeners.removeIf(listener -> !(listener instanceof ListenerConcurrentMap.DefaultListener));
    }

    @Override
    public V put(K key, V value) {
        V oldValue = super.put(key, value);
        pendingPuts.put(key, value);
        scheduleNotification();
        return oldValue;
    }

    @Override
    public V remove(Object key) {
        V oldValue = super.remove(key);
        if (oldValue != null) {
            pendingRemoves.put((K) key, oldValue);
            scheduleNotification();
        }
        return oldValue;
    }

    /**
     * Schedules a debounced notification to listeners.
     * Multiple rapid put/remove calls will be batched into a single notification cycle.
     */
    private synchronized void scheduleNotification() {
        if (pendingNotification != null && !pendingNotification.isDone()) {
            pendingNotification.cancel(false);
        }
        pendingNotification = scheduler.schedule(this::fireNotifications, DEBOUNCE_DELAY_MS, TimeUnit.MILLISECONDS);
    }

    /**
     * Fires all pending notifications to listeners.
     * Called after debounce delay expires.
     */
    private void fireNotifications() {
        // Process pending puts
        ConcurrentHashMap<K, V> putsToFire = new ConcurrentHashMap<>(pendingPuts);
        pendingPuts.clear();

        for (Map.Entry<K, V> entry : putsToFire.entrySet()) {
            for (Listener<K, V> listener : listeners) {
                try {
                    listener.onPut(entry.getKey(), entry.getValue());
                } catch (Exception e) {
                    System.err.println("Error in listener onPut: " + e.getMessage());
                }
            }
        }

        // Process pending removes
        ConcurrentHashMap<K, V> removesToFire = new ConcurrentHashMap<>(pendingRemoves);
        pendingRemoves.clear();

        for (Map.Entry<K, V> entry : removesToFire.entrySet()) {
            for (Listener<K, V> listener : listeners) {
                try {
                    listener.onRemove(entry.getKey(), entry.getValue());
                } catch (Exception e) {
                    System.err.println("Error in listener onRemove: " + e.getMessage());
                }
            }
        }
    }

    /**
     * Immediately fires pending notifications without waiting for debounce.
     * Useful for testing or when immediate notification is required.
     */
    public void flushNotifications() {
        if (pendingNotification != null && !pendingNotification.isDone()) {
            pendingNotification.cancel(false);
        }
        fireNotifications();
    }

    /**
     * Shuts down the scheduler. Call this when the map is no longer needed.
     */
    public void shutdown() {
        scheduler.shutdown();
        try {
            if (!scheduler.awaitTermination(1, TimeUnit.SECONDS)) {
                scheduler.shutdownNow();
            }
        } catch (InterruptedException e) {
            scheduler.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }

    public interface Listener<K, V> {
        void onPut(K key, V value);
        void onRemove(K key, V value);
    }

    private class DefaultListener implements Listener<K, V> {
        @Override
        public void onPut(K key, V value) {
            // Reduced logging - only log count summary during batch operations
            System.out.println("[ListenerConcurrentMap] Put: " + key);
        }

        @Override
        public void onRemove(K key, V value) {
            System.out.println("[ListenerConcurrentMap] Removed: " + key);
        }
    }
}