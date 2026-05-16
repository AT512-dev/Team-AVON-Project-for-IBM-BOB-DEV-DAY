"use client";

import React from "react";

interface CenterPanelProps {
  children: React.ReactNode;
}

export default function CenterPanel({ children }: CenterPanelProps) {
  return (
    <div className="flex-1 bg-[#0a0e1a] overflow-hidden relative">
      {children}
    </div>
  );
}

// Made with Bob
