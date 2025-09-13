// java
package org.example.jsonOperator;

import org.example.jsonOperator.dao.HMIJSONDAOStub;
import org.example.jsonOperator.dao.ListenerConcurrentMap;
import org.example.jsonOperator.dto.HmiData;
import org.example.jsonOperator.service.JSONOperatorServiceStub;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.lang.reflect.Field;
import java.util.Set;
import java.util.concurrent.ConcurrentLinkedQueue;

import static org.junit.jupiter.api.Assertions.*;

class JSONQueueTests {

    private JSONOperatorServiceStub service;
    private HMIJSONDAOStub dao;

    // Minimal test data (two entries)
    private static final String TWO_ENTRY_JSON = """
        [
          {"INDEX":1,"TAG":"A","HMI_VALUEb":false,"HMI_VALUEi":0,"PI_VALUEf":0.0,"PI_VALUEb":null,"HMI_READi":0},
          {"INDEX":2,"TAG":"B","HMI_VALUEb":true,"HMI_VALUEi":0,"PI_VALUEf":0.0,"PI_VALUEb":null,"HMI_READi":0}
        ]
        """;

    @BeforeEach
    void setUp() throws Exception {
        dao = new HMIJSONDAOStub();
        service = new JSONOperatorServiceStub(dao);

        // Prepare a small map and inject into DAO so service works on it
        ListenerConcurrentMap<String, HmiData> map = service.writeStringToMap(TWO_ENTRY_JSON);
        dao.setHmiDataMap(map);

        // Optional: initialize listeners if they are used internally
        service.initialize();
    }

    @SuppressWarnings("unchecked")
    private ConcurrentLinkedQueue<Set<String>> getInFlightQueue(JSONOperatorServiceStub s) throws Exception {
        Field f = JSONOperatorServiceStub.class.getDeclaredField("inFlightBatches");
        f.setAccessible(true);
        return (ConcurrentLinkedQueue<Set<String>>) f.get(s);
    }

    @Test
    @DisplayName("prepareDataForSending enqueues a batch and returns a payload")
    void testPrepareEnqueuesBatch() throws Exception {
        // Mark entries as updated (which implies HMI_READi should become 2)
        HmiData d1 = dao.fetchAll().get("1");
        HmiData d2 = dao.fetchAll().get("2");
        // Use service API to update so HMI_READi is set to 2
        service.updateValue(d1, "HMI_VALUEi", 11);
        service.updateValue(d2, "HMI_VALUEb", false);

        String payload = service.prepareDataForSending();
        assertNotNull(payload);
        assertFalse(payload.isBlank());
        assertTrue(payload.contains("\"HMI_READi\":2"));

        var q = getInFlightQueue(service);
        assertEquals(1, q.size(), "One batch should be queued");
        Set<String> batch = q.peek();
        assertNotNull(batch);
        assertTrue(batch.contains("1"));
        assertTrue(batch.contains("2"));
    }

    @Test
    @DisplayName("finalizeSentData dequeues batch and clears flags")
    void testFinalizeDequeuesAndClears() throws Exception {
        // Arrange: enqueue a batch
        HmiData d1 = dao.fetchAll().get("1");
        HmiData d2 = dao.fetchAll().get("2");
        service.updateValue(d1, "HMI_VALUEi", 22);
        service.updateValue(d2, "HMI_VALUEb", true);
        String payload = service.prepareDataForSending();
        assertNotNull(payload);

        var qBefore = getInFlightQueue(service);
        assertEquals(1, qBefore.size());

        // Act: simulate server ACK
        service.finalizeSentData();

        // Assert: queue is drained and flags are cleared (no longer 2)
        var qAfter = getInFlightQueue(service);
        assertEquals(0, qAfter.size(), "Queue should be empty after finalize");

        assertNotEquals(2, dao.fetchAll().get("1").getHmiReadi(), "HMI_READi should be cleared for entry 1");
        assertNotEquals(2, dao.fetchAll().get("2").getHmiReadi(), "HMI_READi should be cleared for entry 2");
    }

    @Test
    @DisplayName("Multiple prepare calls enqueue multiple batches")
    void testMultiplePrepareCreatesMultipleBatches() throws Exception {
        // First batch
        service.updateValue(dao.fetchAll().get("1"), "HMI_VALUEi", 33);
        String p1 = service.prepareDataForSending();
        assertNotNull(p1);

        // Second batch (re-update another value)
        service.updateValue(dao.fetchAll().get("2"), "HMI_VALUEi", 44);
        String p2 = service.prepareDataForSending();
        assertNotNull(p2);

        var q = getInFlightQueue(service);
        assertEquals(2, q.size(), "Two batches should be queued");
    }
}