"use client";

import React from "react";
import { FileNode } from "@/types";
import { FileText, FileCode } from "lucide-react";

interface FileNodeProps {
  node: FileNode;
  depth: number;
  isSelected: boolean;
  onSelect: () => void;
}

export default function FileNodeComponent({
  node,
  depth,
  isSelected,
  onSelect,
}: FileNodeProps) {
  const getFileIcon = () => {
    if (node.extension === "js" || node.extension === "ts") {
      return <FileCode className="w-4 h-4 text-[#fbbf24]" />;
    }
    return <FileText className="w-4 h-4 text-[#94a3b8]" />;
  };

  const getBadgeColor = () => {
    switch (node.badge) {
      case "I":
        return "bg-[#34d399] text-black";
      case "II":
        return "bg-[#fbbf24] text-black";
      case "III":
        return "bg-[#ef4444] text-white";
      default:
        return "";
    }
  };

  return (
    <div
      onClick={onSelect}
      style={{ paddingLeft: `${depth * 16 + 8}px` }}
      className={`
        flex items-center gap-2 py-1.5 px-2 rounded cursor-pointer
        transition-colors duration-150
        ${
          isSelected
            ? "bg-[#a78bfa]/20 text-[#f1f5f9]"
            : "text-[#94a3b8] hover:bg-[#1e293b] hover:text-[#f1f5f9]"
        }
      `}
    >
      {getFileIcon()}
      <span className="text-sm flex-1 truncate">{node.name}</span>
      {node.badge && (
        <span
          className={`
          w-4 h-4 rounded flex items-center justify-center 
          text-[10px] font-bold ${getBadgeColor()}
        `}
        >
          {node.badge}
        </span>
      )}
    </div>
  );
}

// Made with Bob
