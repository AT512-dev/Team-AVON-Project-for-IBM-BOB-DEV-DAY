// Compass AI - Mock / Static Data

import { Module } from "@/components/layout/LeftPanelModules";
import {
  ConstellationNode,
  ConstellationEdge,
  LevelNode,
  VisualizationStats,
} from "@/types";

// ── Module list (sidebar) ─────────────────────────────────────────────────────
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
    position: { x: 80, y: 40 },
    color: "purple",
    dependencies: ["api"],
  },
  {
    id: "api",
    fileName: "API",
    position: { x: 480, y: 80 },
    color: "yellow",
    dependencies: ["database"],
  },
  {
    id: "database",
    fileName: "DATABASE",
    position: { x: 560, y: 280 },
    color: "green",
    dependencies: [],
  },
  {
    id: "ui",
    fileName: "UI",
    position: { x: 300, y: 340 },
    color: "yellow",
    dependencies: ["api", "auth"],
  },
  {
    id: "payments",
    fileName: "PAYMENTS",
    position: { x: 540, y: 500 },
    color: "green",
    dependencies: ["api"],
  },
  {
    id: "analytics",
    fileName: "ANALYTICS",
    position: { x: 100, y: 460 },
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

// ── Per-module fallback data ───────────────────────────────────────────────────
export const mockAuthLevelNodes: LevelNode[] = [
  {
    id: "auth-1",
    level: 1,
    fileName: "jwt.ts",
    description: "Token signing",
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
    description: "Session mgmt",
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
    description: "Hashing & reset",
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

export const mockApiLevelNodes: LevelNode[] = [
  {
    id: "api-1",
    level: 1,
    fileName: "router.ts",
    description: "Route definitions",
    difficulty: "LOW",
    isCompleted: true,
    dependencies: [],
  },
  {
    id: "api-2",
    level: 2,
    fileName: "middleware.ts",
    description: "Request pipeline",
    difficulty: "MED",
    isCompleted: false,
    dependencies: ["router.ts"],
  },
  {
    id: "api-3",
    level: 3,
    fileName: "endpoints.ts",
    description: "API endpoints",
    difficulty: "MED",
    isCompleted: false,
    dependencies: ["middleware.ts"],
  },
  {
    id: "api-4",
    level: 4,
    fileName: "validators.ts",
    description: "Input validation",
    difficulty: "LOW",
    isCompleted: false,
    dependencies: ["endpoints.ts"],
  },
  {
    id: "api-5",
    level: 5,
    fileName: "handlers.ts",
    description: "Request handlers",
    difficulty: "HIGH",
    isCompleted: false,
    dependencies: ["validators.ts"],
  },
];

export const mockDatabaseLevelNodes: LevelNode[] = [
  {
    id: "db-1",
    level: 1,
    fileName: "connection.ts",
    description: "DB connection",
    difficulty: "LOW",
    isCompleted: true,
    dependencies: [],
  },
  {
    id: "db-2",
    level: 2,
    fileName: "models.ts",
    description: "Data models",
    difficulty: "MED",
    isCompleted: false,
    dependencies: ["connection.ts"],
  },
  {
    id: "db-3",
    level: 3,
    fileName: "migrations.ts",
    description: "Schema changes",
    difficulty: "MED",
    isCompleted: false,
    dependencies: ["models.ts"],
  },
  {
    id: "db-4",
    level: 4,
    fileName: "queries.ts",
    description: "DB queries",
    difficulty: "HIGH",
    isCompleted: false,
    dependencies: ["migrations.ts"],
  },
  {
    id: "db-5",
    level: 5,
    fileName: "seeds.ts",
    description: "Seed data",
    difficulty: "LOW",
    isCompleted: false,
    dependencies: ["queries.ts"],
  },
];

export const mockUiLevelNodes: LevelNode[] = [
  {
    id: "ui-1",
    level: 1,
    fileName: "theme.ts",
    description: "Design tokens",
    difficulty: "LOW",
    isCompleted: true,
    dependencies: [],
  },
  {
    id: "ui-2",
    level: 2,
    fileName: "components.tsx",
    description: "Base components",
    difficulty: "MED",
    isCompleted: false,
    dependencies: ["theme.ts"],
  },
  {
    id: "ui-3",
    level: 3,
    fileName: "layouts.tsx",
    description: "Page layouts",
    difficulty: "MED",
    isCompleted: false,
    dependencies: ["components.tsx"],
  },
  {
    id: "ui-4",
    level: 4,
    fileName: "pages.tsx",
    description: "App pages",
    difficulty: "HIGH",
    isCompleted: false,
    dependencies: ["layouts.tsx"],
  },
  {
    id: "ui-5",
    level: 5,
    fileName: "hooks.ts",
    description: "Custom hooks",
    difficulty: "MED",
    isCompleted: false,
    dependencies: ["pages.tsx"],
  },
];

export const mockPaymentsLevelNodes: LevelNode[] = [
  {
    id: "pay-1",
    level: 1,
    fileName: "stripe.ts",
    description: "Stripe setup",
    difficulty: "LOW",
    isCompleted: true,
    dependencies: [],
  },
  {
    id: "pay-2",
    level: 2,
    fileName: "checkout.ts",
    description: "Checkout flow",
    difficulty: "MED",
    isCompleted: false,
    dependencies: ["stripe.ts"],
  },
  {
    id: "pay-3",
    level: 3,
    fileName: "webhook.ts",
    description: "Payment events",
    difficulty: "HIGH",
    isCompleted: false,
    dependencies: ["checkout.ts"],
  },
  {
    id: "pay-4",
    level: 4,
    fileName: "refunds.ts",
    description: "Refund logic",
    difficulty: "MED",
    isCompleted: false,
    dependencies: ["webhook.ts"],
  },
];

export const mockAnalyticsLevelNodes: LevelNode[] = [
  {
    id: "ana-1",
    level: 1,
    fileName: "events.ts",
    description: "Event tracking",
    difficulty: "LOW",
    isCompleted: true,
    dependencies: [],
  },
  {
    id: "ana-2",
    level: 2,
    fileName: "metrics.ts",
    description: "Key metrics",
    difficulty: "MED",
    isCompleted: false,
    dependencies: ["events.ts"],
  },
  {
    id: "ana-3",
    level: 3,
    fileName: "reports.ts",
    description: "Report generation",
    difficulty: "HIGH",
    isCompleted: false,
    dependencies: ["metrics.ts"],
  },
];

export function getMockLevelNodes(moduleId: string): LevelNode[] {
  switch (moduleId) {
    case "auth":
      return mockAuthLevelNodes;
    case "api":
      return mockApiLevelNodes;
    case "database":
      return mockDatabaseLevelNodes;
    case "ui":
      return mockUiLevelNodes;
    case "payments":
      return mockPaymentsLevelNodes;
    case "analytics":
      return mockAnalyticsLevelNodes;
    default:
      return mockAuthLevelNodes;
  }
}

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

export const mockVisualizationStats: VisualizationStats = {
  filesFound: 247,
  criticalPaths: 6,
  completionPercentage: 8,
};
