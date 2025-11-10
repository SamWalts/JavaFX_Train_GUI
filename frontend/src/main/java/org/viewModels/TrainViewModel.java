package org.viewModels;

import javafx.beans.property.*;
import org.example.jsonOperator.dto.HmiData;
import org.services.DAOService;
import org.services.HMIChangeListener;
import org.services.UIStateService;

import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

public class TrainViewModel extends AbstractHmiViewModel {

    private final BooleanProperty dieselMode = new SimpleBooleanProperty(true);
    private final BooleanProperty hornVisible = new SimpleBooleanProperty();
    private final BooleanProperty whistleVisible = new SimpleBooleanProperty();
    private final BooleanProperty bellVisible = new SimpleBooleanProperty();

    private final StringProperty rr1abSpeed = new SimpleStringProperty("0.0");
    private final StringProperty rr1cdSpeed = new SimpleStringProperty("0.0");
    private final StringProperty rr2abSpeed = new SimpleStringProperty("0.0");

    private final Map<String, BooleanProperty> switchStates = new ConcurrentHashMap<>();
    private final DAOService daoService;

    private final Set<String> backendMainSeen = ConcurrentHashMap.newKeySet();

    private static final Map<String,String> TAG_ALIASES = new ConcurrentHashMap<>();
    static {
        TAG_ALIASES.put("HMI_Switch2b", "HMI_Switch2RR3b");
        TAG_ALIASES.put("HMI_Switch3b", "HMI_Switch3RR4b");
        TAG_ALIASES.put("HMI_Switch4b", "HMI_Switch4RR3b");
        TAG_ALIASES.put("Switch1Main_HMIb", "HMI_Switch1ABb");
        TAG_ALIASES.put("Switch2RR3Main_HMIb", "HMI_Switch2RR3b");
        TAG_ALIASES.put("Switch3RR4Main_HMIb", "HMI_Switch3RR4b");
        TAG_ALIASES.put("Switch4RR3Main_HMIb", "HMI_Switch4RR3b");
        TAG_ALIASES.put("Switch5Main_HMIb", "HMI_Switch5ABb");
        TAG_ALIASES.put("Switch6Main_HMIb", "HMI_Switch6ABb");
    }

    private final Map<String, Boolean> pendingDesiredSwitchState = new ConcurrentHashMap<>();

    public TrainViewModel() {
        this.daoService = DAOService.getInstance();
        new HMIChangeListener(daoService.getHmiJsonDao(), this);

        initializeSwitchStates();
        hydrateInitialSwitchStates();

        // Bind sound control visibility to the diesel/steam mode
        hornVisible.bind(dieselMode);
        whistleVisible.bind(dieselMode.not());
        bellVisible.bind(dieselMode.not());

        System.out.println("TrainViewModel initialized.");
    }

    private void initializeSwitchStates() {
        // Tags must match the "TAG" in your JSON for the switches
        switchStates.put("HMI_Switch1ABb", new SimpleBooleanProperty(false));
        switchStates.put("HMI_Switch2RR3b", new SimpleBooleanProperty(false));
        switchStates.put("HMI_Switch3RR4b", new SimpleBooleanProperty(false));
        switchStates.put("HMI_Switch4RR3b", new SimpleBooleanProperty(false));
        switchStates.put("HMI_Switch5ABb", new SimpleBooleanProperty(false));
        switchStates.put("HMI_Switch6ABb", new SimpleBooleanProperty(false));
    }

    private void hydrateInitialSwitchStates() {
        // Build temporary holders to decide canonical initial state preferring backend main feedback
        Map<String, Boolean> initial = new ConcurrentHashMap<>();
        // First pass: main variant rows (Switch*Main_HMIb) using PI_VALUEb then HMI_VALUEb
        daoService.getHmiDataMap().values().forEach(d -> {
            String tag = d.getTag();
            if (tag == null) return;
            if (tag.startsWith("Switch") && tag.endsWith("HMIb")) {
                String canonical = canonicalTag(tag);
                if (switchStates.containsKey(canonical)) {
                    Boolean val = d.getPiValueb() != null ? d.getPiValueb() : d.getHmiValueb();
                    if (val != null) initial.put(canonical, val);
                }
            }
        });
        // Second pass: HMI command rows fill any not yet set
        daoService.getHmiDataMap().values().forEach(d -> {
            String tag = d.getTag();
            if (tag == null) return;
            String canonical = canonicalTag(tag);
            if (switchStates.containsKey(canonical) && !initial.containsKey(canonical)) {
                Boolean val = d.getPiValueb() != null ? d.getPiValueb() : d.getHmiValueb();
                if (val != null) initial.put(canonical, val);
            }
        });
        // Apply
        initial.forEach((canon, val) -> {
            BooleanProperty prop = switchStates.get(canon);
            if (prop != null) {
                prop.set(val);
                System.out.println("[TrainViewModel] Initial state set for " + canon + " = " + val);
            }
        });
    }

    private String canonicalTag(String tag) { return TAG_ALIASES.getOrDefault(tag, tag); }

    private String mainVariant(String canonical) {
        if (canonical.startsWith("HMI_Switch1")) return "Switch1Main_HMIb";
        if (canonical.startsWith("HMI_Switch2RR3")) return "Switch2RR3Main_HMIb";
        if (canonical.startsWith("HMI_Switch3RR4")) return "Switch3RR4Main_HMIb";
        if (canonical.startsWith("HMI_Switch4RR3")) return "Switch4RR3Main_HMIb";
        if (canonical.startsWith("HMI_Switch5")) return "Switch5Main_HMIb";
        if (canonical.startsWith("HMI_Switch6")) return "Switch6Main_HMIb";
        return null;
    }

    @Override
    protected void applyData(HmiData data, String key) {
        String tag = data.getTag();
        if (tag == null) return;
        String canonical = canonicalTag(tag);
        boolean aliasUsed = !canonical.equals(tag);
        boolean isBackendMain = tag.startsWith("Switch") && tag.endsWith("HMIb");
        if (isBackendMain) backendMainSeen.add(canonical);

        Integer readi = data.getHmiReadi();
        boolean isAck = readi == null || readi != 2; // Only treat as ACK when HMI_READi != 2

        boolean allowFromHmi = !isBackendMain && !backendMainSeen.contains(canonical);
        boolean allow = isBackendMain || allowFromHmi;

        if (switchStates.containsKey(canonical)) {
            BooleanProperty prop = switchStates.get(canonical);
            boolean oldVal = prop.get();

            if (!isAck) {
                System.out.println("[TrainViewModel] Ignoring pending (HMI_READi=2) update tag=" + tag + (aliasUsed?" (alias->"+canonical+")":""));
            } else {
                Boolean candidate = data.getPiValueb();
                if (candidate == null) candidate = data.getHmiValueb();

                boolean hasPending = pendingDesiredSwitchState.containsKey(canonical);
                Boolean desired = pendingDesiredSwitchState.get(canonical);

                // If we have a pending desired state and haven't yet seen a backend main change reflecting it,
                // allow the HMI ACK row to drive the UI even if backendMainSeen already contains the canonical tag.
                boolean allowPendingHmiAck = !isBackendMain && hasPending && desired != null && candidate != null && candidate.equals(desired);

                if (isBackendMain && hasPending && desired != null && candidate != null && candidate.equals(desired)) {
                    // Main variant now reflects desired state; clear pending
                    pendingDesiredSwitchState.remove(canonical);
                }

                if (!allow && !allowPendingHmiAck) {
                    System.out.println("[TrainViewModel] Skipping non-main HMI update post-ACK tag=" + tag + " (main already authoritative, no pending override)");
                } else {
                    // We can apply either because it's backend main OR HMI before main OR pending desired ack
                    if (candidate != null && oldVal != candidate) {
                        prop.set(candidate);
                        System.out.println("[TrainViewModel] Switch state applied post-ACK tag=" + tag + (aliasUsed?" (alias->"+canonical+")":"") +
                                " old=" + oldVal + " new=" + candidate + " (pi=" + data.getPiValueb() + ", hmi=" + data.getHmiValueb() + ")" +
                                (isBackendMain?" [MAIN]": (allowPendingHmiAck?" [PENDING-HMI-ACK]": (!isBackendMain && backendMainSeen.contains(canonical)?" [HMI SUPERSEDED]":""))));
                    } else if (hasPending && desired != null && oldVal == desired) {
                        // Already matches desired; clear pending
                        pendingDesiredSwitchState.remove(canonical);
                    }
                }
            }
        }

        switch (canonical) {
            case "HMI_RRDieselSteamb" -> { if (data.getHmiValueb() != null && isAck) dieselMode.set(data.getHmiValueb()); }
            case "RR1ABspeed_HMI" -> { if (data.getPiValuef() != null && isAck) rr1abSpeed.set(String.format("%.2f", data.getPiValuef())); }
            case "RR1CDspeed_HMI" -> { if (data.getPiValuef() != null && isAck) rr1cdSpeed.set(String.format("%.2f", data.getPiValuef())); }
            case "RR2ABspeed_HMI" -> { if (data.getPiValuef() != null && isAck) rr2abSpeed.set(String.format("%.2f", data.getPiValuef())); }
        }
    }

    private Optional<HmiData> findDataByTag(String tag) { return daoService.getHmiDataMap().values().stream().filter(d -> tag.equals(d.getTag())).findFirst(); }

    public void toggleSwitch(String tag) {
        String canonical = canonicalTag(tag);
        HmiData hmiEntry = findDataByTag(canonical).orElse(null);
        if (hmiEntry == null) return;
        boolean currentState = hmiEntry.getHmiValueb() != null && hmiEntry.getHmiValueb();
        boolean newState = !currentState;
        pendingDesiredSwitchState.put(canonical, newState);
        UIStateService.getInstance().markPending(Set.of(String.valueOf(hmiEntry.getIndex())));
        hmiEntry.setHmiValueb(newState);
        hmiEntry.setHmiReadi(2);
        daoService.getHmiDataMap().put(String.valueOf(hmiEntry.getIndex()), hmiEntry);
        System.out.println("[TrainViewModel] toggleSwitch request canonical=" + canonical + " newState=" + newState + " (waiting ACK, pending recorded)");
    }

    public void toggleHmiAction(String tag) { findDataByTag(tag).ifPresent(data -> { boolean currentState = data.getHmiValueb() != null && data.getHmiValueb(); UIStateService.getInstance().markPending(Set.of(String.valueOf(data.getIndex()))); data.setHmiValueb(!currentState); data.setHmiReadi(2); daoService.getHmiDataMap().put(String.valueOf(data.getIndex()), data); }); }

    public BooleanProperty getSwitchStateProperty(String tag) { return switchStates.get(tag); }
    public BooleanProperty hornVisibleProperty() { return hornVisible; }
    public BooleanProperty whistleVisibleProperty() { return whistleVisible; }
    public BooleanProperty bellVisibleProperty() { return bellVisible; }
    public StringProperty rr1abSpeedProperty() { return rr1abSpeed; }
    public StringProperty rr1cdSpeedProperty() { return rr1cdSpeed; }
    public StringProperty rr2abSpeedProperty() { return rr2abSpeed; }
    public StringProperty jsonStringProperty() { return super.jsonStringProperty(); }
}