package org.example.jsonOperator.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.*;
import org.example.jsonOperator.dao.HMIJSONDAOStub;
import org.example.jsonOperator.dao.IHMIJSONDAO;
import org.example.jsonOperator.dao.ListenerConcurrentMap;
import org.example.jsonOperator.dto.HmiData;

import java.io.File;
import java.io.IOException;
import java.util.*;

public class JSONOperatorServiceStub implements IJSONOperatorService {
    private static final ObjectMapper objectMapper = getDefaultObjectMapper();
    private final IHMIJSONDAO<HmiData> hmiJsonDao;

    /**
     * Default constructor
     */
    public JSONOperatorServiceStub() {
        this(new HMIJSONDAOStub(new ListenerConcurrentMap<>()));
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

    private static String generateString(JsonNode node, boolean pretty) throws JsonProcessingException {
        ObjectWriter objectWriter = objectMapper.writer();
        if (pretty)
            objectWriter = objectWriter.with(SerializationFeature.INDENT_OUTPUT);
        return objectWriter.writeValueAsString(node);
    }

    @Override
    public ListenerConcurrentMap<String, HmiData> readHmiDataMapFromFile(String filePath) throws IOException {
        ListenerConcurrentMap<String, HmiData> hmiDataMap = objectMapper.readValue(new File(filePath), new TypeReference<>() {});
        hmiJsonDao.setHmiDataMap(hmiDataMap);
//        updateIndexWithKeyValue(hmiDataMap);
        return hmiDataMap;
    }
//  TODO: Is this still needed?
    private void updateIndexWithKeyValue(ListenerConcurrentMap<String, HmiData> hmiDataMap) {
        ListenerConcurrentMap<String, HmiData> updatedIndexMap = new ListenerConcurrentMap<>();

        for (Map.Entry<String, HmiData> entry : hmiDataMap.entrySet()) {
            String key = entry.getKey();
            HmiData value = entry.getValue();
            value.setIndex(Integer.parseInt(key)); // The key is a string representation of the index
            updatedIndexMap.put(key, value);
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

    public String getStringToSendToServer(ListenerConcurrentMap<String, HmiData> hmiDataMap) throws JsonProcessingException {
        // make an empty map to store the values that have HMI_READi = 1
        ListenerConcurrentMap<String, HmiData> hmiReadiMap = new ListenerConcurrentMap<>();
        // Loop through the map that is passed in to get the values that have HMI_READi = 1;
        for (Map.Entry<String, HmiData> entry : hmiDataMap.entrySet()) {
            HmiData hmiData = entry.getValue();
            if (hmiData.getHmiReadi() == 1) {
                hmiReadiMap.put(entry.getKey(), hmiData);
                System.out.println(hmiReadiMap);
            }
        }
        return(writeMapToString(hmiReadiMap));
    }

    /**
     * Compare and set HMI_READi to 0 if the value is different from the original value.
     * @param hmiDataMap
     * @param workMap
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

    @Override
    public ListenerConcurrentMap<String, HmiData> writeStringToMap(String jsonString) throws IOException {
        JsonNode jsonNode = objectMapper.readTree(jsonString);
        ListenerConcurrentMap<String, HmiData> resultsMap = new ListenerConcurrentMap<>();
        Iterator<JsonNode> elements = jsonNode.elements();
        while (elements.hasNext()) {
            JsonNode element = elements.next();
            if (element.has("INDEX")) {
                String index = element.get("INDEX").asText();
                HmiData hmiData = objectMapper.treeToValue(element, HmiData.class);
                hmiData.setIndex(Integer.parseInt(index)); // Keep the INDEX value in HmiData
                resultsMap.put(index, hmiData);
            } else {
                System.err.println("Missing INDEX field in element: " + element);
            }
        }
        hmiJsonDao.setHmiDataMap(resultsMap);
        return resultsMap;
    }

    @Override
    public void writeMapToFile(ListenerConcurrentMap<String, ?> map, String filePath) throws IOException {
        objectMapper.configure(SerializationFeature.INDENT_OUTPUT, true);
        objectMapper.writeValue(new File(filePath), map);
    }

    @Override
    public String writeMapToString(ListenerConcurrentMap<String, HmiData> map) {
        List<HmiData> sortedList = new ArrayList<>(map.values());
        sortedList.sort(Comparator.comparing(HmiData::getIndex));

        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < sortedList.size(); i++) {
            sb.append(sortedList.get(i).toString());
            if (i < sortedList.size() - 1) {
                sb.append(",");
            }
        }
        sb.append("]");
        return sb.toString();
    }

    @Override
    public void printMap(ListenerConcurrentMap<String, HmiData> map) {
        System.out.println(hmiJsonDao.fetchAll());
    }
}