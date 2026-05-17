"use client";

import React from "react";
import { GameLevelMapProps, ViewType } from "@/types";
import AllModulesLevelMap from "./AllModulesLevelMap";
import ModuleLevelMap from "./ModuleLevelMap";
import { getMockLevelNodes } from "@/lib/mockData";

interface Props extends GameLevelMapProps {
  onViewChange?: (view: ViewType) => void;
  selectedModule?: string | null;
  onModuleChange?: (moduleId: string | null) => void;
}

export default function GameLevelMap({
  levels,
  onLevelClick,
  onViewChange,
  selectedModule,
  onModuleChange,
}: Props) {
  if (!selectedModule) {
    return (
      <AllModulesLevelMap
        levels={levels}
        onViewChange={onViewChange}
        onModuleSelect={(moduleId) => onModuleChange?.(moduleId)}
        onModuleChange={onModuleChange}
      />
    );
  }

  const moduleLevels =
    levels.length > 0 ? levels : getMockLevelNodes(selectedModule);

  return (
    <ModuleLevelMap
      levels={moduleLevels}
      selectedModule={selectedModule}
      onLevelClick={onLevelClick}
      onViewChange={onViewChange}
      onModuleChange={onModuleChange}
    />
  );
}

// Made with Bob
