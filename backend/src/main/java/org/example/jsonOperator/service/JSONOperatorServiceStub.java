package org.example.jsonOperator.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.*;
import org.example.jsonOperator.dao.HMIJSONDAOSingleton;
import org.example.jsonOperator.dao.IHMIJSONDAO;
import org.example.jsonOperator.dao.ListenerConcurrentMap;
import org.example.jsonOperator.dto.HmiData;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.util.*;
import java.util.stream.Collectors;
public class JSONOperatorServiceStub implements IJSONOperatorService {

    private static final ObjectMapper objectMapper = getDefaultObjectMapper();
    private final IHMIJSONDAO<HmiData> hmiJsonDao;

    /**
     * Default constructor
     */
    public JSONOperatorServiceStub() {
        this.hmiJsonDao = HMIJSONDAOSingleton.getInstance();
    }

    /**
     * Constructor with DAO interface.
     * @param hmiJsonDao IHMIJSONDAO<HmiData>
     */
    public JSONOperatorServiceStub(IHMIJSONDAO<HmiData> hmiJsonDao) {
        this.hmiJsonDao = hmiJsonDao;
    }

    private static ObjectMapper getDefaultObjectMapper() {
        ObjectMapper defaultObjectMapper = new ObjectMapper();
        defaultObjectMapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
        return defaultObjectMapper;
    }

    @Override
    public ListenerConcurrentMap<String, HmiData> getHmiDataMap() {
        return hmiJsonDao.fetchAll();
    }

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
    @Override
    public void updateValue(HmiData data, String variableName, Object newValue) {
        if (data == null) {
            throw new IllegalArgumentException("Data cannot be null");
        }
        if (variableName.equals("HMI_READi")) {
            data.setHmiReadi(1);
        }

        switch (variableName) {
            case "HMI_VALUEi":
                data.setHmiValuei((Integer) newValue);
                data.setHmiReadi(1);
                break;
            case "HMI_VALUEb":
                data.setHmiValueb((Boolean) newValue);
                data.setHmiReadi(1);
                break;
            case "PI_VALUEf":
                data.setPiValuef((Float) newValue);
                data.setHmiReadi(1);
                break;
            case "PI_VALUEb":
                data.setPiValueb((Boolean) newValue);
                data.setHmiReadi(1);
                break;
            default:
                throw new IllegalArgumentException("Unknown variable name: " + variableName);
        }
    }

    /**
     * Check if any of the HMI_READi values are updated to 1.
     * @return boolean
     */
    @Override
    public boolean hasUpdatedHMI_READi() {
        return hmiJsonDao.fetchAll().values().stream().anyMatch(data -> data.getHmiReadi() == 1);
    }

    /**
     * Convert the map to a JSON string to send to the server.
     * @param hmiDataMap
     * @return
     * @throws JsonProcessingException
     */
    public String getStringToSendToServer(ListenerConcurrentMap<String, HmiData> hmiDataMap) throws JsonProcessingException {
        // make an empty map to store the values that have HMI_READi = 1
        ListenerConcurrentMap<String, HmiData> hmiReadiMap = hmiDataMap.entrySet().stream()
                .filter(entry -> entry.getValue().getHmiReadi() == 1)
                .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue, (oldValue, newValue) -> newValue, ListenerConcurrentMap::new));

        if (!hmiReadiMap.isEmpty()) {
            System.out.println(hmiReadiMap);
        }
        return(writeMapToString(hmiReadiMap));
    }

    /**
     * Compare and set HMI_READi to 0 if the value is different from the original value.
     * @param hmiDataMap the map that is being compared.
     * @param workMap the map that is being compared to.
     */
    @Override
    public void compareAndSetHMI_READi(ListenerConcurrentMap<String, HmiData> hmiDataMap, ListenerConcurrentMap<String, HmiData> workMap) {
        for (Map.Entry<String, HmiData> entry : hmiDataMap.entrySet()) {
            HmiData data = entry.getValue();
            HmiData originalData = workMap.get(entry.getKey());
            if (originalData != null && !data.getHmiReadi().equals(originalData.getHmiReadi())) {
                data.setHmiReadi(0);
                System.out.println("HMI_READi updated to 0 for " + data.getTag());
            }
        }
    }

    /**
     * Convert a JSON string to a map and store it in the DAO.
     * @param jsonString the JSON string to convert.
     * @return ListenerConcurrentMap<String, HmiData>
     * @throws IOException
     */
    @Override
    public ListenerConcurrentMap<String, HmiData> writeStringToMap(String jsonString) throws IOException {
        ListenerConcurrentMap<String, HmiData> resultsMap = new ListenerConcurrentMap<>();
        try {
            // Assuming jsonString is an array of HmiData objects
            List<HmiData> hmiDataList = objectMapper.readValue(jsonString, new TypeReference<List<HmiData>>() {});

            for (HmiData hmiData : hmiDataList) {
                if (hmiData.getIndex() != null) {
                    resultsMap.put(String.valueOf(hmiData.getIndex()), hmiData);
                } else if (hmiData.getTag() != null && !hmiData.getTag().isEmpty()) {
                    resultsMap.put(hmiData.getTag(), hmiData);
                } else {
                    System.err.println("Missing INDEX or tag field in element: " + hmiData);
                }
            }
        } catch (JsonProcessingException e) {
            System.err.println("Error parsing JSON string to map: " + e.getMessage());
            throw new IOException("Error parsing JSON string: " + e.getMessage(), e);
        }
        hmiJsonDao.setHmiDataMap(resultsMap);
        return resultsMap;
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
