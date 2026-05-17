"use client";

import React, { useState } from "react";

export interface Module {
  id: string;
  name: string;
  fileCount: number;
  color: string;
  iconLetter: string;
}

interface LeftPanelModulesProps {
  modules?: Module[];   // optional — safe fallback to []
  selectedModule: string | null;
  onModuleSelect: (moduleId: string | null) => void;
  totalFiles?: number;
  completedFiles?: number;
  userName?: string;
  userInitials?: string;
  userRole?: string;
  userDays?: number;
}

const MODULE_ICONS: Record<string, React.ReactNode> = {
  auth: (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none">
      <rect x="5" y="11" width="14" height="10" rx="2" stroke="currentColor" strokeWidth="1.8"/>
      <path d="M8 11V7a4 4 0 018 0v4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"/>
    </svg>
  ),
  api: (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none">
      <path d="M8 6l-6 6 6 6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M16 6l6 6-6 6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  ),
  database: (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none">
      <ellipse cx="12" cy="6" rx="8" ry="3" stroke="currentColor" strokeWidth="1.8"/>
      <path d="M4 6v6c0 1.66 3.58 3 8 3s8-1.34 8-3V6" stroke="currentColor" strokeWidth="1.8"/>
      <path d="M4 12v6c0 1.66 3.58 3 8 3s8-1.34 8-3v-6" stroke="currentColor" strokeWidth="1.8"/>
    </svg>
  ),
  ui: (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none">
      <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" strokeWidth="1.8"/>
      <path d="M3 9h18" stroke="currentColor" strokeWidth="1.8"/>
      <path d="M9 21V9" stroke="currentColor" strokeWidth="1.8"/>
    </svg>
  ),
  payments: (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none">
      <rect x="2" y="6" width="20" height="14" rx="2" stroke="currentColor" strokeWidth="1.8"/>
      <path d="M2 10h20" stroke="currentColor" strokeWidth="1.8"/>
    </svg>
  ),
  analytics: (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none">
      <path d="M3 20l5-7 4 4 5-8 4 5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  ),
};

const MODULE_COLORS: Record<string, string> = {
  auth:      "#06b6d4",
  api:       "#6d5ce7",
  database:  "#f59e0b",
  ui:        "#a78bfa",
  payments:  "#f97316",
  analytics: "#10b981",
};

export default function LeftPanelModules({
  modules = [],   // ← default to empty array — never undefined
  selectedModule,
  onModuleSelect,
  totalFiles = 0,
  completedFiles = 0,
  userName = "Developer",
  userInitials = "DV",
  userRole = "Engineer",
  userDays = 1,
}: LeftPanelModulesProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [listOpen, setListOpen]       = useState(true);

  // Safe filter — modules is guaranteed to be an array
  const filtered = modules.filter(m =>
    m.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleModuleClick = (moduleId: string) => {
    onModuleSelect(selectedModule === moduleId ? null : moduleId);
  };

  const handleAllModulesClick = () => {
    if (selectedModule !== null) {
      onModuleSelect(null);
    } else {
      setListOpen(v => !v);
    }
  };

  const progressPct = totalFiles > 0 ? Math.round(completedFiles / totalFiles * 100) : 0;

  return (
    <div style={{
      width:250, minWidth:250, maxWidth:250, height:"100%",
      background:"#0d1117", borderRight:"1px solid rgba(255,255,255,0.06)",
      display:"flex", flexDirection:"column", flexShrink:0, overflow:"hidden",
    }}>

      {/* Logo */}
      <div style={{ padding:"22px 18px 16px" }}>
        <span style={{ fontSize:22, fontWeight:800, color:"#ffffff", letterSpacing:"-0.4px" }}>
          Compass AI
        </span>
      </div>

      {/* Search */}
      <div style={{ padding:"0 12px 12px" }}>
        <div style={{ display:"flex", alignItems:"center", height:38, background:"rgba(255,255,255,0.04)", border:"1px solid rgba(255,255,255,0.09)", borderRadius:9, padding:"0 10px", gap:8 }}>
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" style={{ flexShrink:0 }}>
            <circle cx="11" cy="11" r="8" stroke="rgba(255,255,255,0.22)" strokeWidth="2"/>
            <path d="M21 21l-4.35-4.35" stroke="rgba(255,255,255,0.22)" strokeWidth="2" strokeLinecap="round"/>
          </svg>
          <input type="text" placeholder="Search or ask Bob..."
            value={searchQuery} onChange={e => setSearchQuery(e.target.value)}
            style={{ flex:1, minWidth:0, background:"transparent", border:"none", outline:"none", color:"rgba(255,255,255,0.55)", fontSize:12, fontFamily:"inherit" }}
          />
          <div style={{ flexShrink:0, display:"flex", alignItems:"center", gap:2 }}>
            <kbd style={{ fontSize:10, color:"rgba(255,255,255,0.25)", background:"rgba(255,255,255,0.07)", border:"1px solid rgba(255,255,255,0.1)", borderRadius:4, padding:"1px 5px", fontFamily:"inherit", lineHeight:1.6, whiteSpace:"nowrap" }}>⌘</kbd>
            <kbd style={{ fontSize:10, color:"rgba(255,255,255,0.25)", background:"rgba(255,255,255,0.07)", border:"1px solid rgba(255,255,255,0.1)", borderRadius:4, padding:"1px 5px", fontFamily:"inherit", lineHeight:1.6 }}>K</kbd>
          </div>
        </div>
      </div>

      {/* All modules toggle */}
      <div style={{ padding:"0 12px 10px" }}>
        <button onClick={handleAllModulesClick} style={{
          width:"100%", display:"flex", alignItems:"center", justifyContent:"space-between",
          padding:"9px 14px",
          background: selectedModule===null ? "rgba(6,182,212,0.15)" : "rgba(6,182,212,0.07)",
          border: `1px solid ${selectedModule===null ? "rgba(6,182,212,0.4)" : "rgba(6,182,212,0.2)"}`,
          borderRadius:9, cursor:"pointer", transition:"all 0.15s",
        }}>
          <span style={{ fontSize:13, fontWeight:600, color:"#06b6d4" }}>All modules</span>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
            style={{ color:"#06b6d4", transform:listOpen?"rotate(180deg)":"rotate(0deg)", transition:"transform 0.2s", flexShrink:0 }}>
            <path d="M6 9l6 6 6-6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
      </div>

      {/* Module list */}
      {listOpen && (
        <div style={{ flex:1, overflowY:"auto", padding:"2px 12px 0", scrollbarWidth:"none" }}>
          {filtered.length === 0 && (
            <div style={{ fontSize:12, color:"rgba(255,255,255,0.2)", textAlign:"center", padding:"20px 0" }}>
              No modules found
            </div>
          )}
          {filtered.map(mod => {
            const isSelected = selectedModule === mod.id;
            const color = MODULE_COLORS[mod.id] ?? "#64748b";
            const icon  = MODULE_ICONS[mod.id];
            return (
              <button key={mod.id} onClick={() => handleModuleClick(mod.id)}
                style={{
                  width:"100%", display:"flex", alignItems:"center", gap:14,
                  padding:"10px 10px", marginBottom:2,
                  background: isSelected ? `${color}15` : "transparent",
                  border: `1px solid ${isSelected ? `${color}30` : "transparent"}`,
                  borderRadius:8, cursor:"pointer", transition:"all 0.15s", textAlign:"left",
                }}
                onMouseEnter={e => { if(!isSelected)(e.currentTarget as HTMLButtonElement).style.background="rgba(255,255,255,0.04)"; }}
                onMouseLeave={e => { if(!isSelected)(e.currentTarget as HTMLButtonElement).style.background="transparent"; }}
              >
                <div style={{
                  width:32, height:32, borderRadius:8, flexShrink:0,
                  background: isSelected ? `${color}25` : `${color}1a`,
                  border: `1px solid ${isSelected ? `${color}50` : `${color}30`}`,
                  display:"flex", alignItems:"center", justifyContent:"center",
                  color: color,
                  boxShadow: isSelected ? `0 0 10px ${color}30` : "none",
                  transition:"all 0.15s",
                }}>
                  {icon}
                </div>
                <span style={{ fontSize:13, fontWeight:isSelected?600:500, color:isSelected?"#ffffff":"rgba(255,255,255,0.65)", letterSpacing:"0.01em", transition:"color 0.15s" }}>
                  {mod.name}
                </span>
                {isSelected && (
                  <div style={{ marginLeft:"auto", width:6, height:6, borderRadius:"50%", background:color, boxShadow:`0 0 6px ${color}`, flexShrink:0 }}/>
                )}
              </button>
            );
          })}
        </div>
      )}

      {!listOpen && <div style={{ flex:1 }}/>}

      {/* User card */}
      <div style={{ padding:"14px 16px 16px", borderTop:"1px solid rgba(255,255,255,0.05)", flexShrink:0 }}>
        <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:7 }}>
          <span style={{ fontSize:11, color:"rgba(255,255,255,0.28)" }}>Your progress</span>
          <span style={{ fontSize:11, color:"rgba(255,255,255,0.5)", fontWeight:500 }}>{completedFiles} / {totalFiles} files</span>
        </div>
        <div style={{ height:3, background:"rgba(255,255,255,0.07)", borderRadius:99, overflow:"hidden", marginBottom:5 }}>
          <div style={{ height:"100%", width:`${progressPct}%`, borderRadius:99, background:"linear-gradient(90deg, #06b6d4, #6d5ce7)" }}/>
        </div>
        <div style={{ textAlign:"right", marginBottom:14 }}>
          <span style={{ fontSize:11, fontWeight:700, color:"#06b6d4" }}>{progressPct}%</span>
        </div>
        <div style={{ display:"flex", alignItems:"center", gap:10 }}>
          <div style={{ width:34, height:34, borderRadius:"50%", background:"linear-gradient(135deg, #6d5ce7 0%, #06b6d4 100%)", display:"flex", alignItems:"center", justifyContent:"center", fontSize:12, fontWeight:700, color:"#fff", flexShrink:0 }}>
            {userInitials}
          </div>
          <div style={{ flex:1, minWidth:0 }}>
            <div style={{ fontSize:13, fontWeight:600, color:"rgba(255,255,255,0.85)", lineHeight:1.3, whiteSpace:"nowrap", overflow:"hidden", textOverflow:"ellipsis" }}>
              {userName}
            </div>
            <div style={{ fontSize:11, color:"rgba(255,255,255,0.3)", marginTop:1 }}>
              {userRole} · day {userDays}
            </div>
          </div>
          <button
            style={{ background:"transparent", border:"none", cursor:"pointer", color:"rgba(255,255,255,0.2)", padding:4, flexShrink:0, display:"flex", alignItems:"center" }}
            onMouseEnter={e => ((e.currentTarget as HTMLButtonElement).style.color="rgba(255,255,255,0.5)")}
            onMouseLeave={e => ((e.currentTarget as HTMLButtonElement).style.color="rgba(255,255,255,0.2)")}
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor">
              <circle cx="5"  cy="12" r="1.5"/>
              <circle cx="12" cy="12" r="1.5"/>
              <circle cx="19" cy="12" r="1.5"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}

// Made with Bob
