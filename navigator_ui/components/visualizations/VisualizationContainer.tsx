"use client";

import React from "react";
import { VisualizationContainerProps } from "@/types";

export default function VisualizationContainer({
  currentView,
  children,
}: VisualizationContainerProps & { children: React.ReactNode }) {
  return (
    <div
      style={{
        height: "100%",
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
      }}
    >
      <div style={{ flex: 1, position: "relative", overflow: "hidden" }}>
        {children}
      </div>
    </div>
  );
}

// Made with Bob
