// Compass AI - TypeScript Type Definitions
import type { UIFileNode, UIFileEdge } from "@/lib/api";

export interface FileNode {
  id: string;
  name: string;
  type: "file" | "folder";
  extension?: string;
  badge?: "I" | "II" | "III";
  children?: FileNode[];
  isExpanded?: boolean;
}

export type ViewType = "constellation" | "levelMap";

export interface VisualizationStats {
  filesFound: number;
  criticalPaths: number;
  completionPercentage: number;
}

export type NodeColor = "yellow" | "purple" | "green";

export interface ConstellationNode {
  id: string;
  fileName: string;
  position: { x: number; y: number };
  color: NodeColor;
  dependencies: string[];
}

export interface ConstellationEdge {
  id: string;
  source: string;
  target: string;
  type: "dependency";
}

export type DifficultyLevel = "LOW" | "MED" | "HIGH";

export interface LevelNode {
  id: string;
  level: number;
  fileName: string;
  description: string;
  difficulty: DifficultyLevel;
  isCompleted: boolean;
  codePreview?: string;
  dependencies?: string[];
}

export type MessageSender = "user" | "bob";
export type BobStatusType = "active" | "idle" | "thinking";
export interface CodeBlock {
  language: string;
  code: string;
}

export interface ChatMessage {
  id: string;
  sender: MessageSender;
  content: string;
  timestamp: Date;
  codeBlock?: CodeBlock;
}

export interface BobStatus {
  isConnected: boolean;
  isTyping: boolean;
  status: BobStatusType;
}

export interface AppState {
  selectedFile: string | null;
  currentView: ViewType;
  chatMessages: ChatMessage[];
  fileTree: FileNode[];
  constellationNodes: ConstellationNode[];
  constellationEdges: ConstellationEdge[];
  levelNodes: LevelNode[];
  visualizationStats: VisualizationStats;
  bobStatus: BobStatus;
}

export interface DashboardLayoutProps {
  children?: React.ReactNode;
}

export interface FileTreeProps {
  files: FileNode[];
  selectedFile: string | null;
  onFileSelect: (fileId: string) => void;
}

// Simplified — container is now just a pass-through wrapper
export interface VisualizationContainerProps {
  currentView: ViewType;
  onViewChange: (view: ViewType) => void;
  stats: VisualizationStats;
  selectedModule?: string | null;
}

export interface ConstellationMapProps {
  nodes: ConstellationNode[];
  edges: ConstellationEdge[];
  onNodeClick: (nodeId: string) => void;
  selectedNode: string | null;
  onViewChange?: (view: ViewType) => void;
  selectedModule?: string | null;
  onModuleChange?: (moduleId: string | null) => void;
  moduleFileNodes?: UIFileNode[];
  moduleFileEdges?: UIFileEdge[];
}

export interface GameLevelMapProps {
  levels: LevelNode[];
  onLevelClick: (levelId: string) => void;
  selectedLevel: string | null;
  onViewChange?: (view: ViewType) => void;
  selectedModule?: string | null;
  onModuleChange?: (moduleId: string | null) => void;
}

export interface BobChatPanelProps {
  messages: ChatMessage[];
  bobStatus: BobStatus;
  onSendMessage: (message: string) => void;
  completionPercentage: number;
}

export interface TopNavBarProps {
  onAnalyze: () => Promise<void>;
  isConnected: boolean;
  selectedModule?: string | null;
}
