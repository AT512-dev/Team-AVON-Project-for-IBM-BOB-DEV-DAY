"use client";

import React from "react";

interface RightPanelProps {
  children: React.ReactNode;
}

export default function RightPanel({ children }: RightPanelProps) {
  return (
    <div
      style={{
        width: 300,
        minWidth: 300,
        maxWidth: 300,
        height: "100%",
        background: "#0d1117",
        borderLeft: "1px solid rgba(255,255,255,0.06)",
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
        flexShrink: 0,
      }}
    >
      {children}
    </div>
  );
}

// Made with Bob
