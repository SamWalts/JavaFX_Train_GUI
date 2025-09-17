package org.example.jsonOperator.dao;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;

public class ListenerConcurrentMap<K, V> extends ConcurrentHashMap<K, V> {
    private final CopyOnWriteArrayList<Listener<K, V>> listeners;

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

    @Override
    public V put(K key, V value) {
        V oldValue = super.put(key, value);
        for (Listener<K, V> listener : listeners) {
            listener.onPut(key, value);
        }
        return oldValue;
    }

    @Override
    public V remove(Object key) {
        V oldValue = super.remove(key);
        if (oldValue != null) {
            for (Listener<K, V> listener : listeners) {
                listener.onRemove((K) key, oldValue);
            }
        }
        return oldValue;
    }

    public interface Listener<K, V> {
        void onPut(K key, V value);
        void onRemove(K key, V value);
    }

    private class DefaultListener implements Listener<K, V> {
        @Override
        public void onPut(K key, V value) {
            System.out.println("{ListenerConcurrentMap] Added: From Listener: " + key + " -> " + value);
        }

        @Override
        public void onRemove(K key, V value) {
            System.out.println("Removed: From Listener: " + key + " -> " + value);
        }
    }
}