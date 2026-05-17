"use client";

import React from "react";
import { GameLevelMapProps, ViewType } from "@/types";

const BG_STARS = Array.from({ length: 50 }, (_, i) => ({
  x: ((i * 137 + 50) % 720) + 20,
  y: ((i * 97 + 30) % 620) + 20,
  r: i % 7 === 0 ? 1.5 : i % 3 === 0 ? 1 : 0.5,
  o: 0.1 + (i % 5) * 0.04,
}));

// Colors per module (for all-modules level map circles)
const MODULE_COLORS: Record<
  string,
  { border: string; text: string; bg: string }
> = {
  AUTH: { border: "#06b6d4", text: "#06b6d4", bg: "rgba(6,182,212,0.15)" },
  API: { border: "#6d5ce7", text: "#a78bfa", bg: "rgba(109,92,231,0.12)" },
  DATABASE: { border: "#92400e", text: "#d97706", bg: "rgba(146,64,14,0.12)" },
  UI: { border: "#6d5ce7", text: "#a78bfa", bg: "rgba(109,92,231,0.12)" },
  PAYMENTS: { border: "#92400e", text: "#d97706", bg: "rgba(146,64,14,0.12)" },
  ANALYTICS: { border: "#475569", text: "#94a3b8", bg: "rgba(71,85,105,0.1)" },
};

interface Props extends GameLevelMapProps {
  onViewChange?: (view: ViewType) => void;
  selectedModule?: string | null;
  onModuleChange?: (moduleId: string | null) => void;
}

export default function GameLevelMap({
  levels,
  onLevelClick,
  selectedLevel,
  onViewChange,
  selectedModule,
  onModuleChange,
}: Props) {
  const isModuleView = !!selectedModule;
  const currentIndex = levels.findIndex((l) => !l.isCompleted);
  const completedCount = levels.filter((l) => l.isCompleted).length;
  const progressPct = Math.round((completedCount / levels.length) * 100);

  // Zigzag: even index = left side, odd = right side
  const isLeft = (i: number) => i % 2 === 0;

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        position: "relative",
        overflow: "auto",
        background:
          "radial-gradient(ellipse at 50% 20%, #1e2a5e 0%, #12184a 25%, #0d1117 65%)",
        userSelect: "none",
      }}
    >
      {/* BG stars */}
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

      {/* ── Top bar ── */}
      <div
        style={{
          position: "sticky",
          top: 0,
          left: 0,
          right: 0,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "12px 18px",
          zIndex: 20,
          background: "rgba(13,17,23,0.6)",
          backdropFilter: "blur(10px)",
          borderBottom: "1px solid rgba(255,255,255,0.05)",
        }}
      >
        {/* Left breadcrumb */}
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <button
            onClick={() => onModuleChange?.(null)}
            style={{
              background: "rgba(255,255,255,0.06)",
              border: "1px solid rgba(255,255,255,0.1)",
              borderRadius: 7,
              padding: "5px 10px",
              color: "rgba(255,255,255,0.6)",
              fontSize: 12,
              cursor: "pointer",
              fontFamily: "inherit",
            }}
          >
            All modules
          </button>
          {isModuleView && (
            <>
              <span style={{ color: "rgba(255,255,255,0.3)", fontSize: 12 }}>
                ›
              </span>
              <div
                style={{
                  background: "rgba(255,255,255,0.08)",
                  border: "1px solid rgba(255,255,255,0.15)",
                  borderRadius: 7,
                  padding: "5px 10px",
                  color: "rgba(255,255,255,0.9)",
                  fontSize: 12,
                  fontWeight: 600,
                }}
              >
                {selectedModule.toUpperCase()}
              </div>
            </>
          )}
        </div>

        {/* Center toggle */}
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
              <circle cx="12" cy="12" r="2.5" fill="rgba(255,255,255,0.35)" />
              <circle cx="4" cy="5" r="1.5" fill="rgba(255,255,255,0.25)" />
              <circle cx="20" cy="5" r="1.5" fill="rgba(255,255,255,0.25)" />
              <circle cx="4" cy="19" r="1.5" fill="rgba(255,255,255,0.25)" />
              <circle cx="20" cy="19" r="1.5" fill="rgba(255,255,255,0.25)" />
            </svg>
            <span style={{ fontSize: 12, color: "rgba(255,255,255,0.4)" }}>
              Constellation
            </span>
          </button>
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

        {/* Right: progress */}
        {isModuleView && (
          <div
            style={{
              background: "rgba(255,255,255,0.05)",
              border: "1px solid rgba(255,255,255,0.1)",
              borderRadius: 8,
              padding: "6px 12px",
              textAlign: "right",
            }}
          >
            <div style={{ fontSize: 11, color: "rgba(255,255,255,0.5)" }}>
              {selectedModule.toUpperCase()} onboarding
              <span style={{ color: "rgba(255,255,255,0.8)", fontWeight: 600 }}>
                {" "}
                3 / 8 lessons
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
                    width: "37%",
                    height: "100%",
                    background: "linear-gradient(90deg,#06b6d4,#6d5ce7)",
                    borderRadius: 99,
                  }}
                />
              </div>
              <span style={{ fontSize: 11, fontWeight: 700, color: "#06b6d4" }}>
                37%
              </span>
            </div>
          </div>
        )}
        {!isModuleView && <div style={{ width: 80 }} />}
      </div>

      {/* ── Level nodes ── */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          padding: "40px 0 80px",
          position: "relative",
          zIndex: 1,
        }}
      >
        <div style={{ width: "100%", maxWidth: 520, position: "relative" }}>
          {levels.map((level, index) => {
            const isDone = level.isCompleted;
            const isCurrent = index === currentIndex;
            const isLocked = !isDone && !isCurrent;
            const onLeft = isLeft(index);

            // Circle size
            const circleSize = isCurrent ? 80 : isDone ? 72 : 52;

            // Circle style
            let circleBg = "rgba(255,255,255,0.04)";
            let circleBorder = "rgba(255,255,255,0.15)";
            let circleGlow = "none";
            let circleText = "rgba(255,255,255,0.25)";
            let labelColor = "rgba(255,255,255,0.3)";

            if (isDone) {
              circleBg = "rgba(16,185,129,0.12)";
              circleBorder = "#10b981";
              circleGlow =
                "0 0 24px rgba(16,185,129,0.4), 0 0 48px rgba(16,185,129,0.15)";
              circleText = "#10b981";
              labelColor = "#10b981";
            } else if (isCurrent) {
              circleBg = "rgba(6,182,212,0.15)";
              circleBorder = "#06b6d4";
              circleGlow =
                "0 0 30px rgba(6,182,212,0.55), 0 0 60px rgba(6,182,212,0.2)";
              circleText = "#06b6d4";
              labelColor = "#06b6d4";
            } else if (!isModuleView) {
              // All-modules: use module-specific colors
              const mc =
                MODULE_COLORS[level.fileName] ?? MODULE_COLORS["ANALYTICS"];
              circleBg = mc.bg;
              circleBorder = mc.border;
              circleText = mc.text;
              labelColor = mc.text;
            }

            return (
              <div key={level.id}>
                {/* Node row */}
                <div
                  style={{
                    display: "flex",
                    justifyContent: onLeft ? "flex-start" : "flex-end",
                    paddingLeft: onLeft ? "8%" : 0,
                    paddingRight: onLeft ? 0 : "8%",
                    position: "relative",
                  }}
                >
                  <div
                    onClick={() => !isLocked && onLevelClick(level.id)}
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "center",
                      cursor: isLocked ? "default" : "pointer",
                    }}
                  >
                    {/* YOU'RE HERE label */}
                    {isCurrent && (
                      <div
                        style={{
                          fontSize: 9,
                          fontWeight: 700,
                          letterSpacing: "0.15em",
                          color: "#06b6d4",
                          marginBottom: 6,
                          textTransform: "uppercase",
                        }}
                      >
                        YOU&apos;RE HERE
                      </div>
                    )}

                    {/* Circle */}
                    <div
                      style={{
                        width: circleSize,
                        height: circleSize,
                        borderRadius: "50%",
                        background: circleBg,
                        border: `2px solid ${circleBorder}`,
                        boxShadow: circleGlow,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        position: "relative",
                        transition: "all 0.3s",
                      }}
                    >
                      {/* Pulse ring */}
                      {isCurrent && (
                        <div
                          style={{
                            position: "absolute",
                            inset: -10,
                            borderRadius: "50%",
                            border: "1px solid rgba(6,182,212,0.2)",
                            animation: "glmPulse 2s ease-in-out infinite",
                          }}
                        />
                      )}

                      {isDone ? (
                        <svg
                          width={circleSize * 0.45}
                          height={circleSize * 0.45}
                          viewBox="0 0 24 24"
                          fill="none"
                        >
                          <path
                            d="M5 12L10 17L19 7"
                            stroke="#10b981"
                            strokeWidth="2.5"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                          />
                        </svg>
                      ) : (
                        <span
                          style={{
                            fontSize: isCurrent ? 28 : isLocked ? 16 : 20,
                            fontWeight: 700,
                            color: circleText,
                          }}
                        >
                          {level.level}
                        </span>
                      )}
                    </div>

                    {/* Module name + sub */}
                    <div style={{ marginTop: 10, textAlign: "center" }}>
                      <div
                        style={{
                          fontSize: isCurrent || isDone ? 14 : 12,
                          fontWeight: 600,
                          color: labelColor,
                          letterSpacing: "0.05em",
                          fontFamily: isModuleView ? "monospace" : "inherit",
                        }}
                      >
                        {level.fileName}
                      </div>
                      {!isModuleView && (
                        <div
                          style={{
                            fontSize: 11,
                            color: "rgba(255,255,255,0.3)",
                            marginTop: 3,
                          }}
                        >
                          {level.description}
                        </div>
                      )}
                      {isCurrent && isModuleView && (
                        <div
                          style={{
                            fontSize: 10,
                            color: "#06b6d4",
                            marginTop: 3,
                            letterSpacing: "0.08em",
                          }}
                        >
                          YOU&apos;RE HERE
                        </div>
                      )}
                      {isCurrent && !isModuleView && (
                        <div
                          style={{
                            fontSize: 10,
                            color: "#06b6d4",
                            marginTop: 2,
                          }}
                        >
                          3 / 12 files · in progress
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Connector to next */}
                {index < levels.length - 1 && (
                  <div
                    style={{
                      display: "flex",
                      justifyContent: onLeft ? "flex-end" : "flex-start",
                      paddingLeft: onLeft ? 0 : "14%",
                      paddingRight: onLeft ? "14%" : 0,
                      margin: "10px 0",
                    }}
                  >
                    <svg
                      width={100}
                      height={36}
                      viewBox="0 0 100 36"
                      fill="none"
                    >
                      <path
                        d={
                          onLeft
                            ? "M 85 4 Q 50 18 15 32"
                            : "M 15 4 Q 50 18 85 32"
                        }
                        stroke={
                          isDone
                            ? "rgba(6,182,212,0.4)"
                            : "rgba(255,255,255,0.12)"
                        }
                        strokeWidth="1.5"
                        strokeDasharray={isDone ? "none" : "4 5"}
                        fill="none"
                      />
                    </svg>
                  </div>
                )}
              </div>
            );
          })}

          {/* ── Bottom star ── */}
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              marginTop: 20,
            }}
          >
            <div
              style={{
                width: 72,
                height: 72,
                borderRadius: "50%",
                background: "radial-gradient(circle, #f59e0b, #b45309)",
                boxShadow:
                  "0 0 28px rgba(245,158,11,0.5), 0 0 56px rgba(245,158,11,0.2)",
                border: "2px solid rgba(245,158,11,0.6)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <span style={{ fontSize: 28 }}>⭐</span>
            </div>
            <div style={{ marginTop: 10, textAlign: "center" }}>
              <div style={{ fontSize: 15, fontWeight: 700, color: "#f59e0b" }}>
                {isModuleView
                  ? `${selectedModule.toUpperCase()} Mastery`
                  : "Onboarding complete"}
              </div>
              <div
                style={{
                  fontSize: 11,
                  color: "rgba(255,255,255,0.3)",
                  marginTop: 4,
                }}
              >
                You&apos;re ready to ship code
              </div>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes glmPulse {
          0%,100% { transform:scale(1); opacity:0.4; }
          50% { transform:scale(1.3); opacity:0; }
        }
      `}</style>
    </div>
  );
}

// Made with Bob
