"use client";

import React, { useState } from "react";
import DashboardLayout from "@/components/layout/DashboardLayout";
import LeftPanelModules from "@/components/layout/LeftPanelModules";
import CenterPanel from "@/components/layout/CenterPanel";
import RightPanel from "@/components/layout/RightPanel";
import VisualizationContainer from "@/components/visualizations/VisualizationContainer";
import ConstellationMap from "@/components/visualizations/ConstellationMap";
import GameLevelMap from "@/components/visualizations/GameLevelMap";
import BobChatPanel from "@/components/chat/BobChatPanel";
import {
  mockModules,
  mockConstellationNodes,
  mockConstellationEdges,
  mockAuthConstellationNodes,
  mockAuthConstellationEdges,
  mockLevelNodes,
  mockAuthLevelNodes,
  mockVisualizationStats,
} from "@/lib/mockData";
import { ViewType } from "@/types";

export default function Home() {
  const [selectedModule, setSelectedModule] = useState<string | null>(null);
  const [currentView, setCurrentView] = useState<ViewType>("constellation");
  const [selectedNode, setSelectedNode] = useState<string | null>(null);

  const handleModuleSelect = (moduleId: string | null) => {
    setSelectedModule(moduleId);
    setSelectedNode(null);
  };

  const constellationNodes =
    selectedModule === "auth"
      ? mockAuthConstellationNodes
      : mockConstellationNodes;
  const constellationEdges =
    selectedModule === "auth"
      ? mockAuthConstellationEdges
      : mockConstellationEdges;
  const levelNodes =
    selectedModule === "auth" ? mockAuthLevelNodes : mockLevelNodes;

  return (
    <DashboardLayout>
      <div className="flex-1 flex overflow-hidden">
        <LeftPanelModules
          modules={mockModules}
          selectedModule={selectedModule}
          onModuleSelect={handleModuleSelect}
        />

        <CenterPanel>
          <VisualizationContainer
            currentView={currentView}
            onViewChange={setCurrentView}
            stats={mockVisualizationStats}
            selectedModule={selectedModule}
          >
            {currentView === "constellation" ? (
              <ConstellationMap
                nodes={constellationNodes}
                edges={constellationEdges}
                onNodeClick={setSelectedNode}
                selectedNode={selectedNode}
                onViewChange={setCurrentView}
                selectedModule={selectedModule}
                onModuleChange={handleModuleSelect}
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
        </CenterPanel>

        <RightPanel>
          <BobChatPanel
            selectedModule={selectedModule}
            selectedFile={selectedNode}
          />
        </RightPanel>
      </div>
    </DashboardLayout>
  );
}

// Made with Bob
