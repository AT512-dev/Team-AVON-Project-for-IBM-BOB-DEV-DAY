"use client";

import React, { useState, useMemo } from "react";

export interface Module {
  id: string;
  name: string;
  fileCount: number;
  color: string;
  iconLetter: string;
}

// Represents a node in our repository structure tree
interface FileTreeNode {
  name: string;
  path: string;
  isFolder: boolean;
  children: Record<string, FileTreeNode>;
}

interface LeftPanelModulesProps {
  modules?: Module[]; 
  selectedModule: string | null; // Acts as the selected file or directory path string
  onModuleSelect: (moduleId: string | null) => void;
  totalFiles?: number;
  completedFiles?: number;
  userName?: string;
  userInitials?: string;
  userRole?: string;
  userDays?: number;
  // Using structural typing with an intersection type here resolves the index signature error
  repoFiles?: Array<{ path: string } & Record<string, unknown>>;
}

// ── Icons ──────────────────────────────────────────────────────────────────
const FolderIcon = ({ isOpen }: { isOpen: boolean }) => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0 }}>
    <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
  </svg>
);

const FileIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.45)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0 }}>
    <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z" />
    <polyline points="13 2 13 9 20 9" />
  </svg>
);

// ── Recursive Node Component ───────────────────────────────────────────────
interface FileRowProps {
  node: FileTreeNode;
  depth: number;
  searchQuery: string;
  selectedPath: string | null;
  onSelect: (path: string | null) => void;
}

function FileTreeRow({ node, depth, searchQuery, selectedPath, onSelect }: FileRowProps) {
  const [isOpen, setIsOpen] = useState(true);

  // Filter and sort children: Folders always surface to top, then alphabetical files
  const childNodes = useMemo(() => {
    return Object.values(node.children).sort((a, b) => {
      if (a.isFolder && !b.isFolder) return -1;
      if (!a.isFolder && b.isFolder) return 1;
      return a.name.localeCompare(b.name);
    });
  }, [node.children]);

  // Determine filtering matrix for sub-item and title visibility matching search
  const matchesSearch = node.name.toLowerCase().includes(searchQuery.toLowerCase());
  const hasMatchingChildren = childNodes.some(child => 
    child.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
    Object.keys(child.children).some(k => k.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  if (searchQuery && !matchesSearch && !hasMatchingChildren) {
    return null;
  }

  const isSelected = selectedPath === node.path;

  const handleRowClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (node.isFolder) {
      setIsOpen(!isOpen);
    } else {
      onSelect(isSelected ? null : node.path);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column" }}>
      {/* Node Button Item */}
      {node.path !== "root" && (
        <button
          onClick={handleRowClick}
          style={{
            width: "100%",
            display: "flex",
            alignItems: "center",
            gap: 8,
            padding: `6px 10px 6px ${depth * 12}px`,
            background: isSelected ? "rgba(6,182,212,0.12)" : "transparent",
            border: "none",
            borderRadius: 6,
            cursor: "pointer",
            textAlign: "left",
            transition: "background 0.1s",
          }}
          onMouseEnter={e => { if(!isSelected) e.currentTarget.style.background = "rgba(255,255,255,0.03)"; }}
          onMouseLeave={e => { if(!isSelected) e.currentTarget.style.background = "transparent"; }}
        >
          {node.isFolder ? <FolderIcon isOpen={isOpen} /> : <FileIcon />}
          <span style={{
            fontSize: 13,
            fontWeight: isSelected ? 600 : 400,
            color: isSelected ? "#06b6d4" : node.isFolder ? "rgba(255,255,255,0.8)" : "rgba(255,255,255,0.6)",
            whiteSpace: "nowrap",
            overflow: "hidden",
            textOverflow: "ellipsis",
            flex: 1
          }}>
            {node.name}
          </span>
          {node.isFolder && (
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.3)" strokeWidth="2.5" 
                 style={{ transform: isOpen ? "rotate(180deg)" : "rotate(0deg)", transition: "transform 0.1s", marginLeft: "auto" }}>
              <path d="M6 9l6 6 6-6" />
            </svg>
          )}
        </button>
      )}

      {/* Render Sub Tree Nodes Nested Layers */}
      {(isOpen || node.path === "root") && childNodes.length > 0 && (
        <div style={{ display: "flex", flexDirection: "column" }}>
          {childNodes.map(child => (
            <FileTreeRow
              key={child.path}
              node={child}
              depth={node.path === "root" ? 1 : depth + 1}
              searchQuery={searchQuery}
              selectedPath={selectedPath}
              onSelect={onSelect}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// ── Main Left Panel Component ──────────────────────────────────────────────
export default function LeftPanelModules({
  selectedModule,
  onModuleSelect,
  totalFiles = 0,
  completedFiles = 0,
  userName = "Developer",
  userInitials = "DV",
  userRole = "Engineer",
  userDays = 1,
  repoFiles = []
}: LeftPanelModulesProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [listOpen, setListOpen] = useState(true);

  // Build the hierarchical tree from the flat repoFiles payload array
  const fileTreeRoot = useMemo(() => {
    const root: FileTreeNode = { name: "Root", path: "root", isFolder: true, children: {} };
    
    repoFiles.forEach(file => {
      const parts = file.path.split("/");
      let current = root;
      let currentPath = "";

      parts.forEach((part, index) => {
        currentPath = currentPath ? `${currentPath}/${part}` : part;
        const isLast = index === parts.length - 1;

        if (!current.children[part]) {
          current.children[part] = {
            name: part,
            path: currentPath,
            isFolder: !isLast,
            children: {}
          };
        }
        current = current.children[part];
      });
    });

    return root;
  }, [repoFiles]);

  return (
    <div style={{
      width: 250, minWidth: 250, maxWidth: 250, height: "100%",
      background: "#0d1117", borderRight: "1px solid rgba(255,255,255,0.06)",
      display: "flex", flexDirection: "column", flexShrink: 0, overflow: "hidden",
    }}>

      {/* Logo Container */}
      <div style={{ padding: "22px 18px 16px" }}>
        <span style={{ fontSize: 22, fontWeight: 800, color: "#ffffff", letterSpacing: "-0.4px" }}>
          Compass AI
        </span>
      </div>

      {/* Repository Filter Input Stream Bar */}
      <div style={{ padding: "0 12px 12px" }}>
        <div style={{ display: "flex", alignItems: "center", height: 38, background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.09)", borderRadius: 9, padding: "0 10px", gap: 8 }}>
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" style={{ flexShrink: 0 }}>
            <circle cx="11" cy="11" r="8" stroke="rgba(255,255,255,0.22)" strokeWidth="2" />
            <path d="M21 21l-4.35-4.35" stroke="rgba(255,255,255,0.22)" strokeWidth="2" strokeLinecap="round" />
          </svg>
          <input type="text" placeholder="Filter files..."
            value={searchQuery} onChange={e => setSearchQuery(e.target.value)}
            style={{ flex: 1, minWidth: 0, background: "transparent", border: "none", outline: "none", color: "rgba(255,255,255,0.55)", fontSize: 12, fontFamily: "inherit" }}
          />
        </div>
      </div>

      {/* Directory Title Section Header */}
      <div style={{ padding: "0 12px 10px" }}>
        <button onClick={() => setListOpen(!listOpen)} style={{
          width: "100%", display: "flex", alignItems: "center", justifyContent: "space-between",
          padding: "9px 14px",
          background: "rgba(6,182,212,0.07)",
          border: "1px solid rgba(6,182,212,0.2)",
          borderRadius: 9, cursor: "pointer", transition: "all 0.15s",
        }}>
          <span style={{ fontSize: 13, fontWeight: 600, color: "#06b6d4" }}>Repository Workspace</span>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
            style={{ color: "#06b6d4", transform: listOpen ? "rotate(180deg)" : "rotate(0deg)", transition: "transform 0.2s", flexShrink: 0 }}>
            <path d="M6 9l6 6 6-6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </button>
      </div>

      {/* File Tree System Canvas Scroll Shell */}
      {listOpen && (
        <div style={{ flex: 1, overflowY: "auto", padding: "2px 12px", scrollbarWidth: "none" }}>
          {repoFiles.length === 0 ? (
            <div style={{ fontSize: 12, color: "rgba(255,255,255,0.2)", textAlign: "center", padding: "20px 0" }}>
              Empty Workspace Tree
            </div>
          ) : (
            <FileTreeRow
              node={fileTreeRoot}
              depth={0}
              searchQuery={searchQuery}
              selectedPath={selectedModule}
              onSelect={onModuleSelect}
            />
          )}
        </div>
      )}

      {!listOpen && <div style={{ flex: 1 }} />}

      {/* Dynamic User Real Progress Metric Card */}
      <div style={{ padding: "14px 16px 16px", borderTop: "1px solid rgba(255,255,255,0.05)", flexShrink: 0 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 7 }}>
          <span style={{ fontSize: 11, color: "rgba(255,255,255,0.28)" }}>Your progress</span>
          <span style={{ fontSize: 11, color: "rgba(255,255,255,0.5)", fontWeight: 500 }}>
            {completedFiles} / {totalFiles} files
          </span>
        </div>
        
        {/* Track Loading Bar */}
        <div style={{ height: 4, background: "rgba(255,255,255,0.07)", borderRadius: 99, overflow: "hidden", marginBottom: 6 }}>
          <div style={{ 
            height: "100%", 
            width: `${totalFiles > 0 ? Math.min(100, Math.round((completedFiles / totalFiles) * 100)) : 0}%`, 
            borderRadius: 99, 
            background: "linear-gradient(90deg, #06b6d4, #6d5ce7)",
            transition: "width 0.4s cubic-bezier(0.4, 0, 0.2, 1)"
          }} />
        </div>

        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 4, marginBottom: 12 }}>
          <span style={{ fontSize: 10, color: "rgba(255,255,255,0.22)" }}>Architecture Covered</span>
          <span style={{ fontSize: 11, fontWeight: 700, color: "#06b6d4" }}>
            {totalFiles > 0 ? Math.min(100, Math.round((completedFiles / totalFiles) * 100)) : 0}%
          </span>
        </div>

        {/* User Identity Details Footer */}
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{ width: 34, height: 34, borderRadius: "50%", background: "linear-gradient(135deg, #6d5ce7 0%, #06b6d4 100%)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 12, fontWeight: 700, color: "#fff", flexShrink: 0 }}>
            {userInitials}
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontSize: 13, fontWeight: 600, color: "rgba(255,255,255,0.85)", lineHeight: 1.3, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
              {userName}
            </div>
            <div style={{ fontSize: 11, color: "rgba(255,255,255,0.3)", marginTop: 1 }}>
              {userRole} · day {userDays}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}