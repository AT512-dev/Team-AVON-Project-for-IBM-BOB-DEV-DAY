"use client";

import React, { useState } from "react";

const ALL_MODULES = [
  { id: "auth", label: "AUTH" },
  { id: "api", label: "API" },
  { id: "database", label: "DATABASE" },
  { id: "ui", label: "UI" },
  { id: "payments", label: "PAYMENTS" },
  { id: "analytics", label: "ANALYTICS" },
];

interface Props {
  selectedModule: string | null;
  onModuleChange: (moduleId: string | null) => void;
}

export default function ModuleDropdown({
  selectedModule,
  onModuleChange,
}: Props) {
  const [open, setOpen] = useState(false);

  const label = selectedModule
    ? (ALL_MODULES.find((m) => m.id === selectedModule)?.label ?? "All modules")
    : "All modules";

  const select = (id: string | null) => {
    onModuleChange(id);
    setOpen(false);
  };

  return (
    <div style={{ position: "relative" }}>
      <button
        onClick={() => setOpen((v) => !v)}
        style={{
          display: "flex",
          alignItems: "center",
          gap: 8,
          background: "rgba(255,255,255,0.07)",
          border: "1px solid rgba(255,255,255,0.14)",
          borderRadius: 9,
          padding: "7px 14px",
          color: "rgba(255,255,255,0.85)",
          fontSize: 13,
          fontWeight: selectedModule ? 600 : 400,
          cursor: "pointer",
          fontFamily: "inherit",
        }}
      >
        {label}
        <svg
          width="11"
          height="11"
          viewBox="0 0 24 24"
          fill="none"
          style={{
            transform: open ? "rotate(180deg)" : "rotate(0deg)",
            transition: "transform 0.2s",
          }}
        >
          <path
            d="M6 9l6 6 6-6"
            stroke="rgba(255,255,255,0.5)"
            strokeWidth="2"
            strokeLinecap="round"
          />
        </svg>
      </button>

      {open && (
        <div
          style={{
            position: "absolute",
            top: "calc(100% + 6px)",
            left: 0,
            background: "#1a2234",
            border: "1px solid rgba(255,255,255,0.1)",
            borderRadius: 10,
            overflow: "hidden",
            zIndex: 50,
            minWidth: 160,
            boxShadow: "0 8px 32px rgba(0,0,0,0.5)",
          }}
          onMouseDown={(e) => e.stopPropagation()}
        >
          {/* All modules — always at top */}
          <button
            onClick={() => select(null)}
            style={{
              width: "100%",
              display: "block",
              padding: "9px 16px 8px",
              background: "transparent",
              border: "none",
              borderBottom: "1px solid rgba(255,255,255,0.07)",
              color:
                selectedModule === null ? "#06b6d4" : "rgba(255,255,255,0.4)",
              fontSize: 11,
              fontWeight: selectedModule === null ? 600 : 400,
              cursor: "pointer",
              textAlign: "left",
              fontFamily: "inherit",
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLButtonElement).style.background =
                "rgba(255,255,255,0.05)";
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLButtonElement).style.background =
                "transparent";
            }}
          >
            {selectedModule === null && (
              <span style={{ color: "#06b6d4", marginRight: 6 }}>✓</span>
            )}
            All modules
          </button>

          {/* Individual modules */}
          {ALL_MODULES.map((m) => (
            <button
              key={m.id}
              onClick={() => select(m.id)}
              style={{
                width: "100%",
                display: "block",
                padding: "8px 16px",
                background: "transparent",
                border: "none",
                color:
                  selectedModule === m.id ? "#06b6d4" : "rgba(255,255,255,0.7)",
                fontSize: 12,
                fontWeight: selectedModule === m.id ? 600 : 400,
                cursor: "pointer",
                textAlign: "left",
                fontFamily: "inherit",
                letterSpacing: "0.04em",
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLButtonElement).style.background =
                  "rgba(255,255,255,0.05)";
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLButtonElement).style.background =
                  "transparent";
              }}
            >
              {selectedModule === m.id && (
                <span style={{ color: "#06b6d4", marginRight: 6 }}>✓</span>
              )}
              {m.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
