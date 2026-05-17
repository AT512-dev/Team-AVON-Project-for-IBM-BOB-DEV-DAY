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
import FileDetailView from "@/components/visualizations/FileDetailView";
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

// Define a local interface matching what ConstellationMap expects
interface ConstellationEdge {
  id: string;
  source: string;
  target: string;
  type?: string;
}

// Helper to map UIFileEdge[] → ConstellationEdge[]
function mapEdges(edges: UIFileEdge[]): ConstellationEdge[] {
  return edges.map((edge) => ({
    id: `e_${edge.from}_to_${edge.to}`,
    source: edge.from,
    target: edge.to,
    type: "smoothstep",
  }));
}

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

  // ── File/Folder detail view ───────────────────────────────────────────────
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

  const sidebarModules = dynamicModules ?? mockModules;

  // ── Module select → fetch module-specific roadmap ─────────────────────────
  const handleModuleSelect = useCallback(async (moduleId: string | null) => {
    setSelectedModule(moduleId);
    setSelectedNode(null);
    setSelectedFilePath(null); // clear detail view when switching modules
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

  const levelNodes = selectedModule
    ? (levelNodesFromModule ?? [])
    : (levelNodesFromInitial ?? mockLevelNodes);

  const constellationFileNodes = selectedModule
    ? (moduleFileNodes ?? [])
    : (initialNodes ?? []);

  // ── Map UIFileEdge[] → ConstellationEdge[] for both contexts ─────────────
  const constellationFileEdges: ConstellationEdge[] = mapEdges(
    selectedModule ? (moduleFileEdges ?? []) : (initialEdges ?? []),
  );

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

  return (
    <DashboardLayout>
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
          repoFiles={repoFiles.map((file) => ({
            ...file,
            path: file.path,
          }))}
          modules={sidebarModules}
          selectedModule={selectedModule}
          onModuleSelect={handleModuleSelect}
          totalFiles={repoFiles.length || constellationFileNodes?.length || 0}
          completedFiles={
            constellationFileNodes?.filter((n) => n.status === "done").length ??
            0
          }
          userName="Ali Jan"
          userInitials="AJ"
          userRole="Frontend Engineer"
          userDays={1}
        />

        <CenterPanel>
          {selectedFilePath ? (
            <FileDetailView
              selectedPath={selectedFilePath}
              repoFiles={repoFiles}
              onClose={() => {
                setSelectedFilePath(null);
                setSelectedNode(null); // keep both in sync on close
              }}
              onFileSelect={setSelectedFilePath}
              moduleContext={selectedModule}
            />
          ) : (
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
                  nodes={constellationFileNodes}
                  edges={constellationFileEdges}
                  onNodeClick={(nodeId) => {
                    if (!selectedModule) {
                      // Top-level: clicking a cluster star drills into that module
                      handleModuleSelect(nodeId);
                    } else {
                      // Module view: clicking a file star opens FileDetailView
                      setSelectedNode(nodeId);
                      setSelectedFilePath(nodeId); // ← THE FIX
                    }
                  }}
                  selectedNode={selectedNode}
                  onViewChange={setCurrentView}
                  selectedModule={selectedModule}
                  onModuleChange={handleModuleSelect}
                  moduleFileNodes={constellationFileNodes}
                  moduleFileEdges={constellationFileEdges}
                  availableModules={sidebarModules.map((m) => ({
                    id: m.id,
                    name: m.name,
                  }))}
                />
              ) : (
                <GameLevelMap
                  levels={levelNodes}
                  onLevelClick={(nodeId) => {
                    setSelectedNode(nodeId);
                    setSelectedFilePath(nodeId); // also wire level map clicks
                  }}
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
