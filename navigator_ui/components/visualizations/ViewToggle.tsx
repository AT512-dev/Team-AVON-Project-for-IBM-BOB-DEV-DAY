"use client";

import React from "react";
import { ViewType } from "@/types";

interface ViewToggleProps {
  currentView: ViewType;
  onViewChange: (view: ViewType) => void;
}

export default function ViewToggle({
  currentView,
  onViewChange,
}: ViewToggleProps) {
  return (
    <div className="flex gap-2">
      <button
        onClick={() => onViewChange("constellation")}
        className={`
          px-4 py-2 rounded-lg font-medium text-sm transition-all duration-200
          ${
            currentView === "constellation"
              ? "bg-[#a78bfa] text-white shadow-lg shadow-[#a78bfa]/30"
              : "bg-[#1e293b] text-[#94a3b8] hover:bg-[#334155] hover:text-[#f1f5f9] border border-[#334155]"
          }
        `}
      >
        Constellation
      </button>
      <button
        onClick={() => onViewChange("levelMap")}
        className={`
          px-4 py-2 rounded-lg font-medium text-sm transition-all duration-200
          ${
            currentView === "levelMap"
              ? "bg-[#a78bfa] text-white shadow-lg shadow-[#a78bfa]/30"
              : "bg-[#1e293b] text-[#94a3b8] hover:bg-[#334155] hover:text-[#f1f5f9] border border-[#334155]"
          }
        `}
      >
        Level Map
      </button>
    </div>
  );
}

// Made with Bob
