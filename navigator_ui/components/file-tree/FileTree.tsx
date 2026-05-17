"use client";

import React, { useState } from "react";
import { FileTreeProps, FileNode } from "@/types";
import FileNodeComponent from "./FileNode";
import FolderNode from "./FolderNode";
import { Search } from "lucide-react";

export default function FileTree({
  files,
  selectedFile,
  onFileSelect,
}: FileTreeProps) {
  const [searchQuery, setSearchQuery] = useState("");
  // Track ALL expanded folders at the top level so nested folders work
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(
    new Set(["root"]),
  );

  const toggleFolder = (folderId: string) => {
    setExpandedFolders((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(folderId)) {
        newSet.delete(folderId);
      } else {
        newSet.add(folderId);
      }
      return newSet;
    });
  };

  // Filter files recursively based on search query
  const filterNode = (node: FileNode): FileNode | null => {
    if (!searchQuery.trim()) return node;
    const query = searchQuery.toLowerCase();

    if (node.type === "file") {
      return node.name.toLowerCase().includes(query) ? node : null;
    }

    // For folders, filter children and include folder if any children match
    const filteredChildren = (node.children || [])
      .map(filterNode)
      .filter(Boolean) as FileNode[];

    if (
      filteredChildren.length > 0 ||
      node.name.toLowerCase().includes(query)
    ) {
      return { ...node, children: filteredChildren };
    }
    return null;
  };

  const filteredFiles = files.map(filterNode).filter(Boolean) as FileNode[];

  // Pass expandedFolders and toggleFolder down so nested folders work
  const renderNode = (node: FileNode, depth: number = 0) => {
    if (node.type === "folder") {
      return (
        <FolderNode
          key={node.id}
          node={node}
          depth={depth}
          isExpanded={expandedFolders.has(node.id)}
          onToggle={() => toggleFolder(node.id)}
          selectedFile={selectedFile}
          onFileSelect={onFileSelect}
          expandedFolders={expandedFolders}
          onFolderToggle={toggleFolder}
        />
      );
    } else {
      return (
        <FileNodeComponent
          key={node.id}
          node={node}
          depth={depth}
          isSelected={selectedFile === node.id}
          onSelect={() => onFileSelect(node.id)}
        />
      );
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-[#1e293b]">
        <h2 className="text-[#f1f5f9] font-semibold text-sm mb-3 tracking-widest">
          REPOSITORY
        </h2>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[#94a3b8]" />
          <input
            type="text"
            placeholder="Search files..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-[#1e293b] text-[#f1f5f9] text-sm placeholder-[#94a3b8] pl-8 pr-3 py-1.5 rounded border border-[#334155] focus:border-[#a78bfa] focus:outline-none focus:ring-1 focus:ring-[#a78bfa] transition-colors"
          />
        </div>
      </div>

      {/* File Tree */}
      <div className="flex-1 overflow-y-auto p-2">
        {filteredFiles.length === 0 && searchQuery ? (
          <p className="text-[#94a3b8] text-xs text-center mt-8 px-4">
            No files match &quot;{searchQuery}&quot;
          </p>
        ) : (
          filteredFiles.map((node) => renderNode(node, 0))
        )}
      </div>

      {/* Legend */}
      <div className="p-4 border-t border-[#1e293b]">
        <div className="text-xs text-[#94a3b8] space-y-1.5">
          <div className="font-semibold mb-2 tracking-widest">
            COMPLEXITY LEGEND
          </div>
          <div className="flex items-center gap-2">
            <span className="w-5 h-5 bg-[#34d399] rounded flex items-center justify-center text-[10px] font-bold text-black flex-shrink-0">
              I
            </span>
            <span>High Overlap</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-5 h-5 bg-[#fbbf24] rounded flex items-center justify-center text-[10px] font-bold text-black flex-shrink-0">
              II
            </span>
            <span>Mid Decoupled</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-5 h-5 bg-[#ef4444] rounded flex items-center justify-center text-[10px] font-bold text-white flex-shrink-0">
              III
            </span>
            <span>Learned Context</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// Made with Bob
