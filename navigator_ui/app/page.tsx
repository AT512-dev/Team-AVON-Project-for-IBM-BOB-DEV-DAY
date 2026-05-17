"use client";

import React, { useState, useEffect, useCallback } from "react";
import LandingPage from "@/components/visualizations/LandingPage";
import DashboardLayout from "@/components/layout/DashboardLayout";
import LeftPanelModules from "@/components/layout/LeftPanelModules";
import CenterPanel from "@/components/layout/CenterPanel";
import RightPanel from "@/components/layout/RightPanel";
import VisualizationContainer from "@/components/visualizations/VisualizationContainer";
import ConstellationMap from "@/components/visualizations/ConstellationMap";
import GameLevelMap from "@/components/visualizations/GameLevelMap";
import BobChatPanel from "@/components/chat/BobChatPanel";
import {
  checkHealth,
  fetchInitialRoadmap,
  fetchModuleRoadmap,
  setRepoUrl,
  UIFileNode,
  UIFileEdge,
  SimpleFile,
} from "@/lib/api";
import { mockModules, mockLevelNodes } from "@/lib/mockData";
import { ViewType, LevelNode } from "@/types";
import { Module } from "@/components/layout/LeftPanelModules";

const DEMO_REPO_URL =
  "https://github.com/AleyJan/vision-intelligence---techmesh-26";

export default function Home() {
  // ── Gate ──────────────────────────────────────────────────────────────────
  const [connected, setConnected] = useState(false);

  // ── Initial repo load ─────────────────────────────────────────────────────
  const [initialLoading, setInitialLoading] = useState(false);
  const [initialNodes, setInitialNodes] = useState<UIFileNode[] | null>(null);
  const [initialEdges, setInitialEdges] = useState<UIFileEdge[] | null>(null);
  const [repoFiles, setRepoFiles] = useState<SimpleFile[]>([]);

  // ── Module selection ──────────────────────────────────────────────────────
  const [selectedModule, setSelectedModule] = useState<string | null>(null);
  const [currentView, setCurrentView] = useState<ViewType>("constellation");
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [moduleFileNodes, setModuleFileNodes] = useState<UIFileNode[] | null>(
    null,
  );
  const [moduleFileEdges, setModuleFileEdges] = useState<UIFileEdge[] | null>(
    null,
  );
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  // ── File viewer state ─────────────────────────────────────────────────────
  const [fileViewMode, setFileViewMode] = useState(false);
  const [fileContent, setFileContent] = useState<string | null>(null);
  const [fileLoading, setFileLoading] = useState(false);
  const [selectedFilePath, setSelectedFilePath] = useState<string | null>(null);

  // ── Fetch initial roadmap when connected ──────────────────────────────────
  useEffect(() => {
    if (!connected) return;

    const init = async () => {
      const ok = await checkHealth();
      console.log(ok ? "✅ Backend connected" : "⚠️ Backend offline");
      if (!ok) return;

      setInitialLoading(true);
      console.log("🌐 Loading repo overview...");
      try {
        const result = await fetchInitialRoadmap();
        if (result) {
          setInitialNodes(result.nodes);
          setInitialEdges(result.edges);
          setRepoFiles(result.files);
          console.log(
            `✅ Dashboard loaded with ${result.files.length} real files`,
          );
        } else {
          console.warn("⚠️ Could not load repo overview — using mock data");
        }
      } finally {
        setInitialLoading(false);
      }
    };

    init();
  }, [connected]);

  // ── Elapsed timer ─────────────────────────────────────────────────────────
  useEffect(() => {
    if (!isLoading && !initialLoading) return;
    const interval = setInterval(() => setElapsedSeconds((s) => s + 1), 1000);
    return () => clearInterval(interval);
  }, [isLoading, initialLoading]);

  // ── Build dynamic modules from real file list ─────────────────────────────
  // Groups files by their top-level folder → shows as modules in sidebar
  const dynamicModules: Module[] | null =
    repoFiles.length > 0
      ? (() => {
          const folderMap = new Map<string, number>();
          repoFiles.forEach((f) => {
            const parts = f.path.split("/");
            const folder = parts.length > 1 ? parts[0] : "root";
            folderMap.set(folder, (folderMap.get(folder) ?? 0) + 1);
          });
          const colors = [
            "#06b6d4",
            "#6d5ce7",
            "#f59e0b",
            "#ec4899",
            "#f97316",
            "#10b981",
            "#a78bfa",
            "#ef4444",
          ];
          return Array.from(folderMap.entries()).map(([name, count], i) => ({
            id: name.toLowerCase().replace(/[^a-z0-9]/g, "_"),
            name: name.toUpperCase(),
            fileCount: count,
            color: colors[i % colors.length],
            iconLetter: name[0]?.toUpperCase() ?? "?",
          }));
        })()
      : null;

  // Use real modules if available, otherwise fall back to mock
  const sidebarModules = dynamicModules ?? mockModules;

  // ── Module select → fetch module-specific roadmap ─────────────────────────
  const handleModuleSelect = useCallback(async (moduleId: string | null) => {
    setSelectedModule(moduleId);
    setSelectedNode(null);
    setModuleFileNodes(null);
    setModuleFileEdges(null);
    setFetchError(null);
    setElapsedSeconds(0);

    if (!moduleId) return;

    setIsLoading(true);
    try {
      const result = await fetchModuleRoadmap(moduleId);
      if (result && result.nodes.length > 0) {
        setModuleFileNodes(result.nodes);
        setModuleFileEdges(result.edges);
      } else {
        setFetchError(
          result === null
            ? "IBM Bob / WatsonX timed out. Check backend terminal."
            : `Backend returned 0 files for ${moduleId.toUpperCase()}.`,
        );
        setModuleFileNodes([]);
        setModuleFileEdges([]);
      }
    } catch (err) {
      console.error("handleModuleSelect error:", err);
      setFetchError("Unexpected error. Check browser console.");
      setModuleFileNodes([]);
      setModuleFileEdges([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // ── Handle file node click → fetch file details from API ──────────────────
  const handleFileNodeClick = useCallback(
    async (filePath: string) => {
      console.log("📄 File clicked:", filePath);
      setSelectedFilePath(filePath);
      setFileViewMode(true);
      setFileLoading(true);
      setFileContent(null);

      try {
        const response = await fetch("http://localhost:8000/api/v1/ask", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            repo_path: DEMO_REPO_URL,
            question: `Show me the code and explain the file structure of ${filePath}`,
            current_file: filePath,
          }),
        });

        if (!response.ok) {
          throw new Error(`API responded with status ${response.status}`);
        }

        const data = await response.json();
        setFileContent(data.answer || "No content returned from API");
        console.log("✅ File content loaded");
      } catch (err) {
        console.error("❌ Error fetching file:", err);
        setFileContent(
          `Error loading file: ${err instanceof Error ? err.message : "Unknown error"}`
        );
      } finally {
        setFileLoading(false);
      }
    },
    []
  );

  // ── Handle back to map ────────────────────────────────────────────────────
  const handleBackToMap = useCallback(() => {
    setFileViewMode(false);
    setFileContent(null);
    setSelectedFilePath(null);
  }, []);

  // ── Derive level nodes ────────────────────────────────────────────────────
  const levelNodesFromModule: LevelNode[] | null =
    moduleFileNodes && moduleFileNodes.length > 0
      ? moduleFileNodes.map((n, i) => ({
          id: n.id,
          level: i + 1,
          fileName: n.label,
          description: n.objective,
          difficulty:
            n.complexity === "Easy"
              ? "LOW"
              : n.complexity === "Hard"
                ? "HIGH"
                : "MED",
          isCompleted: n.status === "done",
          dependencies: [],
        }))
      : null;

  const levelNodesFromInitial: LevelNode[] | null =
    initialNodes && initialNodes.length > 0
      ? initialNodes.map((n, i) => ({
          id: n.id,
          level: i + 1,
          fileName: n.label,
          description: n.objective,
          difficulty:
            n.complexity === "Easy"
              ? "LOW"
              : n.complexity === "Hard"
                ? "HIGH"
                : "MED",
          isCompleted: n.status === "done",
          dependencies: [],
        }))
      : null;

  // What to show in level map:
  // - Module selected → module-specific data
  // - No module → initial real data if loaded, else mock
  const levelNodes = selectedModule
    ? (levelNodesFromModule ?? [])
    : (levelNodesFromInitial ?? mockLevelNodes);

  // Constellation nodes:
  // - Module selected → module file nodes
  // - No module → initial real nodes if loaded, else nothing (uses cluster view)
  const constellationFileNodes = selectedModule
    ? (moduleFileNodes ?? undefined)
    : (initialNodes ?? undefined);

  const constellationFileEdges = selectedModule
    ? (moduleFileEdges ?? undefined)
    : (initialEdges ?? undefined);

  // ── Landing gate ──────────────────────────────────────────────────────────
  if (!connected) {
    return (
      <LandingPage
        onConnect={(url) => {
          const repoUrl = url?.trim() || DEMO_REPO_URL;
          setRepoUrl(repoUrl);
          setConnected(true);
          console.log("🚀 Starting with repo:", repoUrl);
        }}
      />
    );
  }

  // ── Dashboard ─────────────────────────────────────────────────────────────
  return (
    <DashboardLayout>
      {/* Initial loading overlay — shown while fetching repo on first load */}
      {initialLoading && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 9999,
            background: "rgba(10,13,26,0.95)",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            gap: 16,
          }}
        >
          <div
            style={{
              width: 48,
              height: 48,
              borderRadius: "50%",
              border: "3px solid rgba(6,182,212,0.15)",
              borderTop: "3px solid #06b6d4",
              animation: "spin 0.8s linear infinite",
            }}
          />
          <div style={{ color: "#06b6d4", fontSize: 16, fontWeight: 700 }}>
            IBM Bob is scanning the repository...
          </div>
          <div
            style={{
              color: "rgba(255,255,255,0.4)",
              fontSize: 12,
              textAlign: "center",
              lineHeight: 1.8,
            }}
          >
            WatsonX is analysing every file in your repo
            <br />
            This takes 1–2 minutes on first load
            <br />
            <span style={{ color: "rgba(255,255,255,0.22)" }}>
              {elapsedSeconds}s elapsed
            </span>
          </div>
          <div style={{ display: "flex", gap: 6, marginTop: 4 }}>
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: "50%",
                  background: "#06b6d4",
                  animation: `pulse 1.4s ease-in-out ${i * 0.2}s infinite`,
                }}
              />
            ))}
          </div>
          {repoFiles.length > 0 && (
            <div
              style={{
                fontSize: 11,
                color: "rgba(6,182,212,0.6)",
                marginTop: 8,
              }}
            >
              ✅ {repoFiles.length} files loaded so far...
            </div>
          )}
        </div>
      )}

      {/* Module loading overlay */}
      {isLoading && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 9999,
            background: "rgba(10,13,26,0.92)",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            gap: 16,
          }}
        >
          <div
            style={{
              width: 44,
              height: 44,
              borderRadius: "50%",
              border: "3px solid rgba(6,182,212,0.15)",
              borderTop: "3px solid #06b6d4",
              animation: "spin 0.8s linear infinite",
            }}
          />
          <div style={{ color: "#06b6d4", fontSize: 15, fontWeight: 700 }}>
            Loading {selectedModule?.toUpperCase()} module...
          </div>
          <div
            style={{
              color: "rgba(255,255,255,0.4)",
              fontSize: 12,
              textAlign: "center",
              lineHeight: 1.7,
            }}
          >
            WatsonX is generating the learning roadmap
            <br />
            <span style={{ color: "rgba(255,255,255,0.25)" }}>
              {elapsedSeconds}s elapsed · timeout at 120s
            </span>
          </div>
          <div style={{ display: "flex", gap: 6 }}>
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: "50%",
                  background: "#06b6d4",
                  animation: `pulse 1.4s ease-in-out ${i * 0.2}s infinite`,
                }}
              />
            ))}
          </div>
        </div>
      )}

      {/* Error toast */}
      {fetchError && !isLoading && (
        <div
          style={{
            position: "fixed",
            top: 16,
            left: "50%",
            transform: "translateX(-50%)",
            zIndex: 8888,
            background: "rgba(248,113,113,0.1)",
            border: "1px solid rgba(248,113,113,0.3)",
            borderRadius: 8,
            padding: "10px 20px",
            fontSize: 12,
            color: "#f87171",
            display: "flex",
            alignItems: "center",
            gap: 12,
            maxWidth: 520,
          }}
        >
          <span>⚠ {fetchError}</span>
          <button
            onClick={() => setFetchError(null)}
            style={{
              background: "transparent",
              border: "none",
              color: "#f87171",
              cursor: "pointer",
              fontSize: 18,
              padding: 0,
              lineHeight: 1,
            }}
          >
            ×
          </button>
        </div>
      )}

      <div className="flex-1 flex overflow-hidden">
        <LeftPanelModules
          modules={sidebarModules}
          selectedModule={selectedModule}
          onModuleSelect={handleModuleSelect}
          totalFiles={repoFiles.length || moduleFileNodes?.length || 0}
          completedFiles={
            moduleFileNodes?.filter((n) => n.status === "done").length ?? 0
          }
          userName="Ali Jan"
          userInitials="AJ"
          userRole="Frontend Engineer"
          userDays={1}
        />

        <CenterPanel>
          {fileViewMode ? (
            // ── FILE VIEWER PANEL ──
            <div
              style={{
                width: "100%",
                height: "100%",
                display: "flex",
                flexDirection: "column",
                background: "#0a0e1a",
                position: "relative",
              }}
            >
              {/* Header with back button */}
              <div
                style={{
                  padding: "16px 20px",
                  borderBottom: "1px solid rgba(255,255,255,0.06)",
                  background: "rgba(13,17,23,0.7)",
                  backdropFilter: "blur(12px)",
                  display: "flex",
                  alignItems: "center",
                  gap: 16,
                  position: "sticky",
                  top: 0,
                  zIndex: 10,
                }}
              >
                <button
                  onClick={handleBackToMap}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                    padding: "8px 16px",
                    background: "rgba(6,182,212,0.12)",
                    border: "1px solid rgba(6,182,212,0.3)",
                    borderRadius: 8,
                    color: "#06b6d4",
                    fontSize: 13,
                    fontWeight: 600,
                    cursor: "pointer",
                    transition: "all 0.2s",
                  }}
                  onMouseEnter={(e) => {
                    (e.currentTarget as HTMLButtonElement).style.background =
                      "rgba(6,182,212,0.18)";
                  }}
                  onMouseLeave={(e) => {
                    (e.currentTarget as HTMLButtonElement).style.background =
                      "rgba(6,182,212,0.12)";
                  }}
                >
                  <svg
                    width="14"
                    height="14"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M19 12H5M12 19l-7-7 7-7" />
                  </svg>
                  Back to Map
                </button>
                <div style={{ flex: 1 }}>
                  <div
                    style={{
                      fontSize: 14,
                      fontWeight: 600,
                      color: "rgba(255,255,255,0.85)",
                      fontFamily: "monospace",
                    }}
                  >
                    {selectedFilePath}
                  </div>
                  <div
                    style={{
                      fontSize: 11,
                      color: "rgba(255,255,255,0.35)",
                      marginTop: 2,
                    }}
                  >
                    {selectedModule?.toUpperCase()} module
                  </div>
                </div>
              </div>

              {/* Loading state */}
              {fileLoading && (
                <div
                  style={{
                    flex: 1,
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: 16,
                  }}
                >
                  <div
                    style={{
                      width: 44,
                      height: 44,
                      borderRadius: "50%",
                      border: "3px solid rgba(6,182,212,0.15)",
                      borderTop: "3px solid #06b6d4",
                      animation: "spin 0.8s linear infinite",
                    }}
                  />
                  <div
                    style={{
                      color: "#06b6d4",
                      fontSize: 14,
                      fontWeight: 600,
                    }}
                  >
                    IBM Bob is analyzing the file...
                  </div>
                  <div
                    style={{
                      color: "rgba(255,255,255,0.3)",
                      fontSize: 12,
                    }}
                  >
                    Fetching code and generating explanation
                  </div>
                </div>
              )}

              {/* File content */}
              {!fileLoading && fileContent && (
                <div
                  style={{
                    flex: 1,
                    overflow: "auto",
                    padding: "24px",
                  }}
                >
                  <div
                    style={{
                      background: "rgba(13,17,23,0.5)",
                      border: "1px solid rgba(255,255,255,0.08)",
                      borderRadius: 12,
                      padding: "20px",
                      fontFamily: "monospace",
                      fontSize: 13,
                      lineHeight: 1.7,
                      color: "rgba(255,255,255,0.85)",
                      whiteSpace: "pre-wrap",
                      wordBreak: "break-word",
                    }}
                  >
                    {fileContent}
                  </div>
                </div>
              )}
            </div>
          ) : (
            // ── NORMAL VISUALIZATION VIEW ──
            <VisualizationContainer
              currentView={currentView}
              onViewChange={setCurrentView}
              stats={{
                filesFound: repoFiles.length,
                criticalPaths: 0,
                completionPercentage: 0,
              }}
              selectedModule={selectedModule}
            >
              {currentView === "constellation" ? (
                <ConstellationMap
                  nodes={[]}
                  edges={[]}
                  onNodeClick={(nodeId) => {
                    if (!selectedModule) {
                      // No module selected → clicking a cluster selects that module
                      handleModuleSelect(nodeId);
                    } else {
                      // Module selected → clicking a file node opens file viewer
                      const clickedNode = moduleFileNodes?.find(
                        (n) => n.id === nodeId
                      );
                      if (clickedNode) {
                        // Use filePath instead of label for the full path
                        handleFileNodeClick(clickedNode.filePath);
                      } else {
                        setSelectedNode(nodeId);
                      }
                    }
                  }}
                  selectedNode={selectedNode}
                  onViewChange={setCurrentView}
                  selectedModule={selectedModule}
                  onModuleChange={handleModuleSelect}
                  moduleFileNodes={constellationFileNodes}
                  moduleFileEdges={constellationFileEdges}
                />
              ) : (
                <GameLevelMap
                  levels={levelNodes}
                  onLevelClick={setSelectedNode}
                  selectedLevel={selectedNode}
                  onViewChange={setCurrentView}
                  selectedModule={selectedModule}
                  onModuleChange={handleModuleSelect}
                />
              )}
            </VisualizationContainer>
          )}
        </CenterPanel>

        <RightPanel>
          <BobChatPanel
            selectedModule={selectedModule}
            selectedFile={selectedNode}
          />
        </RightPanel>
      </div>

      <style>{`
        @keyframes spin  { to { transform: rotate(360deg); } }
        @keyframes pulse { 0%,80%,100%{transform:scale(0.6);opacity:0.3} 40%{transform:scale(1);opacity:1} }
      `}</style>
    </DashboardLayout>
  );
}

