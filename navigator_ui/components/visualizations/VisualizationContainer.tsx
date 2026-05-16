"use client";

import React from "react";
import { VisualizationContainerProps } from "@/types";

export default function VisualizationContainer({
  currentView,
  onViewChange,
  stats,
  selectedModule,
  children,
}: VisualizationContainerProps & { children: React.ReactNode }) {
  // Pass the toggle state down via a wrapper — the constellation handles its own UI
  // This container is now a clean pass-through with just the stats bar when in level map
  const showStatsBar = currentView === "levelMap";

  return (
    <div style={{ height: "100%", display: "flex", flexDirection: "column", overflow: "hidden" }}>
      {/* Stats bar — only show on level map since constellation has its own top bar */}
      {showStatsBar && (
        <div style={{
          padding: "10px 16px",
          borderBottom: "1px solid rgba(255,255,255,0.06)",
          display: "flex", alignItems: "center", justifyContent: "space-between",
          flexShrink: 0,
          background: "#0d1117",
        }}>
          {/* Toggle */}
          <div style={{
            display: "flex", alignItems: "center",
            background: "rgba(255,255,255,0.04)",
            border: "1px solid rgba(255,255,255,0.08)",
            borderRadius: 9, padding: 3, gap: 2,
          }}>
            {[
              { view: "constellation", label: "Constellation" },
              { view: "levelMap",      label: "Level Map" },
            ].map(({ view, label }) => (
              <button
                key={view}
                onClick={() => onViewChange(view as "constellation" | "levelMap")}
                style={{
                  padding: "5px 14px", borderRadius: 7,
                  background: currentView === view ? "rgba(6,182,212,0.15)" : "transparent",
                  border: currentView === view ? "1px solid rgba(6,182,212,0.3)" : "1px solid transparent",
                  color: currentView === view ? "#06b6d4" : "rgba(255,255,255,0.4)",
                  fontSize: 12, fontWeight: currentView === view ? 600 : 400,
                  cursor: "pointer", transition: "all 0.15s", fontFamily: "inherit",
                }}
              >
                {label}
              </button>
            ))}
          </div>

          {/* Stats */}
          <div style={{ display: "flex", alignItems: "center", gap: 16, fontSize: 12 }}>
            <span style={{ color: "rgba(255,255,255,0.35)" }}>
              {stats.filesFound} files found
            </span>
            <div style={{ width: 1, height: 12, background: "rgba(255,255,255,0.1)" }} />
            <span style={{ color: "#f59e0b" }}>{stats.criticalPaths} critical paths</span>
            <div style={{ width: 1, height: 12, background: "rgba(255,255,255,0.1)" }} />
            <span style={{ color: "#10b981" }}>{stats.completionPercentage}% complete</span>
          </div>
        </div>
      )}

      {/* Main view */}
      <div style={{ flex: 1, position: "relative", overflow: "hidden" }}>
        {children}
      </div>
    </div>
  );
}

// Made with Bob
