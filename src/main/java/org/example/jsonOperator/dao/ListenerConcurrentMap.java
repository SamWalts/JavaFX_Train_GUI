package org.example.jsonOperator.dao;

import org.example.jsonOperator.dto.HmiData;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class ListenerConcurrentMap<K, V> extends ConcurrentHashMap<K, V> {
    public ListenerConcurrentMap(Map<? extends K, ? extends V> m) {
        super(m);
        this.listener = new DefaultListener();
    }

    public interface Listener<K, V> {
        void onPut(K key, V value);
        void onRemove(K key, V value);
    }

    private Listener<K, V> listener;

    public ListenerConcurrentMap(Listener<K, V> listener) {
        this.listener = listener;
    }

//    pblic ListenerConcurrentMap()
    public ListenerConcurrentMap() {
        this.listener = new DefaultListener();
    }

    @Override
    public V put(K key, V value) {
        V oldValue = super.put(key, value);
        if (listener != null) {
            listener.onPut(key, value);
        }
        return oldValue;
    }

    @Override
    public V remove(Object key) {
        V oldValue = super.remove(key);
        if (listener != null && oldValue != null) {
            listener.onRemove((K) key, oldValue);
        }
        return oldValue;
    }

    private class DefaultListener implements Listener<K, V> {
        @Override
        public void onPut(K key, V value) {
            System.out.println("Added: From Listener: " + key + " -> " + value);
        }

        @Override
        public void onRemove(K key, V value) {
            System.out.println("Removed: From Listener: " + key + " -> " + value);
        }
    }
}