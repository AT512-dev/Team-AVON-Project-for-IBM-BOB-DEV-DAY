"use client";

import React from "react";
import { VisualizationContainerProps } from "@/types";
import FileDetailView from "@/components/visualizations/FileDetailView";
import { SimpleFile } from "@/lib/api";

interface ExtendedProps extends VisualizationContainerProps {
  children: React.ReactNode;
  // node/file selection
  selectedNode?: string | null;
  onNodeClose?: () => void;
  onFileSelect?: (path: string) => void;
  // repo files for FileDetailView
  repoFiles?: SimpleFile[];
  moduleContext?: string | null;
}

export default function VisualizationContainer({
  currentView,
  children,
  selectedNode,
  onNodeClose,
  onFileSelect,
  repoFiles = [],
  moduleContext,
}: ExtendedProps) {
  return (
    <div
      style={{
        height: "100%",
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
        position: "relative", // needed so FileDetailView absolute positioning works
      }}
    >
      {/* Main visualization (constellation or level map) */}
      <div style={{ flex: 1, position: "relative", overflow: "hidden" }}>
        {children}
      </div>

      {/* FileDetailView slides in over the top when a node is selected */}
      {selectedNode && (
        <FileDetailView
          selectedPath={selectedNode}
          repoFiles={repoFiles}
          onClose={() => onNodeClose?.()}
          onFileSelect={(path) => onFileSelect?.(path)}
          moduleContext={moduleContext}
        />
      )}
    </div>
  );
}

// Made with Bob
