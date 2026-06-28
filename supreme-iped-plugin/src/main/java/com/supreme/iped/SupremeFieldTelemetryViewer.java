package com.supreme.iped;

import java.awt.BorderLayout;
import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.Locale;
import java.util.Map;

import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JTable;
import javax.swing.ListSelectionModel;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;
import javax.swing.event.TableModelEvent;
import javax.swing.event.TableModelListener;
import javax.swing.table.TableModel;

import bibliothek.gui.dock.common.DefaultSingleCDockable;
import iped.data.IIPEDSource;
import iped.data.IItem;
import iped.data.IItemId;
import iped.viewers.api.GUIProvider;
import iped.viewers.api.IMultiSearchResultProvider;
import iped.viewers.api.ResultSetViewer;

public final class SupremeFieldTelemetryViewer implements ResultSetViewer, ListSelectionListener, TableModelListener {
    public static final String PLUGIN_VERSION = "SUPREME-IPED-PLUGIN-1.0.0";
    public static final String SCHEMA_VERSION = "SUPREME-FIELD-EVENTS-1.0";

    private final JPanel panel = new JPanel(new BorderLayout());
    private JTable resultsTable;
    private IMultiSearchResultProvider resultsProvider;
    private GUIProvider guiProvider;
    private DefaultSingleCDockable dockable;
    private IItemId currentItemId;
    private long currentOpenedAtMillis;
    private String previousHash = "";
    private final Path logPath;

    public SupremeFieldTelemetryViewer() {
        panel.add(new JLabel("SUPREME field telemetry active"), BorderLayout.CENTER);
        String configured = System.getProperty("supreme.plugin.event.log");
        if (configured == null || configured.trim().isEmpty()) {
            configured = System.getenv("SUPREME_PLUGIN_EVENT_LOG");
        }
        if (configured == null || configured.trim().isEmpty()) {
            configured = Paths.get(System.getProperty("user.home"), ".supreme", "iped-events.ndjson").toString();
        }
        logPath = Paths.get(configured);
        Runtime.getRuntime().addShutdownHook(new Thread(() -> emit("session_end", currentItemId, resolveItem(currentItemId), 0L),
                "supreme-session-end-hook"));
    }

    @Override
    public void init(JTable resultsTable, IMultiSearchResultProvider resultsProvider, GUIProvider guiProvider) {
        this.resultsTable = resultsTable;
        this.resultsProvider = resultsProvider;
        this.guiProvider = guiProvider;
        if (resultsTable != null) {
            resultsTable.getSelectionModel().addListSelectionListener(this);
            resultsTable.getModel().addTableModelListener(this);
        }
        emit("session_start", null, null, 0L);
    }

    @Override
    public void valueChanged(ListSelectionEvent event) {
        if (event.getValueIsAdjusting() || resultsTable == null) {
            return;
        }
        int viewRow = resultsTable.getSelectedRow();
        IItemId next = resolveItemId(viewRow);
        if (next == null || (currentItemId != null && currentItemId.compareTo(next) == 0)) {
            return;
        }
        closeCurrent();
        currentItemId = next;
        currentOpenedAtMillis = System.currentTimeMillis();
        emit("item_open", next, resolveItem(next), 0L);
        emit(mediaEventType(resolveItem(next)), next, resolveItem(next), 0L);
    }

    @Override
    public void tableChanged(TableModelEvent event) {
        if (event.getType() == TableModelEvent.UPDATE && event.getFirstRow() >= 0) {
            int modelRow = event.getFirstRow();
            int viewRow = resultsTable == null ? modelRow : resultsTable.convertRowIndexToView(modelRow);
            IItemId itemId = resolveItemId(viewRow);
            emit("classification_event", itemId, resolveItem(itemId), 0L);
        }
    }

    @Override
    public void redraw() {
        emit("redraw", currentItemId, resolveItem(currentItemId), 0L);
    }

    @Override
    public void updateSelection() {
        if (resultsTable != null && resultsTable.getSelectionModel().getSelectionMode() != ListSelectionModel.SINGLE_SELECTION) {
            resultsTable.getSelectionModel().setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
        }
    }

    @Override
    public void checkAll(boolean value) {
        emit(value ? "check_all" : "uncheck_all", currentItemId, resolveItem(currentItemId), 0L);
    }

    @Override
    public void notifyCaseDataChanged() {
        emit("case_data_changed", currentItemId, resolveItem(currentItemId), 0L);
    }

    @Override
    public JPanel getPanel() {
        return panel;
    }

    @Override
    public String getTitle() {
        return "SUPREME";
    }

    @Override
    public String getID() {
        return "supreme-field-telemetry";
    }

    @Override
    public GUIProvider getGUIProvider() {
        return guiProvider;
    }

    @Override
    public void setDockableContainer(DefaultSingleCDockable dockable) {
        this.dockable = dockable;
    }

    private void closeCurrent() {
        if (currentItemId != null) {
            long duration = Math.max(0L, System.currentTimeMillis() - currentOpenedAtMillis);
            emit("item_close", currentItemId, resolveItem(currentItemId), duration);
        }
    }

    private IItemId resolveItemId(int viewRow) {
        try {
            if (viewRow < 0 || resultsProvider == null || resultsProvider.getResults() == null) {
                return null;
            }
            int modelRow = resultsTable == null ? viewRow : resultsTable.convertRowIndexToModel(viewRow);
            if (modelRow < 0 || modelRow >= resultsProvider.getResults().getLength()) {
                return null;
            }
            return resultsProvider.getResults().getItem(modelRow);
        } catch (RuntimeException ex) {
            return null;
        }
    }

    private IItem resolveItem(IItemId itemId) {
        try {
            if (itemId == null || resultsProvider == null) {
                return null;
            }
            IIPEDSource source = resultsProvider.getIPEDSource();
            return source == null ? null : source.getItemByID(itemId.getId());
        } catch (RuntimeException ex) {
            return null;
        }
    }

    private String mediaEventType(IItem item) {
        String mediaType = mediaType(item).toLowerCase(Locale.ROOT);
        if (mediaType.startsWith("image")) {
            return "image_view";
        }
        if (mediaType.startsWith("video")) {
            return "video_play";
        }
        return "file_open";
    }

    private String mediaType(IItem item) {
        try {
            return item == null || item.getMediaType() == null ? "unknown" : item.getMediaType().toString();
        } catch (RuntimeException ex) {
            return "unknown";
        }
    }

    private void emit(String eventType, IItemId itemId, IItem item, long durationMillis) {
        Map<String, String> event = new LinkedHashMap<>();
        event.put("schema_version", SCHEMA_VERSION);
        event.put("plugin_version", PLUGIN_VERSION);
        event.put("event_type", eventType);
        event.put("timestamp", Instant.now().toString());
        event.put("iped_version", System.getProperty("iped.version", "unknown"));
        event.put("source_id", itemId == null ? "" : Integer.toString(itemId.getSourceId()));
        event.put("item_id", itemId == null ? "" : Integer.toString(itemId.getId()));
        event.put("item_hash", itemHash(item));
        event.put("media_type", mediaType(item));
        event.put("duration_seconds", String.format(Locale.ROOT, "%.3f", durationMillis / 1000.0d));
        event.put("severity", severity(item));
        event.put("previous_hash", previousHash);
        String eventHash = sha256(json(event, false));
        event.put("event_hash", eventHash);
        previousHash = eventHash;
        write(json(event, true));
    }

    private String severity(IItem item) {
        Object value = null;
        try {
            if (item != null) {
                value = item.getExtraAttribute("supreme.severity");
            }
        } catch (RuntimeException ex) {
            value = null;
        }
        return value == null ? "" : String.valueOf(value);
    }

    private String itemHash(IItem item) {
        try {
            if (item != null && item.getHashValue() != null) {
                return sha256(String.valueOf(item.getHashValue()));
            }
        } catch (RuntimeException ex) {
            return "";
        }
        return "";
    }

    private synchronized void write(String line) {
        try {
            if (logPath.getParent() != null) {
                Files.createDirectories(logPath.getParent());
            }
            try (BufferedWriter writer = Files.newBufferedWriter(logPath, StandardCharsets.UTF_8,
                    java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND)) {
                writer.write(line);
                writer.newLine();
            }
        } catch (IOException ex) {
            if (dockable != null) {
                dockable.setTitleText("SUPREME telemetry write error");
            }
        }
    }

    private static String json(Map<String, String> values, boolean includeHash) {
        StringBuilder builder = new StringBuilder("{");
        boolean first = true;
        for (Map.Entry<String, String> entry : values.entrySet()) {
            if (!includeHash && "event_hash".equals(entry.getKey())) {
                continue;
            }
            if (!first) {
                builder.append(',');
            }
            first = false;
            builder.append('"').append(escape(entry.getKey())).append('"').append(':');
            builder.append('"').append(escape(entry.getValue())).append('"');
        }
        builder.append('}');
        return builder.toString();
    }

    private static String escape(String value) {
        if (value == null) {
            return "";
        }
        return value.replace("\\", "\\\\").replace("\"", "\\\"");
    }

    private static String sha256(String value) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(value.getBytes(StandardCharsets.UTF_8));
            StringBuilder hex = new StringBuilder();
            for (byte b : hash) {
                hex.append(String.format("%02x", b));
            }
            return hex.toString();
        } catch (Exception ex) {
            throw new IllegalStateException("SHA-256 unavailable", ex);
        }
    }
}
