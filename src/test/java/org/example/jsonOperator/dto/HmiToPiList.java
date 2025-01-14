package org.example.jsonOperator.dto;

import java.util.Map;

public class HmiToPiList {
    private Map<String, HmiToPi> items;

    // Getter and setter for items
    public Map<String, HmiToPi> getItems() {
        System.out.println(items);
        return items;
    }
    // Method to get the size of the map
    public int getSize() {
        return items != null ? items.size() : 0;
    }
    public void setItems(Map<String, HmiToPi> items) {
        this.items = items;
    }
}
