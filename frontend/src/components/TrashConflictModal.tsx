import React, { useState } from "react";
import { Modal } from "@/components/ui";
import { apiPost } from "@/lib/api";

export interface TrashConflictInfo {
  in_trash?: boolean;
  trash_id: string;
  entity_type: string;
  name?: string | null;
  code?: string | null;
  custom_action_label?: string;
}

export interface TrashConflictModalProps {
  isOpen: boolean;
  conflictInfo: TrashConflictInfo | null;
  onClose: () => void;
  onRestored?: (trashId: string, entityType: string) => Promise<void> | void;
  customRestoreHandler?: (trashId: string, entityType: string) => Promise<void> | void;
}

export const TrashConflictModal: React.FC<TrashConflictModalProps> = ({
  isOpen,
  conflictInfo,
  onClose,
  onRestored,
  customRestoreHandler,
}) => {
  const [restoring, setRestoring] = useState(false);
  const [restoreError, setRestoreError] = useState<string | null>(null);

  if (!isOpen || !conflictInfo) return null;

  const handleRestore = async () => {
    setRestoring(true);
    setRestoreError(null);
    try {
      if (customRestoreHandler) {
        await customRestoreHandler(conflictInfo.trash_id, conflictInfo.entity_type);
      } else {
        await apiPost("/trash/restore", {
          items: [{ entity_type: conflictInfo.entity_type, id: conflictInfo.trash_id }],
        });
      }
      if (onRestored) {
        await onRestored(conflictInfo.trash_id, conflictInfo.entity_type);
      }
      onClose();
    } catch (err: any) {
      setRestoreError(err?.message || "Failed to restore record from trash. Please try again.");
    } finally {
      setRestoring(false);
    }
  };

  const handleOpenTrash = () => {
    window.open("/trash", "_blank", "noopener,noreferrer");
  };

  const displayName = conflictInfo.name || conflictInfo.code || "Item";
  const entityLabel = conflictInfo.entity_type || "Record";

  return (
    <Modal
      open={isOpen}
      variant="center"
      title={
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <span
            style={{
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              width: "32px",
              height: "32px",
              borderRadius: "8px",
              background: "#fef3c7",
              color: "#d97706",
              fontSize: "18px",
            }}
          >
            🗑️
          </span>
          <span style={{ fontSize: "17px", fontWeight: 700, color: "#1e293b" }}>
            {entityLabel} Already Exists in Trash
          </span>
        </div>
      }
      onClose={onClose}
      locked={restoring}
      cardStyle={{ maxWidth: "520px", width: "100%", borderRadius: "14px", overflow: "hidden" }}
    >
      <div style={{ padding: "20px 24px" }}>
        {restoreError && (
          <div
            style={{
              marginBottom: "16px",
              padding: "12px 14px",
              background: "#fee2e2",
              border: "1px solid #f87171",
              borderRadius: "8px",
              color: "#991b1b",
              fontSize: "13.5px",
            }}
          >
            {restoreError}
          </div>
        )}

        <div
          style={{
            background: "#fffbeb",
            border: "1px solid #fde68a",
            borderRadius: "10px",
            padding: "14px 16px",
            marginBottom: "18px",
            color: "#92400e",
            fontSize: "13.5px",
            lineHeight: "1.5",
          }}
        >
          A {entityLabel.toLowerCase()} with this name or code was previously deleted and is currently stored in the{" "}
          <strong>Trash bin</strong>.
        </div>

        <div
          style={{
            background: "#f8fafc",
            border: "1px solid #e2e8f0",
            borderRadius: "10px",
            padding: "14px 16px",
            marginBottom: "20px",
          }}
        >
          <div style={{ display: "grid", gridTemplateColumns: "100px 1fr", gap: "8px", fontSize: "13.5px" }}>
            <span style={{ color: "#64748b", fontWeight: 600 }}>Entity:</span>
            <span style={{ color: "#0f172a", fontWeight: 600 }}>{entityLabel}</span>

            {conflictInfo.name && (
              <>
                <span style={{ color: "#64748b", fontWeight: 600 }}>Name:</span>
                <span style={{ color: "#0f172a", fontWeight: 700 }}>{conflictInfo.name}</span>
              </>
            )}

            {conflictInfo.code && (
              <>
                <span style={{ color: "#64748b", fontWeight: 600 }}>Code:</span>
                <span
                  style={{
                    color: "#0284c7",
                    fontFamily: "monospace",
                    fontWeight: 700,
                    background: "#e0f2fe",
                    padding: "1px 6px",
                    borderRadius: "4px",
                    display: "inline-block",
                    width: "fit-content",
                  }}
                >
                  {conflictInfo.code}
                </span>
              </>
            )}
          </div>
        </div>

        <p style={{ fontSize: "13.5px", color: "#475569", lineHeight: "1.5", margin: "0 0 24px 0" }}>
          Would you like to <strong>restore</strong> this {entityLabel.toLowerCase()} directly back to your active
          records, or <strong>close</strong> this window to change the name/code?
        </p>

        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: "12px",
            flexWrap: "wrap",
            borderTop: "1px solid #e2e8f0",
            paddingTop: "16px",
          }}
        >
          <div style={{ display: "flex", gap: "8px" }}>
            <button
              type="button"
              onClick={onClose}
              disabled={restoring}
              style={{
                padding: "8px 14px",
                borderRadius: "8px",
                border: "1px solid #cbd5e1",
                background: "#ffffff",
                color: "#475569",
                fontSize: "13.5px",
                fontWeight: 600,
                cursor: restoring ? "not-allowed" : "pointer",
              }}
            >
              Change Name / Cancel
            </button>

            <button
              type="button"
              onClick={handleOpenTrash}
              disabled={restoring}
              title="Open the Trash management page in a new tab"
              style={{
                padding: "8px 12px",
                borderRadius: "8px",
                border: "1px solid #e2e8f0",
                background: "#f1f5f9",
                color: "#64748b",
                fontSize: "13px",
                fontWeight: 500,
                cursor: "pointer",
                display: "inline-flex",
                alignItems: "center",
                gap: "4px",
              }}
            >
              Open Trash ↗
            </button>
          </div>

          <button
            type="button"
            onClick={handleRestore}
            disabled={restoring}
            style={{
              padding: "9px 18px",
              borderRadius: "8px",
              border: "none",
              background: restoring ? "#94a3b8" : "linear-gradient(135deg, #059669 0%, #047857 100%)",
              color: "#ffffff",
              fontSize: "13.5px",
              fontWeight: 700,
              cursor: restoring ? "not-allowed" : "pointer",
              display: "inline-flex",
              alignItems: "center",
              gap: "6px",
              boxShadow: "0 2px 4px rgba(5, 150, 105, 0.25)",
            }}
          >
            <span>{restoring ? "⏳" : "🔄"}</span>
            <span>
              {restoring
                ? "Restoring..."
                : conflictInfo.custom_action_label || `Restore ${displayName} from Trash`}
            </span>
          </button>
        </div>
      </div>
    </Modal>
  );
};
