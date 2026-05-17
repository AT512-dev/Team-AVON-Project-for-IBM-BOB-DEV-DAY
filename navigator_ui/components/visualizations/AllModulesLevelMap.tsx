"use client";

import React from "react";
import { LevelNode, ViewType } from "@/types";
import ModuleDropdown from "./ModuleDropdown";

const BG_STARS = Array.from({ length: 40 }, (_, i) => ({
  x: ((i * 137 + 50) % 720) + 20,
  y: ((i * 97 + 30) % 680) + 20,
  r: i % 7 === 0 ? 1.5 : i % 3 === 0 ? 1 : 0.5,
  o: 0.1 + (i % 5) * 0.04,
}));

const MODULE_COLORS: Record<
  string,
  { ring: string; text: string; bg: string }
> = {
  AUTH: { ring: "#06b6d4", text: "#06b6d4", bg: "rgba(6,182,212,0.12)" },
  API: { ring: "#6d5ce7", text: "#a78bfa", bg: "rgba(109,92,231,0.1)" },
  DATABASE: { ring: "#b45309", text: "#d97706", bg: "rgba(180,83,9,0.1)" },
  UI: { ring: "#7c3aed", text: "#a78bfa", bg: "rgba(124,58,237,0.1)" },
  PAYMENTS: { ring: "#b45309", text: "#d97706", bg: "rgba(180,83,9,0.1)" },
  ANALYTICS: { ring: "#475569", text: "#94a3b8", bg: "rgba(71,85,105,0.08)" },
};

interface Props {
  levels: LevelNode[];
  onViewChange?: (view: ViewType) => void;
  onModuleSelect: (moduleId: string) => void;
  // Pass null to reset to all-modules
  onModuleChange?: (moduleId: string | null) => void;
}

export default function AllModulesLevelMap({
  levels,
  onViewChange,
  onModuleSelect,
  onModuleChange,
}: Props) {
  const currentIndex = levels.findIndex((l) => !l.isCompleted);

  const NODE_GAP = 110;
  const LEFT_X = 155;
  const RIGHT_X = 315;
  const START_Y = 70;
  const CANVAS_W = 480;

  const nodePositions = levels.map((_, i) => ({
    x: i % 2 === 0 ? LEFT_X : RIGHT_X,
    y: START_Y + i * NODE_GAP,
  }));

  const totalHeight = START_Y + levels.length * NODE_GAP + 180;

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        position: "relative",
        overflow: "auto",
        background:
          "radial-gradient(ellipse at 50% 10%, #1a2650 0%, #0f1735 30%, #0a0d1a 70%)",
      }}
    >
      <svg
        style={{
          position: "absolute",
          inset: 0,
          width: "100%",
          height: "100%",
          pointerEvents: "none",
        }}
      >
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
      </svg>

      {/* Top bar */}
      <div
        style={{
          position: "sticky",
          top: 0,
          left: 0,
          right: 0,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "10px 16px",
          background: "rgba(10,13,26,0.75)",
          backdropFilter: "blur(12px)",
          borderBottom: "1px solid rgba(255,255,255,0.05)",
          zIndex: 20,
        }}
      >
        {/* Single dropdown — shows "All modules" when no module selected */}
        <ModuleDropdown
          selectedModule={null}
          onModuleChange={(id) => {
            if (id) onModuleSelect(id);
            else onModuleChange?.(null);
          }}
        />

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
          }}
        >
          <button
            onClick={() => onViewChange?.("constellation")}
            style={{
              padding: "5px 14px",
              borderRadius: 7,
              background: "transparent",
              border: "1px solid transparent",
              display: "flex",
              alignItems: "center",
              gap: 5,
              cursor: "pointer",
              fontFamily: "inherit",
            }}
          >
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="2.5" fill="rgba(255,255,255,0.3)" />
              <circle cx="4" cy="5" r="1.5" fill="rgba(255,255,255,0.2)" />
              <circle cx="20" cy="5" r="1.5" fill="rgba(255,255,255,0.2)" />
            </svg>
            <span style={{ fontSize: 12, color: "rgba(255,255,255,0.4)" }}>
              Constellation
            </span>
          </button>
          <div
            style={{
              padding: "5px 14px",
              borderRadius: 7,
              background: "rgba(6,182,212,0.18)",
              border: "1px solid rgba(6,182,212,0.35)",
              display: "flex",
              alignItems: "center",
              gap: 5,
            }}
          >
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none">
              <path
                d="M3 6h18M3 12h18M3 18h18"
                stroke="#06b6d4"
                strokeWidth="1.8"
                strokeLinecap="round"
              />
            </svg>
            <span style={{ fontSize: 12, fontWeight: 600, color: "#06b6d4" }}>
              Level Map
            </span>
          </div>
        </div>

        <div style={{ width: 80 }} />
      </div>

      {/* SVG canvas */}
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          paddingTop: 20,
          paddingBottom: 60,
          position: "relative",
          zIndex: 1,
        }}
      >
        <svg
          width={CANVAS_W}
          height={totalHeight}
          viewBox={`0 0 ${CANVAS_W} ${totalHeight}`}
          style={{ overflow: "visible" }}
        >
          <defs>
            <filter id="amg4">
              <feGaussianBlur stdDeviation="4" result="b" />
              <feMerge>
                <feMergeNode in="b" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
            <radialGradient id="amGold" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#f59e0b" />
              <stop offset="100%" stopColor="#b45309" />
            </radialGradient>
          </defs>

          {/* Connectors */}
          {levels.map((level, i) => {
            if (i >= levels.length - 1) return null;
            const a = nodePositions[i];
            const b = nodePositions[i + 1];
            return (
              <path
                key={`line-${i}`}
                d={`M ${a.x} ${a.y} C ${a.x} ${a.y + 55} ${b.x} ${b.y - 55} ${b.x} ${b.y}`}
                stroke={
                  level.isCompleted
                    ? "rgba(6,182,212,0.4)"
                    : "rgba(255,255,255,0.1)"
                }
                strokeWidth="1.5"
                strokeDasharray={level.isCompleted ? "none" : "5 6"}
                fill="none"
              />
            );
          })}

          {/* Module nodes */}
          {levels.map((level, index) => {
            const isDone = level.isCompleted;
            const isCurrent = index === currentIndex;
            const pos = nodePositions[index];
            const r = isCurrent ? 34 : isDone ? 28 : 22;
            const mc =
              MODULE_COLORS[level.fileName] ?? MODULE_COLORS["ANALYTICS"];
            const moduleId = level.fileName.toLowerCase();

            const ringColor = isCurrent ? "#06b6d4" : mc.ring;
            const bgColor = isCurrent ? "rgba(6,182,212,0.12)" : mc.bg;
            const numColor = isCurrent ? "#06b6d4" : mc.text;
            const labelCol = isCurrent ? "#06b6d4" : mc.text;

            return (
              <g
                key={level.id}
                onClick={() => onModuleSelect(moduleId)}
                style={{ cursor: "pointer" }}
              >
                <circle cx={pos.x} cy={pos.y} r={r + 20} fill="transparent" />

                {isCurrent && (
                  <circle
                    cx={pos.x}
                    cy={pos.y}
                    r={r + 18}
                    fill="rgba(6,182,212,0.07)"
                  />
                )}
                {isCurrent && (
                  <circle
                    cx={pos.x}
                    cy={pos.y}
                    r={r + 10}
                    fill="none"
                    stroke="rgba(6,182,212,0.2)"
                    strokeWidth="1"
                  />
                )}

                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r={r}
                  fill={bgColor}
                  stroke={ringColor}
                  strokeWidth={isCurrent ? 2 : 1.5}
                  filter={isCurrent ? "url(#amg4)" : ""}
                />

                {isDone && (
                  <path
                    d={`M ${pos.x - r * 0.38} ${pos.y} L ${pos.x - r * 0.08} ${pos.y + r * 0.33} L ${pos.x + r * 0.42} ${pos.y - r * 0.33}`}
                    stroke="#10b981"
                    strokeWidth="2.2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    fill="none"
                  />
                )}

                {!isDone && (
                  <text
                    x={pos.x}
                    y={pos.y + 1}
                    textAnchor="middle"
                    dominantBaseline="middle"
                    fontSize={isCurrent ? 18 : 14}
                    fontWeight="700"
                    fill={numColor}
                    fontFamily="inherit"
                  >
                    {level.level}
                  </text>
                )}

                {isCurrent && (
                  <text
                    x={pos.x}
                    y={pos.y - r - 14}
                    textAnchor="middle"
                    fontSize="8"
                    fontWeight="700"
                    letterSpacing="1.5"
                    fill="#06b6d4"
                    fontFamily="inherit"
                  >
                    YOU&apos;RE HERE
                  </text>
                )}

                <text
                  x={pos.x}
                  y={pos.y + r + 16}
                  textAnchor="middle"
                  fontSize={isCurrent ? 13 : 11}
                  fontWeight={isCurrent ? 600 : 500}
                  fill={labelCol}
                  fontFamily="inherit"
                >
                  {level.fileName}
                </text>

                <text
                  x={pos.x}
                  y={pos.y + r + 30}
                  textAnchor="middle"
                  fontSize="9"
                  fill="rgba(255,255,255,0.3)"
                  fontFamily="inherit"
                >
                  {level.description}
                </text>

                {isCurrent && (
                  <text
                    x={pos.x}
                    y={pos.y + r + 44}
                    textAnchor="middle"
                    fontSize="9"
                    fill="rgba(6,182,212,0.65)"
                    fontFamily="inherit"
                  >
                    3 / 12 files · in progress
                  </text>
                )}
              </g>
            );
          })}

          {/* Gold star */}
          {(() => {
            const starY = START_Y + levels.length * NODE_GAP + 24;
            const starX = CANVAS_W / 2;
            return (
              <g>
                {levels.length > 0 && (
                  <path
                    d={`M ${nodePositions[levels.length - 1].x} ${nodePositions[levels.length - 1].y} C ${nodePositions[levels.length - 1].x} ${nodePositions[levels.length - 1].y + 50} ${starX} ${starY - 50} ${starX} ${starY}`}
                    stroke="rgba(245,158,11,0.2)"
                    strokeWidth="1.5"
                    strokeDasharray="4 5"
                    fill="none"
                  />
                )}
                <circle
                  cx={starX}
                  cy={starY}
                  r={34}
                  fill="url(#amGold)"
                  stroke="rgba(245,158,11,0.5)"
                  strokeWidth="2"
                  filter="url(#amg4)"
                />
                <text
                  x={starX}
                  y={starY + 2}
                  textAnchor="middle"
                  dominantBaseline="middle"
                  fontSize="20"
                >
                  ⭐
                </text>
                <text
                  x={starX}
                  y={starY + 52}
                  textAnchor="middle"
                  fontSize="13"
                  fontWeight="700"
                  fill="#f59e0b"
                  fontFamily="inherit"
                >
                  Onboarding complete
                </text>
                <text
                  x={starX}
                  y={starY + 68}
                  textAnchor="middle"
                  fontSize="10"
                  fill="rgba(255,255,255,0.28)"
                  fontFamily="inherit"
                >
                  You&apos;re ready to ship code
                </text>
              </g>
            );
          })()}
        </svg>
      </div>
    </div>
  );
}

// Made with Bob
