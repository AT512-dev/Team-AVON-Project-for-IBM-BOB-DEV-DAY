"use client";

import React from "react";
import { FileNode } from "@/types";
import { ChevronRight, ChevronDown, Folder, FolderOpen } from "lucide-react";
import FileNodeComponent from "./FileNode";

interface FolderNodeProps {
  node: FileNode;
  depth: number;
  isExpanded: boolean;
  onToggle: () => void;
  selectedFile: string | null;
  onFileSelect: (fileId: string) => void;
  // These two props bubble up from FileTree so nested folders work properly
  expandedFolders: Set<string>;
  onFolderToggle: (folderId: string) => void;
}

export default function FolderNode({
  node,
  depth,
  isExpanded,
  onToggle,
  selectedFile,
  onFileSelect,
  expandedFolders,
  onFolderToggle,
}: FolderNodeProps) {
  const renderChildren = () => {
    if (!isExpanded || !node.children) return null;

    return (
      <div>
        {node.children.map((child) => {
          if (child.type === "folder") {
            // Now nested folders get the REAL expanded state and toggle handler
            return (
              <FolderNode
                key={child.id}
                node={child}
                depth={depth + 1}
                isExpanded={expandedFolders.has(child.id)}
                onToggle={() => onFolderToggle(child.id)}
                selectedFile={selectedFile}
                onFileSelect={onFileSelect}
                expandedFolders={expandedFolders}
                onFolderToggle={onFolderToggle}
              />
            );
          } else {
            return (
              <FileNodeComponent
                key={child.id}
                node={child}
                depth={depth + 1}
                isSelected={selectedFile === child.id}
                onSelect={() => onFileSelect(child.id)}
              />
            );
          }
        })}
      </div>
    );
  };

  return (
    <div>
      <div
        onClick={onToggle}
        style={{ paddingLeft: `${depth * 16 + 8}px` }}
        className="
          flex items-center gap-2 py-1.5 px-2 rounded cursor-pointer
          text-[#f1f5f9] hover:bg-[#1e293b]
          transition-colors duration-150 group
        "
      >
        {isExpanded ? (
          <ChevronDown className="w-3.5 h-3.5 text-[#94a3b8] flex-shrink-0" />
        ) : (
          <ChevronRight className="w-3.5 h-3.5 text-[#94a3b8] flex-shrink-0" />
        )}
        {isExpanded ? (
          <FolderOpen className="w-4 h-4 text-[#a78bfa] flex-shrink-0" />
        ) : (
          <Folder className="w-4 h-4 text-[#a78bfa] flex-shrink-0" />
        )}
        <span className="text-sm font-medium truncate">{node.name}</span>
        {node.children && (
          <span className="ml-auto text-[10px] text-[#94a3b8] opacity-0 group-hover:opacity-100 transition-opacity pr-1">
            {node.children.length}
          </span>
        )}
      </div>
      {renderChildren()}
    </div>
  );
}

// Made with Bob
