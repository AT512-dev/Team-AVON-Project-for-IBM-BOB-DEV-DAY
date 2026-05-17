"use client";

import React from "react";

export default function ConstellationLegend() {
  return (
    <div
      style={{
        position: "absolute",
        bottom: 20,
        left: 20,
        zIndex: 10,
        background: "rgba(13,17,23,0.9)",
        border: "1px solid rgba(255,255,255,0.08)",
        borderRadius: 10,
        padding: "14px 16px",
        backdropFilter: "blur(10px)",
        minWidth: 200,
      }}
    >
      {/* Title */}
      <div
        style={{
          fontSize: 11,
          fontWeight: 700,
          color: "rgba(255,255,255,0.5)",
          marginBottom: 12,
          letterSpacing: "0.05em",
          textTransform: "uppercase",
        }}
      >
        Key
      </div>

      {/* Legend items */}
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {/* Star = file */}
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div
            style={{
              width: 20,
              height: 20,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 14,
            }}
          >
            ⭐
          </div>
          <span style={{ fontSize: 12, color: "rgba(255,255,255,0.7)" }}>
            Star = a file
          </span>
        </div>

        {/* Size = dependency weight */}
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
            <div
              style={{
                width: 8,
                height: 8,
                borderRadius: "50%",
                background: "#64748b",
              }}
            />
            <span style={{ fontSize: 10, color: "rgba(255,255,255,0.3)" }}>
              →
            </span>
            <div
              style={{
                width: 14,
                height: 14,
                borderRadius: "50%",
                background: "#64748b",
              }}
            />
          </div>
          <span style={{ fontSize: 12, color: "rgba(255,255,255,0.7)" }}>
            Size = dependency weight
          </span>
        </div>

        {/* Current location */}
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div
            style={{
              width: 20,
              height: 20,
              borderRadius: "50%",
              background: "rgba(6,182,212,0.15)",
              border: "2px solid #06b6d4",
              boxShadow: "0 0 12px rgba(6,182,212,0.5)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <div
              style={{
                width: 8,
                height: 8,
                borderRadius: "50%",
                background: "#06b6d4",
              }}
            />
          </div>
          <span style={{ fontSize: 12, color: "rgba(255,255,255,0.7)" }}>
            Where you are now
          </span>
        </div>

        {/* Divider */}
        <div
          style={{
            height: 1,
            background: "rgba(255,255,255,0.06)",
            margin: "4px 0",
          }}
        />

        {/* Complexity legend */}
        <div
          style={{
            fontSize: 10,
            color: "rgba(255,255,255,0.4)",
            marginBottom: 4,
          }}
        >
          COMPLEXITY LEGEND
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div
            style={{
              width: 12,
              height: 12,
              borderRadius: 3,
              background: "#ef4444",
            }}
          />
          <span style={{ fontSize: 11, color: "rgba(255,255,255,0.6)" }}>
            High Overlap
          </span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div
            style={{
              width: 12,
              height: 12,
              borderRadius: 3,
              background: "#f59e0b",
            }}
          />
          <span style={{ fontSize: 11, color: "rgba(255,255,255,0.6)" }}>
            Mid Decoupled
          </span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div
            style={{
              width: 12,
              height: 12,
              borderRadius: 3,
              background: "#10b981",
            }}
          />
          <span style={{ fontSize: 11, color: "rgba(255,255,255,0.6)" }}>
            Learned Context
          </span>
        </div>
      </div>
    </div>
  );
}

// Made with Bob
