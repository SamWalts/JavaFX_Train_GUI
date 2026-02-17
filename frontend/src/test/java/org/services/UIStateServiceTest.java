package org.services;

import org.example.jsonOperator.dto.HmiData;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.Set;

import static org.junit.jupiter.api.Assertions.*;

class UIStateServiceTest {

    private UIStateService uiStateService;

    @BeforeEach
    void setUp() {
        uiStateService = UIStateService.getInstance();
        // Clear any state from previous tests
        uiStateService.clearAllPending();
    }

    @AfterEach
    void tearDown() {
        // Clean up after each test
        uiStateService.clearAllPending();
    }

    @Test
    void testSingletonInstance() {
        // Get two instances
        UIStateService instance1 = UIStateService.getInstance();
        UIStateService instance2 = UIStateService.getInstance();

        // Verify they are the same instance
        assertSame(instance1, instance2, "UIStateService should be a singleton");
    }

    @Test
    void testInitialState() {
        // Verify initial state
        assertFalse(uiStateService.isWaitingForServer(), "Initial state should not be waiting for server");
        assertTrue(uiStateService.getPendingSnapshot().isEmpty(), "Initial pending set should be empty");
    }

    @Test
    void testMarkPendingWithNullKeys() {
        // Mark pending with null keys
        uiStateService.markPending(null);

        // Verify state hasn't changed
        assertFalse(uiStateService.isWaitingForServer(), "Should not be waiting for server with null keys");
        assertTrue(uiStateService.getPendingSnapshot().isEmpty(), "Pending set should be empty with null keys");
    }

    @Test
    void testMarkPendingWithEmptyKeys() {
        // Mark pending with empty set
        uiStateService.markPending(Set.of());

        // Verify state hasn't changed
        assertFalse(uiStateService.isWaitingForServer(), "Should not be waiting for server with empty keys");
        assertTrue(uiStateService.getPendingSnapshot().isEmpty(), "Pending set should be empty with empty keys");
    }

    @Test
    void testMarkPendingSingleKey() {
        // Mark pending with a single key
        Set<String> keys = Set.of("key1");
        uiStateService.markPending(keys);

        // Verify state changed
        assertTrue(uiStateService.isWaitingForServer(), "Should be waiting for server after marking pending");
        assertEquals(keys, uiStateService.getPendingSnapshot(), "Pending keys should match");
    }

    @Test
    void testMarkPendingMultipleKeys() {
        // Mark pending with multiple keys
        Set<String> keys = Set.of("key1", "key2", "key3");
        uiStateService.markPending(keys);

        // Verify state changed
        assertTrue(uiStateService.isWaitingForServer(), "Should be waiting for server after marking pending");
        assertEquals(keys, uiStateService.getPendingSnapshot(), "Pending keys should match");
    }

    @Test
    void testMarkPendingMultipleTimes() {
        // Mark pending with first set of keys
        Set<String> keys1 = Set.of("key1", "key2");
        uiStateService.markPending(keys1);

        assertTrue(uiStateService.isWaitingForServer(), "Should be waiting for server");
        assertEquals(2, uiStateService.getPendingSnapshot().size(), "Should have 2 pending keys");

        // Mark pending with second set of keys
        Set<String> keys2 = Set.of("key3", "key4");
        uiStateService.markPending(keys2);

        assertTrue(uiStateService.isWaitingForServer(), "Should still be waiting for server");
        assertEquals(4, uiStateService.getPendingSnapshot().size(), "Should have 4 pending keys total");
        assertTrue(uiStateService.getPendingSnapshot().containsAll(Set.of("key1", "key2", "key3", "key4")));
    }

    @Test
    void testCheckAckWithNullKey() {
        // Mark a key as pending
        uiStateService.markPending(Set.of("key1"));

        // Create HmiData
        HmiData hmiData = new HmiData();
        hmiData.setHmiReadi(1);

        // Check ack with null key
        uiStateService.checkAck(null, hmiData);

        // Verify state hasn't changed
        assertTrue(uiStateService.isWaitingForServer(), "Should still be waiting for server");
        assertEquals(1, uiStateService.getPendingSnapshot().size(), "Should still have 1 pending key");
    }

    @Test
    void testCheckAckWithNullData() {
        // Mark a key as pending
        uiStateService.markPending(Set.of("key1"));

        // Check ack with null data
        uiStateService.checkAck("key1", null);

        // Verify state hasn't changed
        assertTrue(uiStateService.isWaitingForServer(), "Should still be waiting for server");
        assertEquals(1, uiStateService.getPendingSnapshot().size(), "Should still have 1 pending key");
    }

    @Test
    void testCheckAckForNonPendingKey() {
        // Mark a key as pending
        uiStateService.markPending(Set.of("key1"));

        // Create HmiData
        HmiData hmiData = new HmiData();
        hmiData.setHmiReadi(1);

        // Check ack for a different key
        uiStateService.checkAck("key2", hmiData);

        // Verify state hasn't changed
        assertTrue(uiStateService.isWaitingForServer(), "Should still be waiting for server");
        assertEquals(1, uiStateService.getPendingSnapshot().size(), "Should still have 1 pending key");
    }

    @Test
    void testCheckAckWithReadi2() {
        // Mark a key as pending
        uiStateService.markPending(Set.of("key1"));

        // Create HmiData with HMI_READi = 2 (not acked)
        HmiData hmiData = new HmiData();
        hmiData.setHmiReadi(2);

        // Check ack
        uiStateService.checkAck("key1", hmiData);

        // Verify key is still pending (HMI_READi == 2 means not acked)
        assertTrue(uiStateService.isWaitingForServer(), "Should still be waiting for server");
        assertEquals(1, uiStateService.getPendingSnapshot().size(), "Should still have 1 pending key");
    }

    @Test
    void testCheckAckWithReadiNot2() {
        // Mark a key as pending
        uiStateService.markPending(Set.of("key1"));

        // Create HmiData with HMI_READi != 2 (acked)
        HmiData hmiData = new HmiData();
        hmiData.setHmiReadi(1);

        // Check ack
        uiStateService.checkAck("key1", hmiData);

        // Verify key is removed and state is cleared
        assertFalse(uiStateService.isWaitingForServer(), "Should not be waiting for server after ack");
        assertTrue(uiStateService.getPendingSnapshot().isEmpty(), "Pending set should be empty after ack");
    }

    @Test
    void testCheckAckWithNullReadi() {
        // Mark a key as pending
        uiStateService.markPending(Set.of("key1"));

        // Create HmiData with null HMI_READi (considered acked)
        HmiData hmiData = new HmiData();
        hmiData.setHmiReadi(null);

        // Check ack
        uiStateService.checkAck("key1", hmiData);

        // Verify key is removed and state is cleared
        assertFalse(uiStateService.isWaitingForServer(), "Should not be waiting for server after ack");
        assertTrue(uiStateService.getPendingSnapshot().isEmpty(), "Pending set should be empty after ack");
    }

    @Test
    void testCheckAckMultipleKeys() {
        // Mark multiple keys as pending
        uiStateService.markPending(Set.of("key1", "key2", "key3"));

        // Create HmiData
        HmiData hmiData = new HmiData();
        hmiData.setHmiReadi(1);

        // Check ack for first key
        uiStateService.checkAck("key1", hmiData);
        assertTrue(uiStateService.isWaitingForServer(), "Should still be waiting for server");
        assertEquals(2, uiStateService.getPendingSnapshot().size(), "Should have 2 pending keys");

        // Check ack for second key
        uiStateService.checkAck("key2", hmiData);
        assertTrue(uiStateService.isWaitingForServer(), "Should still be waiting for server");
        assertEquals(1, uiStateService.getPendingSnapshot().size(), "Should have 1 pending key");

        // Check ack for third key
        uiStateService.checkAck("key3", hmiData);
        assertFalse(uiStateService.isWaitingForServer(), "Should not be waiting for server after all acks");
        assertTrue(uiStateService.getPendingSnapshot().isEmpty(), "Pending set should be empty after all acks");
    }

    @Test
    void testClearAllPendingWhenWaiting() {
        // Mark keys as pending
        uiStateService.markPending(Set.of("key1", "key2"));
        assertTrue(uiStateService.isWaitingForServer(), "Should be waiting for server");

        // Clear all pending
        uiStateService.clearAllPending();

        // Verify state is cleared
        assertFalse(uiStateService.isWaitingForServer(), "Should not be waiting for server after clear");
        assertTrue(uiStateService.getPendingSnapshot().isEmpty(), "Pending set should be empty after clear");
    }

    @Test
    void testClearAllPendingWhenNotWaiting() {
        // Clear all pending when not waiting
        uiStateService.clearAllPending();

        // Verify state is still clear
        assertFalse(uiStateService.isWaitingForServer(), "Should not be waiting for server");
        assertTrue(uiStateService.getPendingSnapshot().isEmpty(), "Pending set should be empty");
    }

    @Test
    void testWaitingForServerProperty() {
        // Get the property
        var property = uiStateService.waitingForServerProperty();
        assertNotNull(property, "Property should not be null");
        assertFalse(property.get(), "Initial property value should be false");

        // Mark keys as pending
        uiStateService.markPending(Set.of("key1"));
        assertTrue(property.get(), "Property value should be true after marking pending");

        // Clear all pending
        uiStateService.clearAllPending();
        assertFalse(property.get(), "Property value should be false after clearing");
    }

    @Test
    void testGetPendingSnapshotIsImmutable() {
        // Mark keys as pending
        uiStateService.markPending(Set.of("key1", "key2"));

        // Get snapshot
        Set<String> snapshot = uiStateService.getPendingSnapshot();
        assertEquals(2, snapshot.size(), "Snapshot should have 2 keys");

        // Verify snapshot is immutable
        assertThrows(UnsupportedOperationException.class, () -> snapshot.add("key3"),
                "Snapshot should be immutable");
        assertThrows(UnsupportedOperationException.class, () -> snapshot.remove("key1"),
                "Snapshot should be immutable");
    }

    @Test
    void testComplexScenario() {
        // Mark first batch of keys
        uiStateService.markPending(Set.of("key1", "key2", "key3"));
        assertTrue(uiStateService.isWaitingForServer());
        assertEquals(3, uiStateService.getPendingSnapshot().size());

        // Ack one key
        HmiData hmiData = new HmiData();
        hmiData.setHmiReadi(0);
        uiStateService.checkAck("key1", hmiData);
        assertTrue(uiStateService.isWaitingForServer());
        assertEquals(2, uiStateService.getPendingSnapshot().size());

        // Mark more keys while still waiting
        uiStateService.markPending(Set.of("key4", "key5"));
        assertTrue(uiStateService.isWaitingForServer());
        assertEquals(4, uiStateService.getPendingSnapshot().size());

        // Ack remaining keys
        uiStateService.checkAck("key2", hmiData);
        uiStateService.checkAck("key3", hmiData);
        uiStateService.checkAck("key4", hmiData);
        assertTrue(uiStateService.isWaitingForServer());
        assertEquals(1, uiStateService.getPendingSnapshot().size());

        uiStateService.checkAck("key5", hmiData);
        assertFalse(uiStateService.isWaitingForServer());
        assertTrue(uiStateService.getPendingSnapshot().isEmpty());
    }
}
