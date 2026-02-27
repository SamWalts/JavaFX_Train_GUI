package org.services;

/**
 * Interface for resources that need cleanup when a screen is navigated away from.
 * Controllers and ViewModels can implement this interface to be notified
 * when they should release resources like listeners, subscriptions, or background tasks.
 */
public interface Cleanable {
    /**
     * Called when the associated screen is being disposed.
     * Implementations should release any resources such as:
     * - Listeners registered with shared data structures
     * - Background tasks or timers
     * - Open connections
     */
    void cleanup();
}

