"use client";

import React, { useState, useRef, useCallback } from "react";
import { ConstellationMapProps, ConstellationEdge, ViewType } from "@/types";
import { UIFileNode } from "@/lib/api";

const ALL_MODULE_CLUSTERS = [
  {
    id: "auth",
    label: "AUTH",
    cx: 160,
    cy: 210,
    isHere: true,
    dots: [
      { x: 0, y: 0, size: 10, isCurrent: true },
      { x: -28, y: -18, size: 3, isCurrent: false },
      { x: 20, y: -30, size: 2, isCurrent: false },
      { x: 35, y: 10, size: 2.5, isCurrent: false },
      { x: -15, y: 25, size: 2, isCurrent: false },
    ],
    connections: [
      [0, 1],
      [0, 2],
      [0, 3],
      [0, 4],
    ],
  },
  {
    id: "api",
    label: "API",
    cx: 490,
    cy: 110,
    isHere: false,
    dots: [
      { x: 0, y: 0, size: 6, isCurrent: false },
      { x: -22, y: -30, size: 2.5, isCurrent: false },
      { x: 18, y: -25, size: 2, isCurrent: false },
      { x: 30, y: 15, size: 2, isCurrent: false },
      { x: -10, y: 20, size: 3, isCurrent: false },
      { x: 10, y: 35, size: 2, isCurrent: false },
    ],
    connections: [
      [0, 1],
      [0, 2],
      [0, 3],
      [0, 4],
      [0, 5],
      [4, 5],
    ],
  },
  {
    id: "database",
    label: "DATABASE",
    cx: 630,
    cy: 320,
    isHere: false,
    dots: [
      { x: 0, y: 0, size: 5, isCurrent: false },
      { x: -20, y: -28, size: 2, isCurrent: false },
      { x: 25, y: -20, size: 2.5, isCurrent: false },
      { x: 30, y: 20, size: 2, isCurrent: false },
      { x: -15, y: 25, size: 2, isCurrent: false },
      { x: 10, y: -40, size: 1.5, isCurrent: false },
    ],
    connections: [
      [0, 1],
      [0, 2],
      [0, 3],
      [0, 4],
      [0, 5],
    ],
  },
  {
    id: "ui",
    label: "UI",
    cx: 390,
    cy: 400,
    isHere: false,
    dots: [
      { x: 0, y: 0, size: 7, isCurrent: false },
      { x: -30, y: -15, size: 2.5, isCurrent: false },
      { x: -45, y: 10, size: 2, isCurrent: false },
      { x: 25, y: -20, size: 2, isCurrent: false },
      { x: 35, y: 10, size: 2.5, isCurrent: false },
      { x: 10, y: 30, size: 2, isCurrent: false },
      { x: -20, y: 30, size: 2, isCurrent: false },
    ],
    connections: [
      [0, 1],
      [0, 2],
      [0, 3],
      [0, 4],
      [0, 5],
      [0, 6],
      [1, 2],
      [3, 4],
    ],
  },
  {
    id: "analytics",
    label: "ANALYTICS",
    cx: 145,
    cy: 500,
    isHere: false,
    dots: [
      { x: 0, y: 0, size: 5, isCurrent: false },
      { x: -25, y: -20, size: 2.5, isCurrent: false },
      { x: 20, y: -25, size: 2, isCurrent: false },
      { x: 30, y: 15, size: 2, isCurrent: false },
    ],
    connections: [
      [0, 1],
      [0, 2],
      [0, 3],
    ],
  },
  {
    id: "payments",
    label: "PAYMENTS",
    cx: 600,
    cy: 520,
    isHere: false,
    dots: [
      { x: 0, y: 0, size: 5, isCurrent: false },
      { x: -28, y: -15, size: 2, isCurrent: false },
      { x: -15, y: -30, size: 2.5, isCurrent: false },
      { x: 25, y: -20, size: 2, isCurrent: false },
      { x: 30, y: 15, size: 2, isCurrent: false },
    ],
    connections: [
      [0, 1],
      [0, 2],
      [0, 3],
      [0, 4],
      [1, 2],
    ],
  },
];

const CLUSTER_LINES = [
  { from: "auth", to: "api" },
  { from: "api", to: "database" },
  { from: "api", to: "ui" },
  { from: "auth", to: "ui" },
  { from: "ui", to: "analytics" },
  { from: "ui", to: "payments" },
  { from: "database", to: "payments" },
];

const BG_STARS = Array.from({ length: 55 }, (_, i) => ({
  x: ((i * 137 + 50) % 780) + 20,
  y: ((i * 97 + 30) % 580) + 20,
  r: i % 7 === 0 ? 1.5 : i % 3 === 0 ? 1 : 0.5,
  o: 0.12 + (i % 5) * 0.05,
}));

const MODULES = [
  { id: "auth", label: "AUTH" },
  { id: "api", label: "API" },
  { id: "database", label: "DATABASE" },
  { id: "ui", label: "UI" },
  { id: "payments", label: "PAYMENTS" },
  { id: "analytics", label: "ANALYTICS" },
];

function getClusterCenter(id: string) {
  const c = ALL_MODULE_CLUSTERS.find((m) => m.id === id);
  return c ? { x: c.cx, y: c.cy } : { x: 0, y: 0 };
}

// ✅ moduleFileEdges now uses ConstellationEdge[] (not UIFileEdge[])
interface Props extends ConstellationMapProps {
  onViewChange?: (view: ViewType) => void;
  selectedModule?: string | null;
  onModuleChange?: (moduleId: string | null) => void;
  moduleFileNodes?: UIFileNode[];
  moduleFileEdges?: ConstellationEdge[];
  availableModules?: Array<{ id: string; name: string }>;
}

export default function ConstellationMap({
  onNodeClick,
  selectedNode,
  onViewChange,
  selectedModule,
  onModuleChange,
  moduleFileNodes,
  moduleFileEdges,
  availableModules,
}: Props) {
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [dragging, setDragging] = useState(false);
  const [dropdown, setDropdown] = useState(false);
  const dragStart = useRef({ x: 0, y: 0, px: 0, py: 0 });

  const isModuleView = !!selectedModule;
  const fileNodes: UIFileNode[] = (moduleFileNodes as UIFileNode[]) ?? [];
  // ✅ fileEdges uses ConstellationEdge shape (source/target, not from/to)
  const fileEdges: ConstellationEdge[] = moduleFileEdges ?? [];

  const onMouseDown = useCallback(
    (e: React.MouseEvent) => {
      setDragging(true);
      dragStart.current = { x: e.clientX, y: e.clientY, px: pan.x, py: pan.y };
    },
    [pan],
  );
  const onMouseMove = useCallback(
    (e: React.MouseEvent) => {
      if (!dragging) return;
      setPan({
        x: dragStart.current.px + e.clientX - dragStart.current.x,
        y: dragStart.current.py + e.clientY - dragStart.current.y,
      });
    },
    [dragging],
  );
  const onMouseUp = useCallback(() => setDragging(false), []);
  const onWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault();
    setZoom((z) => Math.min(3, Math.max(0.3, z - e.deltaY * 0.001)));
  }, []);

  const selectModule = (id: string | null) => {
    onModuleChange?.(id);
    setDropdown(false);
  };

  // Use real modules if available, fallback to hardcoded MODULES
  const modulesData =
    availableModules && availableModules.length > 0
      ? availableModules.map((m) => ({ id: m.id, label: m.name }))
      : MODULES;

  const dropdownLabel = isModuleView
    ? (modulesData.find((m) => m.id === selectedModule)?.label ?? "All modules")
    : "All modules";

  const dropdownItems: { id: string | null; label: string }[] = isModuleView
    ? [{ id: null, label: "All modules" }, ...modulesData]
    : modulesData.map((m) => ({ id: m.id, label: m.label }));

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        position: "relative",
        overflow: "hidden",
        background:
          "radial-gradient(ellipse at 35% 40%, #1e2a5e 0%, #12184a 25%, #0d1117 65%)",
        cursor: dragging ? "grabbing" : "grab",
        userSelect: "none",
      }}
      onMouseDown={onMouseDown}
      onMouseMove={onMouseMove}
      onMouseUp={onMouseUp}
      onMouseLeave={onMouseUp}
      onWheel={onWheel}
    >
      <div
        style={{
          position: "absolute",
          top: "8%",
          right: "18%",
          width: 320,
          height: 320,
          borderRadius: "50%",
          background:
            "radial-gradient(circle, rgba(180,120,255,0.07) 0%, transparent 70%)",
          pointerEvents: "none",
        }}
      />
      <div
        style={{
          position: "absolute",
          bottom: "18%",
          left: "8%",
          width: 220,
          height: 220,
          borderRadius: "50%",
          background:
            "radial-gradient(circle, rgba(6,182,212,0.06) 0%, transparent 70%)",
          pointerEvents: "none",
        }}
      />

      {/* TOP BAR */}
      <div
        style={{
          position: "absolute",
          top: 14,
          left: 0,
          right: 0,
          display: "flex",
          alignItems: "flex-start",
          justifyContent: "space-between",
          padding: "0 18px",
          zIndex: 30,
          pointerEvents: "none",
        }}
      >
        {/* Dropdown */}
        <div style={{ position: "relative", pointerEvents: "all" }}>
          <button
            onClick={() => setDropdown((v) => !v)}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              background: "rgba(255,255,255,0.07)",
              border: "1px solid rgba(255,255,255,0.14)",
              borderRadius: 9,
              padding: "7px 14px",
              color: "rgba(255,255,255,0.85)",
              fontSize: 13,
              fontWeight: 500,
              cursor: "pointer",
              fontFamily: "inherit",
            }}
          >
            {dropdownLabel}
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none">
              <path
                d="M6 9l6 6 6-6"
                stroke="rgba(255,255,255,0.5)"
                strokeWidth="2"
                strokeLinecap="round"
              />
            </svg>
          </button>
          {dropdown && (
            <div
              style={{
                position: "absolute",
                top: "calc(100% + 6px)",
                left: 0,
                background: "#1a2234",
                border: "1px solid rgba(255,255,255,0.1)",
                borderRadius: 10,
                overflow: "hidden",
                zIndex: 50,
                minWidth: 160,
                boxShadow: "0 8px 32px rgba(0,0,0,0.5)",
              }}
              onMouseDown={(e) => e.stopPropagation()}
            >
              {dropdownItems.map((item) => {
                const isActive = item.id === selectedModule;
                const isAll = item.id === null;
                return (
                  <button
                    key={item.label}
                    onClick={() => selectModule(item.id)}
                    style={{
                      width: "100%",
                      display: "block",
                      padding: isAll ? "9px 16px 8px" : "8px 16px",
                      background: "transparent",
                      border: "none",
                      borderBottom: isAll
                        ? "1px solid rgba(255,255,255,0.07)"
                        : "none",
                      color: isAll
                        ? "rgba(255,255,255,0.4)"
                        : isActive
                          ? "#06b6d4"
                          : "rgba(255,255,255,0.7)",
                      fontSize: isAll ? 11 : 12,
                      fontWeight: isActive ? 600 : 400,
                      cursor: "pointer",
                      textAlign: "left",
                      fontFamily: "inherit",
                      letterSpacing: isAll ? "0.02em" : "0.05em",
                    }}
                    onMouseEnter={(e) => {
                      (e.currentTarget as HTMLButtonElement).style.background =
                        "rgba(255,255,255,0.05)";
                    }}
                    onMouseLeave={(e) => {
                      (e.currentTarget as HTMLButtonElement).style.background =
                        "transparent";
                    }}
                  >
                    {isActive && !isAll && (
                      <span style={{ color: "#06b6d4", marginRight: 6 }}>
                        ✓
                      </span>
                    )}
                    {item.label}
                  </button>
                );
              })}
            </div>
          )}
        </div>

        {/* Toggle */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            background: "rgba(255,255,255,0.05)",
            border: "1px solid rgba(255,255,255,0.1)",
            borderRadius: 10,
            padding: 3,
            gap: 2,
            pointerEvents: "all",
          }}
        >
          <div
            style={{
              padding: "6px 14px",
              borderRadius: 8,
              background: "rgba(6,182,212,0.18)",
              border: "1px solid rgba(6,182,212,0.35)",
              display: "flex",
              alignItems: "center",
              gap: 6,
            }}
          >
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="2.5" fill="#06b6d4" />
              <circle cx="4" cy="5" r="1.5" fill="rgba(6,182,212,0.7)" />
              <circle cx="20" cy="5" r="1.5" fill="rgba(6,182,212,0.7)" />
              <circle cx="4" cy="19" r="1.5" fill="rgba(6,182,212,0.7)" />
              <circle cx="20" cy="19" r="1.5" fill="rgba(6,182,212,0.7)" />
              <line
                x1="12"
                y1="12"
                x2="4"
                y2="5"
                stroke="rgba(6,182,212,0.4)"
                strokeWidth="1"
              />
              <line
                x1="12"
                y1="12"
                x2="20"
                y2="5"
                stroke="rgba(6,182,212,0.4)"
                strokeWidth="1"
              />
              <line
                x1="12"
                y1="12"
                x2="4"
                y2="19"
                stroke="rgba(6,182,212,0.4)"
                strokeWidth="1"
              />
              <line
                x1="12"
                y1="12"
                x2="20"
                y2="19"
                stroke="rgba(6,182,212,0.4)"
                strokeWidth="1"
              />
            </svg>
            <span style={{ fontSize: 12, fontWeight: 600, color: "#06b6d4" }}>
              Constellation
            </span>
          </div>
          <button
            onClick={() => onViewChange?.("levelMap")}
            style={{
              padding: "6px 14px",
              borderRadius: 8,
              background: "transparent",
              border: "1px solid transparent",
              display: "flex",
              alignItems: "center",
              gap: 6,
              cursor: "pointer",
              fontFamily: "inherit",
            }}
          >
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none">
              <path
                d="M3 6h18M3 12h18M3 18h18"
                stroke="rgba(255,255,255,0.35)"
                strokeWidth="1.5"
                strokeLinecap="round"
              />
            </svg>
            <span style={{ fontSize: 12, color: "rgba(255,255,255,0.4)" }}>
              Level Map
            </span>
          </button>
        </div>

        {/* Right: progress + zoom */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "flex-end",
            gap: 8,
            pointerEvents: "all",
          }}
        >
          {isModuleView && fileNodes.length > 0 && (
            <div
              style={{
                background: "rgba(255,255,255,0.05)",
                border: "1px solid rgba(255,255,255,0.1)",
                borderRadius: 8,
                padding: "6px 12px",
                textAlign: "right",
                minWidth: 160,
              }}
            >
              <div style={{ fontSize: 11, color: "rgba(255,255,255,0.45)" }}>
                {selectedModule!.toUpperCase()} module{" "}
                <span
                  style={{ color: "rgba(255,255,255,0.85)", fontWeight: 600 }}
                >
                  {fileNodes.filter((n) => n.status === "done").length} /{" "}
                  {fileNodes.length} files
                </span>
              </div>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  marginTop: 4,
                }}
              >
                <div
                  style={{
                    flex: 1,
                    height: 3,
                    background: "rgba(255,255,255,0.08)",
                    borderRadius: 99,
                    overflow: "hidden",
                  }}
                >
                  <div
                    style={{
                      width: `${Math.round((fileNodes.filter((n) => n.status === "done").length / fileNodes.length) * 100)}%`,
                      height: "100%",
                      background: "#10b981",
                      borderRadius: 99,
                    }}
                  />
                </div>
                <span
                  style={{ fontSize: 11, fontWeight: 700, color: "#10b981" }}
                >
                  {Math.round(
                    (fileNodes.filter((n) => n.status === "done").length /
                      fileNodes.length) *
                      100,
                  )}
                  %
                </span>
              </div>
            </div>
          )}
          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            {[
              { l: "+", a: () => setZoom((z) => Math.min(3, z + 0.2)) },
              { l: "−", a: () => setZoom((z) => Math.max(0.3, z - 0.2)) },
              {
                l: "↺",
                a: () => {
                  setZoom(1);
                  setPan({ x: 0, y: 0 });
                },
              },
            ].map(({ l, a }) => (
              <button
                key={l}
                onClick={a}
                style={{
                  width: 32,
                  height: 32,
                  borderRadius: 8,
                  background: "rgba(255,255,255,0.07)",
                  border: "1px solid rgba(255,255,255,0.12)",
                  color: "rgba(255,255,255,0.65)",
                  fontSize: 15,
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontFamily: "inherit",
                }}
              >
                {l}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* SVG */}
      <svg
        width="100%"
        height="100%"
        style={{ position: "absolute", inset: 0 }}
      >
        <defs>
          <radialGradient id="cyanGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.55" />
            <stop offset="100%" stopColor="#06b6d4" stopOpacity="0" />
          </radialGradient>
          <radialGradient id="greenGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#10b981" stopOpacity="0.4" />
            <stop offset="100%" stopColor="#10b981" stopOpacity="0" />
          </radialGradient>
          <filter id="glow2">
            <feGaussianBlur stdDeviation="2.5" result="b" />
            <feMerge>
              <feMergeNode in="b" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <filter id="glow5">
            <feGaussianBlur stdDeviation="5" result="b" />
            <feMerge>
              <feMergeNode in="b" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        <g transform={`translate(${pan.x},${pan.y}) scale(${zoom})`}>
          {BG_STARS.map((s, i) => (
            <circle
              key={i}
              cx={s.x}
              cy={s.y}
              r={s.r}
              fill="white"
              opacity={s.o}
            />
          ))}

          {/* ── ALL MODULES VIEW ── */}
          {!isModuleView && fileNodes.length === 0 && (
            <>
              {CLUSTER_LINES.map(({ from, to }) => {
                const a = getClusterCenter(from),
                  b = getClusterCenter(to);
                return (
                  <line
                    key={`${from}-${to}`}
                    x1={a.x}
                    y1={a.y}
                    x2={b.x}
                    y2={b.y}
                    stroke="rgba(255,255,255,0.09)"
                    strokeWidth="0.9"
                  />
                );
              })}
              {ALL_MODULE_CLUSTERS.map((cluster) => (
                <g
                  key={cluster.id}
                  onClick={() => onModuleChange?.(cluster.id)}
                  style={{ cursor: "pointer" }}
                >
                  <circle
                    cx={cluster.cx}
                    cy={cluster.cy}
                    r={70}
                    fill="transparent"
                  />
                  {cluster.isHere && (
                    <circle
                      cx={cluster.cx}
                      cy={cluster.cy}
                      r={46}
                      fill="url(#cyanGlow)"
                    />
                  )}
                  {cluster.connections.map(([a, b], i) => (
                    <line
                      key={i}
                      x1={cluster.cx + cluster.dots[a].x}
                      y1={cluster.cy + cluster.dots[a].y}
                      x2={cluster.cx + cluster.dots[b].x}
                      y2={cluster.cy + cluster.dots[b].y}
                      stroke={
                        cluster.isHere
                          ? "rgba(6,182,212,0.3)"
                          : "rgba(255,255,255,0.18)"
                      }
                      strokeWidth="0.9"
                    />
                  ))}
                  {cluster.dots.map((dot, i) => (
                    <g key={i}>
                      {dot.isCurrent && (
                        <>
                          <circle
                            cx={cluster.cx + dot.x}
                            cy={cluster.cy + dot.y}
                            r={dot.size + 12}
                            fill="none"
                            stroke="rgba(6,182,212,0.15)"
                            strokeWidth="1"
                          />
                          <circle
                            cx={cluster.cx + dot.x}
                            cy={cluster.cy + dot.y}
                            r={dot.size + 6}
                            fill="rgba(6,182,212,0.08)"
                            stroke="rgba(6,182,212,0.35)"
                            strokeWidth="1"
                          />
                        </>
                      )}
                      <circle
                        cx={cluster.cx + dot.x}
                        cy={cluster.cy + dot.y}
                        r={dot.size}
                        fill={
                          dot.isCurrent ? "#06b6d4" : "rgba(255,255,255,0.85)"
                        }
                        filter={dot.isCurrent ? "url(#glow5)" : "url(#glow2)"}
                      />
                    </g>
                  ))}
                  {cluster.isHere && (
                    <text
                      x={cluster.cx + cluster.dots[0].x}
                      y={cluster.cy + cluster.dots[0].y - 22}
                      textAnchor="middle"
                      fontSize="8"
                      fontWeight="700"
                      letterSpacing="1.5"
                      fill="#06b6d4"
                      fontFamily="inherit"
                    >
                      YOU ARE HERE
                    </text>
                  )}
                  <text
                    x={cluster.cx}
                    y={cluster.cy + 60}
                    textAnchor="middle"
                    fontSize="10"
                    fontWeight="600"
                    letterSpacing="2"
                    fill="rgba(255,255,255,0.55)"
                    fontFamily="inherit"
                  >
                    {cluster.label}
                  </text>
                </g>
              ))}
            </>
          )}

          {/* ── REAL DATA VIEW (both overview and module-specific) ── */}
          {fileNodes.length > 0 && (
            <>
              {isModuleView && (
                <text
                  x="390"
                  y="88"
                  textAnchor="middle"
                  fontSize="13"
                  fontWeight="700"
                  letterSpacing="10"
                  fill="rgba(6,182,212,0.65)"
                  fontFamily="inherit"
                >
                  {selectedModule!.toUpperCase().split("").join(" ")}
                </text>
              )}
              {!isModuleView && (
                <text
                  x="390"
                  y="88"
                  textAnchor="middle"
                  fontSize="13"
                  fontWeight="700"
                  letterSpacing="3"
                  fill="rgba(6,182,212,0.65)"
                  fontFamily="inherit"
                >
                  REPOSITORY OVERVIEW
                </text>
              )}

              {/* ✅ Uses edge.source / edge.target (ConstellationEdge shape) */}
              {fileEdges.map((edge) => {
                const a = fileNodes.find((n) => n.id === edge.source);
                const b = fileNodes.find((n) => n.id === edge.target);
                if (!a || !b) return null;
                const colored =
                  (a.status === "done" && b.status === "done") ||
                  a.status === "current" ||
                  b.status === "current";
                return (
                  <line
                    key={edge.id}
                    x1={a.x}
                    y1={a.y}
                    x2={b.x}
                    y2={b.y}
                    stroke={
                      colored
                        ? "rgba(16,185,129,0.55)"
                        : "rgba(255,255,255,0.12)"
                    }
                    strokeWidth={colored ? 1.5 : 1}
                  />
                );
              })}

              {fileNodes.map((node) => {
                const isCurrent = node.status === "current";
                const isDone = node.status === "done";
                const r = isCurrent ? 26 : isDone ? 22 : 5;
                const fill = isCurrent
                  ? "rgba(6,182,212,0.15)"
                  : isDone
                    ? "rgba(16,185,129,0.15)"
                    : "rgba(255,255,255,0.03)";
                const stroke = isCurrent
                  ? "#06b6d4"
                  : isDone
                    ? "#10b981"
                    : "rgba(255,255,255,0.2)";
                return (
                  <g
                    key={node.id}
                    onClick={() => onNodeClick(node.id)}
                    style={{ cursor: "pointer" }}
                  >
                    {(isCurrent || isDone) && (
                      <circle
                        cx={node.x}
                        cy={node.y}
                        r={r + 18}
                        fill={isCurrent ? "url(#cyanGlow)" : "url(#greenGlow)"}
                      />
                    )}
                    {isCurrent && (
                      <>
                        <circle
                          cx={node.x}
                          cy={node.y}
                          r={r + 10}
                          fill="none"
                          stroke="rgba(6,182,212,0.2)"
                          strokeWidth="1"
                        />
                        <circle
                          cx={node.x}
                          cy={node.y}
                          r={r + 5}
                          fill="rgba(6,182,212,0.08)"
                          stroke="rgba(6,182,212,0.4)"
                          strokeWidth="1.5"
                        />
                      </>
                    )}
                    <circle
                      cx={node.x}
                      cy={node.y}
                      r={r}
                      fill={fill}
                      stroke={stroke}
                      strokeWidth={isDone || isCurrent ? 2 : 1}
                      filter={isDone || isCurrent ? "url(#glow5)" : ""}
                    />
                    {isDone && (
                      <path
                        d={`M${node.x - 8},${node.y} L${node.x - 2},${node.y + 6} L${node.x + 9},${node.y - 7}`}
                        stroke="#10b981"
                        strokeWidth="2.5"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        fill="none"
                      />
                    )}
                    {isCurrent && (
                      <circle
                        cx={node.x}
                        cy={node.y}
                        r={5}
                        fill="#06b6d4"
                        filter="url(#glow5)"
                      />
                    )}
                    {node.status === "locked" && (
                      <circle
                        cx={node.x}
                        cy={node.y}
                        r={2.5}
                        fill="rgba(255,255,255,0.35)"
                      />
                    )}
                    {isCurrent && (
                      <text
                        x={node.x}
                        y={node.y - r - 13}
                        textAnchor="middle"
                        fontSize="8"
                        fontWeight="700"
                        letterSpacing="1.5"
                        fill="#06b6d4"
                        fontFamily="inherit"
                      >
                        YOU ARE HERE
                      </text>
                    )}
                    <text
                      x={node.x}
                      y={node.y + r + 15}
                      textAnchor="middle"
                      fontSize={isDone || isCurrent ? "11" : "9"}
                      fontWeight={isDone || isCurrent ? "600" : "400"}
                      fill={
                        isDone
                          ? "#10b981"
                          : isCurrent
                            ? "#06b6d4"
                            : "rgba(255,255,255,0.35)"
                      }
                      fontFamily="monospace"
                    >
                      {node.label}
                    </text>
                  </g>
                );
              })}
            </>
          )}
        </g>
      </svg>

      {/* Key */}
      {!isModuleView && (
        <div
          style={{
            position: "absolute",
            bottom: 18,
            left: 18,
            background: "rgba(13,17,23,0.82)",
            border: "1px solid rgba(255,255,255,0.08)",
            borderRadius: 10,
            padding: "10px 14px",
            backdropFilter: "blur(8px)",
            zIndex: 10,
          }}
        >
          <div
            style={{
              fontSize: 11,
              fontWeight: 600,
              color: "rgba(255,255,255,0.65)",
              marginBottom: 7,
            }}
          >
            Key
          </div>
          {[
            { r: 4, fill: "rgba(255,255,255,0.65)", label: "Star = a file" },
            {
              r: 7,
              fill: "rgba(255,255,255,0.9)",
              label: "Size = dependency weight",
            },
            { r: 5, fill: "#06b6d4", label: "Where you are now" },
          ].map(({ r, fill, label }) => (
            <div
              key={label}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
                marginBottom: 5,
              }}
            >
              <svg width={16} height={16}>
                <circle cx={8} cy={8} r={r} fill={fill} />
              </svg>
              <span style={{ fontSize: 11, color: "rgba(255,255,255,0.45)" }}>
                {label}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// Made with Bob
