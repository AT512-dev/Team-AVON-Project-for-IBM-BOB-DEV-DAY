"use client";

import React, { useState, useEffect, useMemo, useCallback } from "react";
import { SimpleFile, fetchFileContent } from "@/lib/api";

interface FileDetailViewProps {
  selectedPath: string | null;
  repoFiles: SimpleFile[];
  onClose: () => void;
  onFileSelect: (path: string) => void;
  moduleContext?: string | null;
}

export default function FileDetailView({
  selectedPath,
  repoFiles,
  onClose,
  onFileSelect,
  moduleContext,
}: FileDetailViewProps) {
  const [fileContent, setFileContent] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Compute folder/file status from props
  const fileInfo = useMemo(() => {
    if (!selectedPath) {
      return { isFolder: false, folderContents: [], matchingFile: null };
    }

    // selectedPath may be a node id (underscores) OR a real file path (slashes)
    // Try exact path match first, then fall back to id match
    const matchingFile =
      repoFiles.find((f) => f.path === selectedPath) ??
      repoFiles.find((f) => f.id === selectedPath);

    // Resolve the real path for folder-child lookups
    const realPath = matchingFile?.path ?? selectedPath;

    const childFiles = repoFiles.filter((f) =>
      f.path.startsWith(realPath + "/"),
    );

    if (childFiles.length > 0 && !matchingFile) {
      const immediateChildren = childFiles.filter((f) => {
        const relativePath = f.path.substring(realPath.length + 1);
        return !relativePath.includes("/");
      });
      return {
        isFolder: true,
        folderContents: immediateChildren,
        matchingFile: null,
      };
    }

    return { isFolder: false, folderContents: [], matchingFile };
  }, [selectedPath, repoFiles]);

  // ── Real file content fetch ───────────────────────────────────────────────
  const loadFileContent = useCallback((path: string) => {
    let cancelled = false;

    // setIsLoading asynchronously — never call setState synchronously in effect
    const t = setTimeout(() => { if (!cancelled) setIsLoading(true); }, 0);

    fetchFileContent(path).then((content) => {
      if (cancelled) return;
      setFileContent(
        content ?? `// Could not load content for: ${path}\n// Check that the backend is running and the file exists.`,
      );
      setIsLoading(false);
    });

    return () => {
      cancelled = true;
      clearTimeout(t);
    };
  }, []);

  useEffect(() => {
    if (!selectedPath || !fileInfo.matchingFile) {
      setFileContent(null);
      setIsLoading(false);
      return;
    }
    // Use the real file path (not the node id with underscores)
    const realFilePath = fileInfo.matchingFile.path;
    const cancel = loadFileContent(realFilePath);
    return cancel;
  }, [selectedPath, fileInfo.matchingFile, loadFileContent]);

  // Derive metadata from real file data, fall back to hash-based values
  const fileMetadata = useMemo(() => {
    if (!selectedPath) {
      return { lessonNumber: 1, difficulty: "MED", estimatedTime: "~10 min" };
    }

    const matched = repoFiles.find((f) => f.path === selectedPath);

    if (matched) {
      const complexityMap: Record<string, string> = {
        Easy: "LOW",
        Medium: "MED",
        Hard: "HIGH",
      };
      const difficulty = complexityMap[matched.complexity] ?? "MED";
      const timeMap: Record<string, string> = {
        LOW: "~5 min",
        MED: "~15 min",
        HIGH: "~30 min",
      };
      // Lesson number = position in repoFiles list
      const lessonNumber = repoFiles.indexOf(matched) + 1;
      return {
        lessonNumber,
        difficulty,
        estimatedTime: timeMap[difficulty] ?? "~10 min",
        objective: matched.objective,
      };
    }

    // Fallback hash for nodes not in repoFiles (e.g. clicked by node id)
    let hash = 0;
    for (let i = 0; i < selectedPath.length; i++) {
      hash = (hash << 5) - hash + selectedPath.charCodeAt(i);
      hash = hash & hash;
    }
    return {
      lessonNumber: (Math.abs(hash) % 12) + 1,
      difficulty: ["LOW", "MED", "HIGH"][Math.abs(hash) % 3],
      estimatedTime: `~${(Math.abs(hash) % 20) + 5} min`,
      objective: null,
    };
  }, [selectedPath, repoFiles]);

  if (!selectedPath) return null;

  // Resolve display name from real path if we matched a file
  const resolvedPath = fileInfo.matchingFile?.path ?? selectedPath;
  const pathParts = resolvedPath.split("/");
  const fileName = pathParts[pathParts.length - 1];
  const { lessonNumber, difficulty, estimatedTime, objective } = fileMetadata;

  const difficultyColors = {
    LOW: {
      bg: "rgba(16,185,129,0.12)",
      border: "rgba(16,185,129,0.3)",
      text: "#10b981",
    },
    MED: {
      bg: "rgba(245,158,11,0.12)",
      border: "rgba(245,158,11,0.3)",
      text: "#f59e0b",
    },
    HIGH: {
      bg: "rgba(239,68,68,0.12)",
      border: "rgba(239,68,68,0.3)",
      text: "#ef4444",
    },
  };

  const diffColor =
    difficultyColors[difficulty as keyof typeof difficultyColors] ??
    difficultyColors["MED"];

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        background: "#0d1117",
        zIndex: 100,
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: "16px 20px",
          borderBottom: "1px solid rgba(255,255,255,0.06)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 8, flex: 1 }}>
          <button
            onClick={onClose}
            style={{
              width: 32,
              height: 32,
              borderRadius: 8,
              background: "rgba(255,255,255,0.05)",
              border: "1px solid rgba(255,255,255,0.1)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              cursor: "pointer",
              flexShrink: 0,
            }}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <path
                d="M19 12H5M5 12l7 7M5 12l7-7"
                stroke="rgba(255,255,255,0.6)"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>

          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 6,
              overflow: "hidden",
            }}
          >
            <span
              style={{
                fontSize: 13,
                color: "rgba(255,255,255,0.4)",
                cursor: "pointer",
              }}
              onClick={onClose}
            >
              All modules
            </span>
            {moduleContext && (
              <>
                <span style={{ fontSize: 13, color: "rgba(255,255,255,0.2)" }}>›</span>
                <span style={{ fontSize: 13, color: "rgba(255,255,255,0.5)" }}>
                  {moduleContext.toUpperCase()}
                </span>
              </>
            )}
            <span style={{ fontSize: 13, color: "rgba(255,255,255,0.2)" }}>›</span>
            <span
              style={{
                fontSize: 13,
                color: "#06b6d4",
                fontWeight: 600,
                whiteSpace: "nowrap",
                overflow: "hidden",
                textOverflow: "ellipsis",
              }}
            >
              {fileName}
            </span>
          </div>
        </div>
      </div>

      {/* File metadata */}
      {!fileInfo.isFolder && (
        <div
          style={{
            padding: "16px 20px",
            borderBottom: "1px solid rgba(255,255,255,0.06)",
            display: "flex",
            alignItems: "center",
            gap: 12,
            flexWrap: "wrap",
          }}
        >
          <div
            style={{
              padding: "4px 10px",
              borderRadius: 6,
              background: "rgba(6,182,212,0.12)",
              border: "1px solid rgba(6,182,212,0.25)",
              fontSize: 11,
              fontWeight: 600,
              color: "#06b6d4",
              letterSpacing: "0.5px",
            }}
          >
            LESSON {lessonNumber}
          </div>
          <div style={{ fontSize: 12, color: "rgba(255,255,255,0.4)" }}>
            {estimatedTime}
          </div>
          <div
            style={{
              padding: "4px 10px",
              borderRadius: 6,
              background: diffColor.bg,
              border: `1px solid ${diffColor.border}`,
              fontSize: 11,
              fontWeight: 600,
              color: diffColor.text,
              letterSpacing: "0.5px",
            }}
          >
            Difficulty {difficulty}
          </div>
        </div>
      )}

      {/* Content */}
      <div style={{ flex: 1, overflow: "auto", padding: "20px" }}>
        {fileInfo.isFolder ? (
          <div>
            <h3
              style={{
                fontSize: 16,
                fontWeight: 700,
                color: "rgba(255,255,255,0.85)",
                marginBottom: 16,
              }}
            >
              Folder Contents
            </h3>
            {fileInfo.folderContents.length === 0 ? (
              <div
                style={{
                  fontSize: 13,
                  color: "rgba(255,255,255,0.3)",
                  textAlign: "center",
                  padding: "40px 0",
                }}
              >
                Empty folder
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {fileInfo.folderContents.map((file) => {
                  const isSubFolder = repoFiles.some((f) =>
                    f.path.startsWith(file.path + "/"),
                  );
                  return (
                    <div
                      key={file.path}
                      onClick={() => onFileSelect(file.path)}
                      style={{
                        padding: "12px 14px",
                        background: "rgba(255,255,255,0.03)",
                        border: "1px solid rgba(255,255,255,0.08)",
                        borderRadius: 8,
                        display: "flex",
                        alignItems: "center",
                        gap: 10,
                        cursor: "pointer",
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.background = "rgba(255,255,255,0.06)";
                        e.currentTarget.style.borderColor = "rgba(255,255,255,0.12)";
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.background = "rgba(255,255,255,0.03)";
                        e.currentTarget.style.borderColor = "rgba(255,255,255,0.08)";
                      }}
                    >
                      {isSubFolder ? (
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                          <path
                            d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"
                            stroke="#f59e0b"
                            strokeWidth="2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                          />
                        </svg>
                      ) : (
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                          <path
                            d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"
                            stroke="rgba(255,255,255,0.45)"
                            strokeWidth="2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                          />
                          <polyline
                            points="13 2 13 9 20 9"
                            stroke="rgba(255,255,255,0.45)"
                            strokeWidth="2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                          />
                        </svg>
                      )}
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div
                          style={{
                            fontSize: 13,
                            color: "rgba(255,255,255,0.7)",
                            overflow: "hidden",
                            textOverflow: "ellipsis",
                            whiteSpace: "nowrap",
                          }}
                        >
                          {file.path.split("/").pop()}
                        </div>
                        {file.objective && (
                          <div
                            style={{
                              fontSize: 11,
                              color: "rgba(255,255,255,0.3)",
                              marginTop: 2,
                              overflow: "hidden",
                              textOverflow: "ellipsis",
                              whiteSpace: "nowrap",
                            }}
                          >
                            {file.objective}
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        ) : (
          <div>
            {/* Learning objective from real backend data */}
            {objective && (
              <div
                style={{
                  marginBottom: 20,
                  padding: "14px 16px",
                  background: "rgba(6,182,212,0.05)",
                  border: "1px solid rgba(6,182,212,0.15)",
                  borderRadius: 10,
                }}
              >
                <div
                  style={{
                    fontSize: 10,
                    fontWeight: 700,
                    color: "rgba(6,182,212,0.6)",
                    letterSpacing: "1px",
                    marginBottom: 6,
                  }}
                >
                  LEARNING OBJECTIVE
                </div>
                <p
                  style={{
                    fontSize: 13,
                    color: "rgba(255,255,255,0.7)",
                    lineHeight: 1.6,
                    margin: 0,
                  }}
                >
                  {objective}
                </p>
              </div>
            )}

            {/* Full file path */}
            <div
              style={{
                marginBottom: 16,
                padding: "8px 12px",
                background: "rgba(255,255,255,0.03)",
                border: "1px solid rgba(255,255,255,0.06)",
                borderRadius: 8,
                fontFamily: "monospace",
                fontSize: 12,
                color: "rgba(255,255,255,0.35)",
              }}
            >
              {resolvedPath}
            </div>

            {/* Code viewer */}
            <div
              style={{
                background: "#161b22",
                border: "1px solid rgba(255,255,255,0.08)",
                borderRadius: 10,
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  padding: "10px 16px",
                  borderBottom: "1px solid rgba(255,255,255,0.06)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                }}
              >
                <span
                  style={{
                    fontSize: 12,
                    color: "rgba(255,255,255,0.5)",
                    fontFamily: "monospace",
                  }}
                >
                  {fileName}
                </span>
                <button
                  onClick={() => {
                    if (fileContent) navigator.clipboard.writeText(fileContent);
                  }}
                  style={{
                    padding: "4px 10px",
                    borderRadius: 6,
                    background: "rgba(255,255,255,0.05)",
                    border: "1px solid rgba(255,255,255,0.1)",
                    fontSize: 11,
                    color: "rgba(255,255,255,0.6)",
                    cursor: "pointer",
                    fontFamily: "inherit",
                  }}
                >
                  Copy
                </button>
              </div>

              <div
                style={{
                  padding: "16px",
                  overflowX: "auto",
                  maxHeight: "500px",
                  overflowY: "auto",
                }}
              >
                {isLoading ? (
                  <div
                    style={{
                      fontSize: 13,
                      color: "rgba(255,255,255,0.3)",
                      textAlign: "center",
                      padding: "40px 0",
                    }}
                  >
                    Loading file content...
                  </div>
                ) : (
                  <pre
                    style={{
                      margin: 0,
                      fontSize: 13,
                      lineHeight: 1.6,
                      color: "rgba(255,255,255,0.8)",
                      fontFamily: "monospace",
                      whiteSpace: "pre-wrap",
                      wordBreak: "break-word",
                    }}
                  >
                    {fileContent}
                  </pre>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Made with Bob
