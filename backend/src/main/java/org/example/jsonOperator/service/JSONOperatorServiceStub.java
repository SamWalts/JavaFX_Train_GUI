package org.example.jsonOperator.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.*;
import org.example.Client.IClientController;
import org.example.jsonOperator.dao.HMIJSONDAOSingleton;
import org.example.jsonOperator.dao.IHMIJSONDAO;
import org.example.jsonOperator.dao.ListenerConcurrentMap;
import org.example.jsonOperator.dto.HmiData;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.util.*;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.logging.Logger;
import java.util.stream.Collectors;
public class JSONOperatorServiceStub implements IJSONOperatorService {
    private static final Logger logger = Logger.getLogger(JSONOperatorServiceStub.class.getName());
    private static final ObjectMapper objectMapper = getDefaultObjectMapper();
    private final IHMIJSONDAO<HmiData> hmiJsonDao;
    private ListenerConcurrentMap<String, HmiData> hmiDataMap;
    private IClientController clientController;

    // TODO: Use an inflight queue to manage data being send to server
    // A queue to hold data that has been sent but not yet confirmed by the server.
    private final ConcurrentLinkedQueue<Set<String>> inFlightBatches = new ConcurrentLinkedQueue<>();

    /**
     * Prepares the JSON string for data that needs to be sent to the server.
     * It moves the relevant data to an "in-flight" state.
     *
     * @return A JSON string of data to be sent, or an empty string if there's nothing to send.
     */
    public String prepareDataForSending() {
        ListenerConcurrentMap<String, HmiData> all = getHmiDataMap();
        if (all == null || all.isEmpty()) {
            logger.info("No HMI data available to send.");
            return "[]";
        }
        Map<String, HmiData> batch = all.entrySet().stream()
                .filter(e -> {
                    HmiData v = e.getValue();
                    return v != null && v.getHmiReadi() != null && v.getHmiReadi() == 2;
                })
                .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));
        if (batch.isEmpty()) {
            logger.info("No HMI data marked as ready to send.");
            return "[]";
        }
        Set<String> batchKeys = new HashSet<>(batch.keySet());
        inFlightBatches.add(batchKeys);
        logger.info("Preparing batch for sending. Keys: " + batchKeys);
        ListenerConcurrentMap<String, HmiData> toWrite = new ListenerConcurrentMap<>(batch);
        String json = writeMapToString(toWrite);
        logger.fine("Serialized batch to JSON: " + json);
        return json;
    }

    //TODO: Implement a method to handle server acknowledgments
    // This method will be called when the server acknowledges receipt of data.
    /**
     * Finalizes the update for in-flight data once the server confirms receipt.
     * This method should be called after receiving "ServerSENDDone".
     * It sets the hmiReadi flag to 0 for all items in the in-flight queue.
     */
    public void finalizeSentData() {
        Set<String> batchKeys = inFlightBatches.poll();
        if (batchKeys == null || batchKeys.isEmpty()) {
            return;
        }
        ListenerConcurrentMap<String, HmiData> all = getHmiDataMap();
        for (String k : batchKeys) {
            HmiData d = all.get(k);
            if (d != null) {
                d.setHmiReadi(0);
                all.put(k, d);
            }
        }
    }

    @Override
    public void setHmiReadi(ListenerConcurrentMap<String, HmiData> hmiDataMap,
                            ListenerConcurrentMap<String, HmiData> workMap) {
        if (hmiDataMap == null || workMap == null) return;
        for (String key : workMap.keySet()) {
            HmiData cur = hmiDataMap.get(key);
            if (cur != null && cur.getHmiReadi() != null && cur.getHmiReadi() > 0) {
                cur.setHmiReadi(0);
                hmiDataMap.put(key, cur);
            }
        }
    }

    /**
     * Default constructor with singleton DAO instance.
     */
    public JSONOperatorServiceStub() {
        this.hmiJsonDao = HMIJSONDAOSingleton.getInstance();
        this.hmiDataMap = hmiJsonDao.fetchAll();
//        setupHmiReadinessListener();
    }

    /**
     * Constructor with DAO interface.
     * @param hmiJsonDao IHMIJSONDAO<HmiData>
     */
    public JSONOperatorServiceStub(IHMIJSONDAO<HmiData> hmiJsonDao) {
        this.hmiJsonDao = hmiJsonDao;
    }

    /**
     * Injects the client controller dependency.
     * @param clientController The client controller instance.
     */
    public void setClientController(IClientController clientController) {
        this.clientController = clientController;
    }


    /**
     * Initializes the service, setting up listeners.
     * This should be called after all dependencies are injected.
     */
    public void initialize() {
        setupHmiReadinessListener();
        System.out.println("JSONOperatorServiceStub initialized with HMI JSON DAO: " + hmiJsonDao);
    }

    /**
     * Get the default ObjectMapper with configuration.
     * @return ObjectMapper
     */
    private static ObjectMapper getDefaultObjectMapper() {
        ObjectMapper defaultObjectMapper = new ObjectMapper();
        defaultObjectMapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
        return defaultObjectMapper;
    }

    /**
     * Get the HMI JSON DAO instance.
     * @return IHMIJSONDAO<HmiData>
     */
    @Override
    public ListenerConcurrentMap<String, HmiData> getHmiDataMap() {
        return hmiJsonDao.fetchAll();
    }

    /**
     * Read HmiData from a JSON file and return a map of HmiData objects.
     * The file can be in either object format ({"key1": {...}, "key2": {...}}) or array format ([{...}, {...}]).
     * @param filePath the path to the JSON file.
     * @return ListenerConcurrentMap<String, HmiData> containing the parsed data.
     * @throws IOException if there is an error reading or parsing the file.
     */
    @Override
    public ListenerConcurrentMap<String, HmiData> readHmiDataMapFromFile(String filePath) throws IOException {
        try {
            InputStream inputStream = getClass().getClassLoader().getResourceAsStream(filePath);
            if (inputStream == null) {
                throw new FileNotFoundException(filePath + " not found in resources");
            }

            ListenerConcurrentMap<String, HmiData> hmiDataMap = hmiJsonDao.fetchAll();
            JsonNode rootNode = objectMapper.readTree(inputStream);

            if (rootNode.isObject()) {
                // Handle JSON object format: {"key1": {...}, "key2": {...}}
                Iterator<Map.Entry<String, JsonNode>> fields = rootNode.fields();
                while (fields.hasNext()) {
                    Map.Entry<String, JsonNode> entry = fields.next();
                    HmiData hmiData = objectMapper.treeToValue(entry.getValue(), HmiData.class);
                    hmiData.setIndex(Integer.parseInt(entry.getKey()));
                    hmiDataMap.put(entry.getKey(), hmiData);
                }
            } else if (rootNode.isArray()) {
                // Handle JSON array format: [{...}, {...}]
                for (JsonNode node : rootNode) {
                    if (node.has("INDEX")) {
                        String key = node.get("INDEX").asText();
                        HmiData hmiData = objectMapper.treeToValue(node, HmiData.class);
                        hmiDataMap.put(key, hmiData);
                    } else if (node.has("tag")) {
                        String key = node.get("tag").asText();
                        HmiData hmiData = objectMapper.treeToValue(node, HmiData.class);
                        hmiDataMap.put(key, hmiData);
                    } else {
                        System.err.println("Missing INDEX or tag field in element: " + node);
                    }
                }
            }

//            hmiJsonDao.setHmiDataMap(hmiDataMap);
            System.out.println("Successfully loaded " + hmiDataMap.size() + " entries from " + filePath);
            return hmiDataMap;
        } catch (JsonProcessingException e) {
            System.err.println("Error parsing JSON from file: " + e.getMessage());
            throw new IOException("Error parsing JSON: " + e.getMessage(), e);
        }
    }

    /**
     * Update the value of a variable in the HmiData object.
     * @param data HmiData object to update.
     * @param variableName name of the variable to update.
     * @param newValue new value to set.
     */
    @Override
    public void updateValue(HmiData data, String variableName, Object newValue) {
        if (data == null) {
            throw new IllegalArgumentException("Data cannot be null");
        }
        if (variableName.equals("HMI_READi")) {
            data.setHmiReadi(2);
        }

        switch (variableName) {
            case "HMI_VALUEi":
                data.setHmiValuei((Integer) newValue);
                data.setHmiReadi(2);
                break;
            case "HMI_VALUEb":
                data.setHmiValueb((Boolean) newValue);
                data.setHmiReadi(2);
                break;
            case "PI_VALUEf":
                data.setPiValuef((Float) newValue);
                data.setHmiReadi(2);
                break;
            case "PI_VALUEb":
                data.setPiValueb((Boolean) newValue);
                data.setHmiReadi(2);
                break;
            default:
                throw new IllegalArgumentException("Unknown variable name: " + variableName);
        }
    }

    /**
     * Check if any of the HMI_READi values are updated to 2, as that indicates an update from the HMI to the server.
     * @return boolean
     */
    @Override
    public boolean hasUpdatedHMI_READi() {
        return hmiJsonDao.fetchAll().values().stream().anyMatch(data -> data.getHmiReadi() == 2);
    }


    private void setupHmiReadinessListener() {
        System.out.println("Setting up HMI readiness listener...");
        if (hmiDataMap == null) {
            hmiDataMap = hmiJsonDao.fetchAll();
        }
        hmiDataMap.addListener(new ListenerConcurrentMap.Listener<>() {
            @Override
            public void onPut(String key, HmiData value) {
                if (value != null && value.getHmiReadi() != null && value.getHmiReadi() == 2) {
                    System.out.println("HMI_READi=2 detected for key: " + key + ". Requesting server ready to receive.");
                    // Trigger handshake: ask server to prepare to receive updates
                    if (clientController != null) {
                        clientController.sendMessage("SendingUpdates");
                    } else {
                        System.err.println("Error: ClientController dependency not injected.");
                    }
                }
            }

            @Override
            public void onRemove(String key, HmiData value) {
                System.out.println("Removed: " + key + " -> " + value);
            }
        });
    }


    /**
     * Filter the ListenerConcurrentMap for any entry that contains getHmiReadi == 2
     * Converts the HmiData into a JSON string to send to the server.
     * @param hmiDataMap
     * @return a JSON string representation of the map.
     * @throws JsonProcessingException
     */
    public String getStringToSendToServer(ListenerConcurrentMap<String, HmiData> hmiDataMap) throws JsonProcessingException {
        // make an empty map to store the values that have HMI_READi = 1
        ListenerConcurrentMap<String, HmiData> hmiReadiMap = hmiDataMap.entrySet().stream()
                .filter(entry -> entry.getValue().getHmiReadi() == 2)
                .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue, (oldValue, newValue) -> newValue, ListenerConcurrentMap::new));

        if (!hmiReadiMap.isEmpty()) {
            System.out.println(hmiReadiMap);
            System.out.println("HMI_READi values updated to 2, sending to server.");
        }
        return(writeMapToString(hmiReadiMap));
    }

    /**
     * Convert a JSON string to a map and store it in the DAO.
     * @param jsonString the JSON string to convert.
     * @return ListenerConcurrentMap<String, HmiData>
     * @throws IOException
     */
    @Override
    public ListenerConcurrentMap<String, HmiData> writeStringToMap(String jsonString) throws IOException {
        try {
            logger.info("Deserializing JSON string to HmiData map. Length: " + jsonString.length());

            // Parse as list (server sends arrays). If a single object arrives, wrap it.
            JsonNode root = objectMapper.readTree(jsonString);
            List<HmiData> hmiDataList = new ArrayList<>();
            if (root.isArray()) {
                for (JsonNode node : root) {
                    hmiDataList.add(objectMapper.treeToValue(node, HmiData.class));
                }
            } else if (root.isObject()) {
                hmiDataList.add(objectMapper.treeToValue(root, HmiData.class));
            } else {
                logger.warning("Unexpected JSON root type: " + root.getNodeType());
            }

            ListenerConcurrentMap<String, HmiData> daoMap = hmiJsonDao.fetchAll();
            int inserted = 0, updated = 0;
            for (HmiData data : hmiDataList) {
                if (data == null) continue;
                String key = data.getIndex();
                if (key == null) continue;
                HmiData prev = daoMap.put(key, data);
                if (prev == null) inserted++; else updated++;
            }
            logger.info("Merged server data into DAO map. Inserted=" + inserted + ", Updated=" + updated + ", TotalSize=" + daoMap.size());
            return daoMap;
        } catch (JsonProcessingException e) {
            logger.severe("Failed to deserialize JSON string: " + e.getMessage());
            throw e;
        }
    }

    @Override
    public void writeMapToFile(ListenerConcurrentMap<String, ?> map, String filePath) throws IOException {
        objectMapper.writeValue(new File(filePath), map);
    }

    @Override
    public String writeMapToString(ListenerConcurrentMap<String, HmiData> map) {
        try {
            // Convert map values to a sorted list
            List<HmiData> sortedList = new ArrayList<>(map.values());
            sortedList.sort(Comparator.comparing(HmiData::getIndex));

            // Use Jackson to convert the sorted list to a JSON string
            return objectMapper.writeValueAsString(sortedList);
        } catch (JsonProcessingException e) {
            System.err.println("Error converting map to JSON: " + e.getMessage());
            // Return empty array as fallback
            return "[]";
        }
    }

    @Override
    public void printMap(ListenerConcurrentMap<String, HmiData> map) {
        System.out.println(hmiJsonDao.fetchAll());
    }
}
