"use client";

import React, { useState, useRef, useEffect, useCallback } from "react";
import { getRepoUrl } from "@/lib/api";

// ── Types ─────────────────────────────────────────────────────────────────────
interface CitedFile {
  path: string;
  reason: string;
  complexity: string;
  loc: number;
}

interface Message {
  id: string;
  role: "bob" | "user";
  content: string;
  citedFiles?: CitedFile[];
  nextSteps?: string[];
  isLoading?: boolean;
}

interface BobChatPanelProps {
  selectedModule?: string | null;
  selectedFile?: string | null;
  repoPath?: string;
}

interface AskResponse {
  answer: string;
  cited_files: CitedFile[];
  related_files: string[];
  next_steps: string[];
  confidence: number;
  query_type: string;
}

// ── Config ────────────────────────────────────────────────────────────────────
const BOB_API = "http://localhost:8000/api/v1";

const QUICK_ACTIONS = [
  {
    label: "Show me the riskiest files",
    primary: true,
    question: "Which files are the most complex and risky?",
  },
  {
    label: "Explain the dependency graph",
    primary: false,
    question: "Explain the dependency graph of this codebase",
  },
];

let _counter = 0;
function nextId() {
  _counter += 1;
  return `msg_${Date.now()}_${_counter}`;
}

// ── Bob avatar ────────────────────────────────────────────────────────────────
function BobAvatar({ size = 28 }: { size?: number }) {
  return (
    <div
      style={{
        width: size,
        height: size,
        borderRadius: "50%",
        background: "linear-gradient(135deg, #1e293b 0%, #0f172a 100%)",
        border: "1px solid rgba(255,255,255,0.1)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        flexShrink: 0,
      }}
    >
      <svg
        width={size * 0.55}
        height={size * 0.55}
        viewBox="0 0 24 24"
        fill="none"
      >
        <rect
          x="5"
          y="8"
          width="14"
          height="11"
          rx="2"
          stroke="rgba(255,255,255,0.6)"
          strokeWidth="1.5"
        />
        <path
          d="M9 8V6a3 3 0 016 0v2"
          stroke="rgba(255,255,255,0.6)"
          strokeWidth="1.5"
          strokeLinecap="round"
        />
        <circle cx="9.5" cy="13" r="1" fill="rgba(6,182,212,0.9)" />
        <circle cx="14.5" cy="13" r="1" fill="rgba(6,182,212,0.9)" />
        <path
          d="M9.5 16.5h5"
          stroke="rgba(255,255,255,0.4)"
          strokeWidth="1.2"
          strokeLinecap="round"
        />
        <line
          x1="12"
          y1="5"
          x2="12"
          y2="8"
          stroke="rgba(255,255,255,0.4)"
          strokeWidth="1.2"
        />
        <circle cx="12" cy="4.5" r="1" fill="rgba(255,255,255,0.3)" />
      </svg>
    </div>
  );
}

// ── Message bubble ────────────────────────────────────────────────────────────
function MessageBubble({ msg }: { msg: Message }) {
  const isUser = msg.role === "user";

  if (msg.isLoading) {
    return (
      <div
        style={{
          display: "flex",
          alignItems: "flex-start",
          gap: 10,
          marginBottom: 16,
        }}
      >
        <BobAvatar />
        <div
          style={{
            background: "rgba(255,255,255,0.05)",
            border: "1px solid rgba(255,255,255,0.08)",
            borderRadius: "4px 12px 12px 12px",
            padding: "12px 16px",
            display: "flex",
            alignItems: "center",
            gap: 6,
          }}
        >
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              style={{
                width: 6,
                height: 6,
                borderRadius: "50%",
                background: "#06b6d4",
                animation: `bobDot 1.2s ease-in-out ${i * 0.2}s infinite`,
              }}
            />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div
      style={{
        display: "flex",
        flexDirection: isUser ? "row-reverse" : "row",
        alignItems: "flex-start",
        gap: 10,
        marginBottom: 16,
      }}
    >
      {!isUser && <BobAvatar />}
      <div
        style={{
          maxWidth: "82%",
          display: "flex",
          flexDirection: "column",
          gap: 8,
        }}
      >
        {/* Main bubble */}
        <div
          style={{
            background: isUser
              ? "rgba(6,182,212,0.12)"
              : "rgba(255,255,255,0.05)",
            border: `1px solid ${isUser ? "rgba(6,182,212,0.25)" : "rgba(255,255,255,0.08)"}`,
            borderRadius: isUser ? "12px 4px 12px 12px" : "4px 12px 12px 12px",
            padding: "12px 16px",
            fontSize: 13,
            lineHeight: 1.6,
            color: isUser ? "rgba(255,255,255,0.85)" : "rgba(255,255,255,0.75)",
            whiteSpace: "pre-wrap",
          }}
        >
          {msg.content}
        </div>

        {/* Cited files */}
        {msg.citedFiles && msg.citedFiles.length > 0 && (
          <div
            style={{
              background: "rgba(255,255,255,0.03)",
              border: "1px solid rgba(255,255,255,0.06)",
              borderRadius: 8,
              padding: "10px 12px",
            }}
          >
            <div
              style={{
                fontSize: 10,
                color: "rgba(255,255,255,0.3)",
                marginBottom: 7,
                letterSpacing: "0.08em",
                textTransform: "uppercase",
              }}
            >
              Referenced files
            </div>
            {msg.citedFiles.map((f) => (
              <div
                key={f.path}
                style={{
                  display: "flex",
                  alignItems: "flex-start",
                  justifyContent: "space-between",
                  padding: "5px 0",
                  borderBottom: "1px solid rgba(255,255,255,0.04)",
                  gap: 8,
                }}
              >
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: 2,
                    minWidth: 0,
                  }}
                >
                  <span
                    style={{
                      fontSize: 11,
                      color: "#06b6d4",
                      fontFamily: "monospace",
                      wordBreak: "break-all",
                    }}
                  >
                    {f.path}
                  </span>
                  {f.reason && (
                    <span
                      style={{
                        fontSize: 10,
                        color: "rgba(255,255,255,0.3)",
                        lineHeight: 1.4,
                      }}
                    >
                      {f.reason}
                    </span>
                  )}
                </div>
                <span
                  style={{
                    fontSize: 9,
                    fontWeight: 600,
                    padding: "2px 6px",
                    borderRadius: 4,
                    flexShrink: 0,
                    color:
                      f.complexity === "Easy"
                        ? "#10b981"
                        : f.complexity === "Hard"
                          ? "#f87171"
                          : "#f59e0b",
                    background:
                      f.complexity === "Easy"
                        ? "rgba(16,185,129,0.1)"
                        : f.complexity === "Hard"
                          ? "rgba(248,113,113,0.1)"
                          : "rgba(245,158,11,0.1)",
                  }}
                >
                  {f.complexity}
                </span>
              </div>
            ))}
          </div>
        )}

        {/* Next steps */}
        {msg.nextSteps && msg.nextSteps.length > 0 && (
          <div
            style={{
              background: "rgba(109,92,231,0.06)",
              border: "1px solid rgba(109,92,231,0.15)",
              borderRadius: 8,
              padding: "10px 12px",
            }}
          >
            <div
              style={{
                fontSize: 10,
                color: "rgba(167,139,250,0.6)",
                marginBottom: 7,
                letterSpacing: "0.08em",
                textTransform: "uppercase",
              }}
            >
              Next steps
            </div>
            {msg.nextSteps.map((step, i) => (
              <div
                key={i}
                style={{
                  display: "flex",
                  gap: 8,
                  fontSize: 12,
                  color: "rgba(255,255,255,0.5)",
                  marginBottom: 4,
                  lineHeight: 1.5,
                }}
              >
                <span style={{ color: "#6d5ce7", flexShrink: 0 }}>
                  {i + 1}.
                </span>
                {step}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────────
export default function BobChatPanel({
  selectedModule,
  selectedFile,
  repoPath,
}: BobChatPanelProps) {
  const activeRepoPath = repoPath || getRepoUrl();

  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "bob",
      content:
        "Hi! I've scanned this codebase and built a personalized learning roadmap for you. Ask me anything about the code.",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [quickActionsUsed, setQuickActionsUsed] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Auto-contextual message when file/module changes
  useEffect(() => {
    if (selectedFile) {
      setMessages((prev) => [
        ...prev,
        {
          id: nextId(),
          role: "bob",
          content: `You selected \`${selectedFile}\`. Ask me anything about this file — what it does, how it fits in, or where to start reading.`,
        },
      ]);
    }
  }, [selectedFile]);

  // ── Ask Bob via real /ask endpoint ────────────────────────────────────────
  const askBob = useCallback(
    async (question: string) => {
      if (!question.trim() || isLoading) return;

      const userMsgId = nextId();
      const loadingId = nextId();
      const responseId = nextId();

      setMessages((prev) => [
        ...prev,
        { id: userMsgId, role: "user", content: question },
        { id: loadingId, role: "bob", content: "", isLoading: true },
      ]);
      setInput("");
      setIsLoading(true);
      setQuickActionsUsed(true);

      try {
        const response = await fetch(`${BOB_API}/ask`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            repo_path: activeRepoPath,
            repo_url: activeRepoPath,
            question,
            current_file: selectedFile ?? undefined,
            context: selectedModule
              ? { task: `understanding the ${selectedModule} module` }
              : undefined,
          }),
        });

        if (!response.ok) {
          const errText = await response.text();
          throw new Error(`HTTP ${response.status}: ${errText}`);
        }

        const data = (await response.json()) as AskResponse;

        setMessages((prev) =>
          prev.map((m) =>
            m.id === loadingId
              ? {
                  id: responseId,
                  role: "bob" as const,
                  content: data.answer,
                  citedFiles: data.cited_files ?? [],
                  nextSteps: data.next_steps ?? [],
                }
              : m,
          ),
        );
      } catch (err) {
        console.error("BobChatPanel error:", err);
        setMessages((prev) =>
          prev.map((m) =>
            m.id === loadingId
              ? {
                  id: responseId,
                  role: "bob" as const,
                  content:
                    err instanceof Error
                      ? `Something went wrong: ${err.message}`
                      : "I couldn't reach the backend. Make sure the server is running at localhost:8000.",
                }
              : m,
          ),
        );
      } finally {
        setIsLoading(false);
      }
    },
    [isLoading, activeRepoPath, selectedFile, selectedModule],
  );

  const handleSend = () => askBob(input);
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        background: "#0d1117",
        borderLeft: "1px solid rgba(255,255,255,0.06)",
        overflow: "hidden",
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: "18px 18px 14px",
          borderBottom: "1px solid rgba(255,255,255,0.06)",
          flexShrink: 0,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <BobAvatar size={32} />
          <div>
            <div
              style={{
                fontSize: 14,
                fontWeight: 700,
                color: "#ffffff",
                display: "flex",
                alignItems: "center",
                gap: 7,
              }}
            >
              Bob
              <span
                style={{
                  width: 7,
                  height: 7,
                  borderRadius: "50%",
                  background: "#10b981",
                  boxShadow: "0 0 6px #10b981",
                  display: "inline-block",
                }}
              />
            </div>
            <div
              style={{
                fontSize: 11,
                color: "rgba(255,255,255,0.3)",
                marginTop: 1,
              }}
            >
              Your AI code mentor
            </div>
          </div>
          {/* Context indicator */}
          {(selectedModule || selectedFile) && (
            <div
              style={{
                marginLeft: "auto",
                padding: "3px 8px",
                borderRadius: 6,
                background: "rgba(6,182,212,0.1)",
                border: "1px solid rgba(6,182,212,0.2)",
                fontSize: 10,
                color: "#06b6d4",
                maxWidth: 120,
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
              }}
            >
              {selectedFile
                ? selectedFile.split("/").pop()
                : selectedModule?.toUpperCase()}
            </div>
          )}
        </div>
      </div>

      {/* Messages */}
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          padding: "18px 14px 8px",
          scrollbarWidth: "none",
        }}
      >
        {messages.map((msg) => (
          <MessageBubble key={msg.id} msg={msg} />
        ))}

        {/* Quick actions */}
        {!quickActionsUsed && (
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: 8,
              marginTop: 4,
              marginBottom: 16,
            }}
          >
            {QUICK_ACTIONS.map((action) => (
              <div
                key={action.label}
                style={{
                  display: "flex",
                  justifyContent: action.primary ? "flex-start" : "flex-end",
                }}
              >
                <button
                  onClick={() => askBob(action.question)}
                  style={{
                    padding: action.primary ? "9px 16px" : "8px 14px",
                    borderRadius: 9,
                    border: action.primary
                      ? "1px solid rgba(6,182,212,0.4)"
                      : "1px solid rgba(255,255,255,0.12)",
                    background: action.primary
                      ? "rgba(6,182,212,0.12)"
                      : "rgba(255,255,255,0.04)",
                    color: action.primary ? "#06b6d4" : "rgba(255,255,255,0.6)",
                    fontSize: 12,
                    fontWeight: action.primary ? 600 : 400,
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    gap: 7,
                    fontFamily: "inherit",
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.opacity = "0.8";
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.opacity = "1";
                  }}
                >
                  {action.primary && (
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none">
                      <path
                        d="M13 2L4.5 13.5H11L10 22L19.5 10.5H13L13 2Z"
                        fill="#06b6d4"
                      />
                    </svg>
                  )}
                  {action.label}
                </button>
              </div>
            ))}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input bar */}
      <div
        style={{
          padding: "12px 14px 16px",
          borderTop: "1px solid rgba(255,255,255,0.06)",
          flexShrink: 0,
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 10,
            background: "rgba(255,255,255,0.04)",
            border: "1px solid rgba(255,255,255,0.09)",
            borderRadius: 24,
            padding: "0 6px 0 16px",
            height: 44,
          }}
        >
          <input
            type="text"
            placeholder={
              selectedFile
                ? `Ask about ${selectedFile.split("/").pop()}...`
                : selectedModule
                  ? `Ask about the ${selectedModule.toUpperCase()} module...`
                  : "Ask anything about the codebase..."
            }
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            style={{
              flex: 1,
              background: "transparent",
              border: "none",
              outline: "none",
              color: "rgba(255,255,255,0.7)",
              fontSize: 13,
              fontFamily: "inherit",
            }}
          />
          <button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            style={{
              width: 32,
              height: 32,
              borderRadius: "50%",
              background:
                input.trim() && !isLoading
                  ? "#06b6d4"
                  : "rgba(255,255,255,0.06)",
              border: "none",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              cursor: input.trim() && !isLoading ? "pointer" : "default",
              transition: "all 0.2s",
              flexShrink: 0,
              boxShadow:
                input.trim() && !isLoading
                  ? "0 0 12px rgba(6,182,212,0.4)"
                  : "none",
            }}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
              <path
                d="M22 2L11 13"
                stroke="white"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M22 2L15 22L11 13L2 9L22 2Z"
                stroke="white"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
        </div>
      </div>

      <style>{`
        @keyframes bobDot {
          0%, 80%, 100% { transform: scale(0.6); opacity: 0.3; }
          40% { transform: scale(1); opacity: 1; }
        }
        div::-webkit-scrollbar { display: none; }
      `}</style>
    </div>
  );
}

// Made with Bob
