package org.example.jsonOperator.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonSetter;

import java.util.logging.Logger;

/**
 *  Data class for HMI data. "INDEX" value will be the key used in the map, and
 *  replicated again inside the value for easy access.
 */
public class HmiData {

    private static final Logger logger = Logger.getLogger(HmiData.class.getName());

    @JsonProperty("INDEX")
    private Integer indexInt;

    // Keep String version for map key compatibility
    private transient String indexStr;

    @JsonProperty("TAG")
    private String tag;

    @JsonProperty("HMI_VALUEb")
    private Boolean hmiValueb;

    @JsonProperty("HMI_VALUEi")
    private Integer hmiValuei;

    @JsonProperty("PI_VALUEf")
    private Float piValuef;

    @JsonProperty("PI_VALUEb")
    private Boolean piValueb;

    @JsonProperty("HMI_READi")
    private Integer hmiReadi;


    // Getters and setters
    /**
     * Returns the index as a String for map key compatibility.
     */
    public String getIndex() {
        if (indexStr != null) {
            return indexStr;
        }
        return indexInt != null ? indexInt.toString() : null;
    }

    /**
     * Returns the index as an Integer for JSON serialization.
     */
    public Integer getIndexAsInt() {
        return indexInt;
    }

    @JsonSetter("INDEX")
    public void setIndex(Object index) {
        if (index instanceof Integer) {
            this.indexInt = (Integer) index;
            this.indexStr = index.toString();
        } else if (index instanceof Number) {
            this.indexInt = ((Number) index).intValue();
            this.indexStr = this.indexInt.toString();
        } else if (index instanceof String) {
            this.indexStr = (String) index;
            try {
                this.indexInt = Integer.parseInt(this.indexStr);
            } catch (NumberFormatException e) {
                logger.warning("Failed to parse INDEX as integer from String value: '" + this.indexStr + "'");
                this.indexInt = null;
            }
        } else if (index != null) {
            this.indexStr = index.toString();
            try {
                this.indexInt = Integer.parseInt(this.indexStr);
            } catch (NumberFormatException e) {
                logger.warning("Failed to parse INDEX as integer from Object value: '" + this.indexStr + "' (type: " + index.getClass().getName() + ")");
                this.indexInt = null;
            }
        }
    }

    public void setIndex(String index) {
        this.indexStr = index;
        if (index != null) {
            try {
                this.indexInt = Integer.parseInt(index);
            } catch (NumberFormatException e) {
                logger.warning("Failed to parse INDEX as integer from String: '" + index + "'");
                this.indexInt = null;
            }
        } else {
            this.indexInt = null;
        }
    }

    public void setIndex(Integer index) {
        this.indexInt = index;
        this.indexStr = index != null ? index.toString() : null;
    }

    public String getTag() {
        return tag;
    }

    public void setTag(String tag) {
        this.tag = tag;
    }

    public Boolean getHmiValueb() {
        return hmiValueb;
    }

    public void setHmiValueb(Boolean hmiValueb) {
        this.hmiValueb = hmiValueb;
    }

    public Integer getHmiValuei() {
        return hmiValuei;
    }

    public void setHmiValuei(Integer hmiValuei) {
        this.hmiValuei = hmiValuei;
    }

    public Float getPiValuef() {
        return piValuef;
    }

    public void setPiValuef(Float piValuef) {
        this.piValuef = piValuef;
    }

    public Boolean getPiValueb() {
        return piValueb;
    }

    public void setPiValueb(Boolean piValueb) {
        this.piValueb = piValueb;
    }

    public Integer getHmiReadi() {
        return hmiReadi;
    }

    public void setHmiReadi(Integer hmiReadi) {
        this.hmiReadi = hmiReadi;
    }


    @Override
    public String toString() {
        return "{" +
                "\"INDEX\": " + indexInt +
                ", \"TAG\": \"" + tag + "\"" +
                ", \"HMI_VALUEi\": " + hmiValuei +
                ", \"HMI_VALUEb\": " + hmiValueb +
                ", \"PI_VALUEf\": " + piValuef +
                ", \"PI_VALUEb\": " + piValueb +
                ", \"HMI_READi\": " + hmiReadi +
                '}';
    }
}
