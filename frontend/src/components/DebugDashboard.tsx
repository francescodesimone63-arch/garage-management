/**
 * Debug Dashboard - Minimale ma funzionante
 * Mostra errori tracciati in tempo reale
 */

import React, { useState, useEffect } from "react";
import { Button, Drawer, Tag, Space, List, Empty, Tooltip, Button as AntButton } from "antd";
import { BugOutlined, DownloadOutlined, DeleteOutlined } from "@ant-design/icons";
import { errorTracker, ErrorLog } from "@/utils/errorTracker";

interface DebugDashboardProps {
  onClose?: () => void;
}

export const DebugDashboard: React.FC<DebugDashboardProps> = ({ onClose }) => {
  const [visible, setVisible] = useState(false);
  const [logs, setLogs] = useState<ErrorLog[]>([]);

  useEffect(() => {
    errorTracker.subscribe(setLogs);

    // Hotkey per aprire il dashboard (Ctrl+Shift+D)
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.shiftKey && e.code === "KeyD") {
        e.preventDefault();
        setVisible((prev) => !prev);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
      errorTracker.unsubscribe(setLogs);
    };
  }, []);

  const severityColor: Record<string, string> = {
    low: "orange",
    medium: "orange",
    high: "red",
    critical: "red",
  };

  const handleClose = () => {
    setVisible(false);
    onClose?.();
  };

  return (
    <>
      <Drawer
        title={
          <span>
            🐛 Debug Dashboard ({logs.length} errors) - Ctrl+Shift+D
          </span>
        }
        placement="right"
        onClose={handleClose}
        open={visible}
        width={600}
      >
        <Space direction="vertical" style={{ width: "100%", marginBottom: "20px" }}>
          <Space>
            <Button
              icon={<DownloadOutlined />}
              onClick={() => errorTracker.downloadLogs()}
            >
              Scarica JSON
            </Button>

            <Button
              icon={<DeleteOutlined />}
              danger
              onClick={() => {
                errorTracker.clearLogs();
              }}
            >
              Cancella tutti
            </Button>

            <Tag color="blue">Total Errors: {logs.length}</Tag>
            <Tag color="red">Critical: {logs.filter((l) => l.severity === "critical").length}</Tag>
            <Tag color="orange">High: {logs.filter((l) => l.severity === "high").length}</Tag>
          </Space>
        </Space>

        {logs.length === 0 ? (
          <Empty description="Nessun errore" />
        ) : (
          <List
            dataSource={logs.slice().reverse()}
            renderItem={(log) => (
              <div
                style={{
                  padding: "12px",
                  marginBottom: "8px",
                  border: `1px solid ${
                    { low: "#FFA500", medium: "#FF8C00", high: "#FF0000", critical: "#8B0000" }[
                      log.severity
                    ]
                  }`,
                  borderRadius: "4px",
                  backgroundColor:
                    { low: "#FFF7E6", medium: "#FFF1F0", high: "#FFF1F0", critical: "#FFF1F0" }[
                      log.severity
                    ],
                }}
              >
                <div style={{ marginBottom: "8px" }}>
                  <Tag color={severityColor[log.severity]}>
                    {log.severity.toUpperCase()}
                  </Tag>
                  <Tag color="blue">{log.type}</Tag>
                  <span style={{ fontSize: "10px", color: "#999", marginLeft: "8px" }}>
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </span>
                </div>

                <div style={{ fontFamily: "monospace", fontSize: "12px", marginBottom: "8px" }}>
                  <strong>{log.message}</strong>
                </div>

                <details
                  style={{ fontSize: "11px", color: "#666", cursor: "pointer" }}
                >
                  <summary>Dettagli</summary>
                  <pre
                    style={{
                      backgroundColor: "#f5f5f5",
                      padding: "8px",
                      marginTop: "8px",
                      fontSize: "10px",
                      overflow: "auto",
                      maxHeight: "200px",
                    }}
                  >
                    {JSON.stringify(log.details, null, 2)}
                  </pre>
                  {log.stackTrace && (
                    <details style={{ marginTop: "8px" }}>
                      <summary>Stack Trace</summary>
                      <pre
                        style={{
                          backgroundColor: "#1f1f1f",
                          color: "#00ff00",
                          padding: "8px",
                          marginTop: "8px",
                          fontSize: "9px",
                          overflow: "auto",
                          maxHeight: "150px",
                        }}
                      >
                        {log.stackTrace}
                      </pre>
                    </details>
                  )}
                </details>
              </div>
            )}
          />
        )}
      </Drawer>

      {/* Trigger button */}
      <Tooltip title="Debug Dashboard (Ctrl+Shift+D)">
        <Button
          type="primary"
          danger
          shape="circle"
          size="large"
          icon={<BugOutlined />}
          onClick={() => setVisible(true)}
          style={{
            position: "fixed",
            bottom: "20px",
            right: "20px",
            zIndex: 9999,
            fontSize: "18px",
          }}
        />
      </Tooltip>
    </>
  );
};

export default DebugDashboard;
