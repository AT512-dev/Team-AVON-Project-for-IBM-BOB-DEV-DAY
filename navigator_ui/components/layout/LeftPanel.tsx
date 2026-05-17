"use client";

import React from "react";

interface LeftPanelProps {
  children: React.ReactNode;
}

export default function LeftPanel({ children }: LeftPanelProps) {
  return (
    <div className="w-[20%] min-w-[250px] bg-[#0f1419] border-r border-[#1e293b] overflow-y-auto">
      {children}
    </div>
  );
}

// Made with Bob
