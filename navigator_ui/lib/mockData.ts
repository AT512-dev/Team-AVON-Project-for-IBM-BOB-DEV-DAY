// Compass AI - Mock Data

import { Module } from "@/components/layout/LeftPanelModules";
import {
  ConstellationNode,
  ConstellationEdge,
  LevelNode,
  VisualizationStats,
  ChatMessage,
  BobStatus,
} from "@/types";

// ── Modules ──────────────────────────────────────────────────────────────────
export const mockModules: Module[] = [
  {
    id: "auth",
    name: "AUTH",
    fileCount: 12,
    color: "#06b6d4",
    iconLetter: "A",
  },
  { id: "api", name: "API", fileCount: 34, color: "#6d5ce7", iconLetter: "A" },
  {
    id: "database",
    name: "DATABASE",
    fileCount: 18,
    color: "#f59e0b",
    iconLetter: "D",
  },
  { id: "ui", name: "UI", fileCount: 67, color: "#ec4899", iconLetter: "U" },
  {
    id: "payments",
    name: "PAYMENTS",
    fileCount: 23,
    color: "#f97316",
    iconLetter: "P",
  },
  {
    id: "analytics",
    name: "ANALYTICS",
    fileCount: 9,
    color: "#10b981",
    iconLetter: "A",
  },
];

// ── All-modules constellation ─────────────────────────────────────────────────
export const mockConstellationNodes: ConstellationNode[] = [
  {
    id: "auth",
    fileName: "AUTH",
    position: { x: 120, y: 80 },
    color: "purple",
    dependencies: ["api"],
  },
  {
    id: "api",
    fileName: "API",
    position: { x: 520, y: 120 },
    color: "yellow",
    dependencies: ["database"],
  },
  {
    id: "database",
    fileName: "DATABASE",
    position: { x: 600, y: 340 },
    color: "green",
    dependencies: [],
  },
  {
    id: "ui",
    fileName: "UI",
    position: { x: 340, y: 400 },
    color: "yellow",
    dependencies: ["api", "auth"],
  },
  {
    id: "payments",
    fileName: "PAYMENTS",
    position: { x: 580, y: 560 },
    color: "green",
    dependencies: ["api"],
  },
  {
    id: "analytics",
    fileName: "ANALYTICS",
    position: { x: 140, y: 520 },
    color: "green",
    dependencies: ["database"],
  },
];

export const mockConstellationEdges: ConstellationEdge[] = [
  { id: "e1", source: "auth", target: "api", type: "dependency" },
  { id: "e2", source: "api", target: "database", type: "dependency" },
  { id: "e3", source: "ui", target: "api", type: "dependency" },
  { id: "e4", source: "ui", target: "auth", type: "dependency" },
  { id: "e5", source: "payments", target: "api", type: "dependency" },
  { id: "e6", source: "analytics", target: "database", type: "dependency" },
];

// ── AUTH constellation (drill-down) ──────────────────────────────────────────
// purple = done, yellow = current (YOU ARE HERE), green = locked
export const mockAuthConstellationNodes: ConstellationNode[] = [
  {
    id: "jwt",
    fileName: "jwt.ts",
    position: { x: 180, y: 80 },
    color: "purple",
    dependencies: [],
  },
  {
    id: "login",
    fileName: "login.ts",
    position: { x: 380, y: 140 },
    color: "purple",
    dependencies: ["jwt"],
  },
  {
    id: "session",
    fileName: "session.ts",
    position: { x: 140, y: 240 },
    color: "purple",
    dependencies: ["login"],
  },
  {
    id: "middleware",
    fileName: "middleware.ts",
    position: { x: 320, y: 300 },
    color: "yellow",
    dependencies: ["session", "jwt", "login"],
  },
  {
    id: "password",
    fileName: "password.ts",
    position: { x: 480, y: 260 },
    color: "green",
    dependencies: ["middleware"],
  },
  {
    id: "oauth",
    fileName: "oauth.ts",
    position: { x: 220, y: 400 },
    color: "green",
    dependencies: ["middleware"],
  },
  {
    id: "refresh",
    fileName: "refresh.ts",
    position: { x: 440, y: 400 },
    color: "green",
    dependencies: ["middleware"],
  },
  {
    id: "signup",
    fileName: "signup.ts",
    position: { x: 100, y: 500 },
    color: "green",
    dependencies: [],
  },
  {
    id: "audit",
    fileName: "audit.ts",
    position: { x: 520, y: 120 },
    color: "green",
    dependencies: [],
  },
  {
    id: "permissions",
    fileName: "permissions.ts",
    position: { x: 60, y: 180 },
    color: "green",
    dependencies: [],
  },
  {
    id: "tokens",
    fileName: "tokens.ts",
    position: { x: 580, y: 280 },
    color: "green",
    dependencies: [],
  },
  {
    id: "recovery",
    fileName: "recovery.ts",
    position: { x: 500, y: 500 },
    color: "green",
    dependencies: [],
  },
];

export const mockAuthConstellationEdges: ConstellationEdge[] = [
  { id: "ae1", source: "jwt", target: "middleware", type: "dependency" },
  { id: "ae2", source: "login", target: "middleware", type: "dependency" },
  { id: "ae3", source: "session", target: "middleware", type: "dependency" },
  { id: "ae4", source: "middleware", target: "password", type: "dependency" },
  { id: "ae5", source: "middleware", target: "oauth", type: "dependency" },
  { id: "ae6", source: "middleware", target: "refresh", type: "dependency" },
  { id: "ae7", source: "jwt", target: "login", type: "dependency" },
  { id: "ae8", source: "login", target: "session", type: "dependency" },
];

// ── All-modules level map ─────────────────────────────────────────────────────
export const mockLevelNodes: LevelNode[] = [
  {
    id: "level-1",
    level: 1,
    fileName: "AUTH",
    description: "12 files",
    difficulty: "LOW",
    isCompleted: false,
    dependencies: [],
  },
  {
    id: "level-2",
    level: 2,
    fileName: "API",
    description: "34 files",
    difficulty: "MED",
    isCompleted: false,
    dependencies: ["AUTH"],
  },
  {
    id: "level-3",
    level: 3,
    fileName: "DATABASE",
    description: "18 files",
    difficulty: "MED",
    isCompleted: false,
    dependencies: ["API"],
  },
  {
    id: "level-4",
    level: 4,
    fileName: "UI",
    description: "67 files",
    difficulty: "HIGH",
    isCompleted: false,
    dependencies: ["DATABASE"],
  },
  {
    id: "level-5",
    level: 5,
    fileName: "PAYMENTS",
    description: "23 files",
    difficulty: "MED",
    isCompleted: false,
    dependencies: ["UI"],
  },
  {
    id: "level-6",
    level: 6,
    fileName: "ANALYTICS",
    description: "9 files",
    difficulty: "LOW",
    isCompleted: false,
    dependencies: ["PAYMENTS"],
  },
];

// ── AUTH level map (drill-down) ───────────────────────────────────────────────
export const mockAuthLevelNodes: LevelNode[] = [
  {
    id: "auth-1",
    level: 1,
    fileName: "jwt.ts",
    description: "Token signing & verification",
    difficulty: "LOW",
    isCompleted: true,
    dependencies: [],
  },
  {
    id: "auth-2",
    level: 2,
    fileName: "login.ts",
    description: "Login handler",
    difficulty: "LOW",
    isCompleted: true,
    dependencies: ["jwt.ts"],
  },
  {
    id: "auth-3",
    level: 3,
    fileName: "session.ts",
    description: "Session management",
    difficulty: "MED",
    isCompleted: true,
    dependencies: ["login.ts"],
  },
  {
    id: "auth-4",
    level: 4,
    fileName: "middleware.ts",
    description: "~15 min",
    difficulty: "HIGH",
    isCompleted: false,
    dependencies: ["session.ts"],
  },
  {
    id: "auth-5",
    level: 5,
    fileName: "password.ts",
    description: "Password hashing & reset",
    difficulty: "MED",
    isCompleted: false,
    dependencies: ["middleware.ts"],
  },
  {
    id: "auth-6",
    level: 6,
    fileName: "oauth.ts",
    description: "OAuth2 flow",
    difficulty: "HIGH",
    isCompleted: false,
    dependencies: ["password.ts"],
  },
  {
    id: "auth-7",
    level: 7,
    fileName: "audit.ts",
    description: "Audit logging",
    difficulty: "LOW",
    isCompleted: false,
    dependencies: ["oauth.ts"],
  },
];

// ── Stats ─────────────────────────────────────────────────────────────────────
export const mockVisualizationStats: VisualizationStats = {
  filesFound: 247,
  criticalPaths: 6,
  completionPercentage: 8,
};

// ── Chat Messages ─────────────────────────────────────────────────────────────
export const mockChatMessages: ChatMessage[] = [
  {
    id: "1",
    sender: "bob",
    content:
      "I've mapped out the authentication flow. authMiddleware.js is the core logic you should start with.",
    timestamp: new Date(Date.now() - 300000), // 5 min ago
    codeBlock: {
      language: "javascript",
      code: `const verifyToken = (req, res) => {
  try {
    // Decrypt handshake...
    verify(req.headers.auth);
  } catch (err) { ... }
}`,
    },
  },
  {
    id: "2",
    sender: "user",
    content: "Explain the link between authMiddleware and config.",
    timestamp: new Date(Date.now() - 240000), // 4 min ago
  },
  {
    id: "3",
    sender: "bob",
    content:
      "authMiddleware imports configuration settings from config.js for JWT secret keys and token expiration times.",
    timestamp: new Date(Date.now() - 180000), // 3 min ago
  },
];

export const mockBobStatus: BobStatus = {
  isConnected: true,
  isTyping: false,
  status: "active",
};
