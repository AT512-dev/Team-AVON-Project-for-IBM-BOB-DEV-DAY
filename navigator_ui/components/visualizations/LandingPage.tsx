"use client";

import { useState, useEffect, useRef } from "react";

const DEMO_REPO_URL =
  "https://github.com/AleyJan/vision-intelligence---techmesh-26";

interface LandingPageProps {
  onConnect?: (repoUrl?: string) => void;
}

function Starfield() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animId: number;
    interface Star {
      x: number;
      y: number;
      r: number;
      opacity: number;
      speed: number;
      phase: number;
    }
    let stars: Star[] = [];

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      const count = Math.floor((canvas.width * canvas.height) / 4500);
      stars = Array.from({ length: count }, () => ({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        r: Math.random() * 1.2 + 0.2,
        opacity: Math.random() * 0.6 + 0.1,
        speed: Math.random() * 0.015 + 0.003,
        phase: Math.random() * Math.PI * 2,
      }));
    };

    const draw = (t: number) => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      for (const s of stars) {
        const tw = Math.sin(t * s.speed + s.phase);
        const alpha = Math.max(0.05, Math.min(1, s.opacity + tw * 0.3));
        const scale = 1 + tw * 0.15;
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.r * scale, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(220,235,255,${alpha})`;
        ctx.fill();
      }
      animId = requestAnimationFrame(draw);
    };

    resize();
    window.addEventListener("resize", resize);
    animId = requestAnimationFrame(draw);
    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener("resize", resize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      aria-hidden="true"
      style={{
        position: "fixed",
        inset: 0,
        width: "100%",
        height: "100%",
        zIndex: 0,
        pointerEvents: "none",
      }}
    />
  );
}

function GithubIcon({
  size = 20,
  color = "#0a0a1f",
}: {
  size?: number;
  color?: string;
}) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill={color}>
      <path d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0112 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z" />
    </svg>
  );
}

const cyanBtnStyle: React.CSSProperties = {
  width: "100%",
  padding: "13px 24px",
  borderRadius: 12,
  border: "none",
  background: "linear-gradient(135deg, #00d4f5 0%, #00b8e6 100%)",
  boxShadow: "0 0 20px rgba(0,229,255,0.35)",
  color: "#0a0a1f",
  fontWeight: 700,
  fontSize: 14,
  cursor: "pointer",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  gap: 8,
  transition: "all 0.2s ease",
};

export default function LandingPage({ onConnect }: LandingPageProps) {
  // Pre-fill with demo repo URL so judges just hit connect
  const [repoUrl, setRepoUrl] = useState(DEMO_REPO_URL);
  const [step, setStep] = useState<"idle" | "connecting" | "done">("idle");

  const handleConnect = () => {
    setStep("connecting");
    // Simulate brief connecting state then hand off
    setTimeout(() => {
      setStep("done");
      onConnect?.(repoUrl.trim() || DEMO_REPO_URL);
    }, 1800);
  };

  return (
    <>
      <style>{`
        @keyframes lp-spin { to { transform: rotate(360deg); } }
        @keyframes lp-fadeUp { from { opacity:0; transform:translateY(18px); } to { opacity:1; transform:translateY(0); } }
        .lp-fadeup { animation: lp-fadeUp 0.7s ease-out forwards; opacity:0; }
      `}</style>

      <Starfield />

      <main
        style={{
          position: "relative",
          zIndex: 1,
          minHeight: "100vh",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "64px 16px",
          background:
            "radial-gradient(ellipse at 50% 0%, rgba(30,20,80,0.55) 0%, transparent 65%)," +
            "radial-gradient(ellipse at 50% 100%, rgba(5,5,20,0.75) 0%, transparent 65%)," +
            "linear-gradient(180deg, #0a0a1f 0%, #0d0d2b 40%, #0a0a22 100%)",
        }}
      >
        {/* Brand */}
        <div
          className="lp-fadeup"
          style={{
            animationDelay: "0ms",
            textAlign: "center",
            marginBottom: 36,
          }}
        >
          <div
            style={{
              fontSize: 13,
              fontWeight: 500,
              letterSpacing: "0.18em",
              color: "rgba(255,255,255,0.45)",
              textTransform: "uppercase",
              marginBottom: 4,
            }}
          >
            Compass AI
          </div>
          <div style={{ fontSize: 13, color: "rgba(255,255,255,0.28)" }}>
            Your AI onboarding mentor — powered by IBM WatsonX
          </div>
        </div>

        {/* Heading */}
        <h1
          className="lp-fadeup"
          style={{
            animationDelay: "120ms",
            fontSize: "clamp(28px, 5vw, 52px)",
            fontWeight: 700,
            color: "white",
            textAlign: "center",
            lineHeight: 1.2,
            maxWidth: 640,
            marginBottom: 16,
          }}
        >
          Connect your GitHub repo to begin
        </h1>

        {/* Subtitle */}
        <p
          className="lp-fadeup"
          style={{
            animationDelay: "240ms",
            fontSize: 15,
            color: "rgba(255,255,255,0.45)",
            textAlign: "center",
            maxWidth: 440,
            lineHeight: 1.7,
            marginBottom: 36,
          }}
        >
          Bob will clone your repo, map every dependency with WatsonX, and build
          a personalised learning roadmap.
        </p>

        {/* Action area */}
        <div
          className="lp-fadeup"
          style={{ animationDelay: "360ms", width: "100%", maxWidth: 440 }}
        >
          {step === "idle" && (
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {/* Repo URL input — pre-filled with demo URL */}
              <div style={{ position: "relative" }}>
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="rgba(255,255,255,0.3)"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  style={{
                    position: "absolute",
                    left: 14,
                    top: "50%",
                    transform: "translateY(-50%)",
                    pointerEvents: "none",
                  }}
                >
                  <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 00-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0020 4.77 5.07 5.07 0 0019.91 1S18.73.65 16 2.48a13.38 13.38 0 00-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 005 4.77a5.44 5.44 0 00-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 009 18.13V22" />
                </svg>
                <input
                  type="text"
                  value={repoUrl}
                  onChange={(e) => setRepoUrl(e.target.value)}
                  placeholder="https://github.com/org/repo"
                  style={{
                    width: "100%",
                    padding: "13px 16px 13px 44px",
                    borderRadius: 12,
                    border: "1px solid rgba(0,229,255,0.3)",
                    background: "rgba(255,255,255,0.06)",
                    color: "white",
                    fontSize: 13,
                    outline: "none",
                    boxSizing: "border-box",
                    fontFamily: "monospace",
                  }}
                  onFocus={(e) => {
                    e.currentTarget.style.borderColor = "rgba(0,229,255,0.6)";
                    e.currentTarget.style.boxShadow =
                      "0 0 0 2px rgba(0,229,255,0.15)";
                  }}
                  onBlur={(e) => {
                    e.currentTarget.style.borderColor = "rgba(0,229,255,0.3)";
                    e.currentTarget.style.boxShadow = "none";
                  }}
                />
              </div>

              {/* Demo hint */}
              <div
                style={{
                  fontSize: 11,
                  color: "rgba(255,255,255,0.3)",
                  textAlign: "center",
                }}
              >
                ↑ Demo repo pre-filled — just click connect for the hackathon
                demo
              </div>

              {/* Connect button */}
              <button
                onClick={handleConnect}
                style={cyanBtnStyle}
                onMouseEnter={(e) => {
                  e.currentTarget.style.boxShadow =
                    "0 0 40px rgba(0,229,255,0.6)";
                  e.currentTarget.style.transform = "translateY(-1px)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.boxShadow =
                    "0 0 20px rgba(0,229,255,0.35)";
                  e.currentTarget.style.transform = "translateY(0)";
                }}
              >
                <GithubIcon size={16} />
                Connect with GitHub →
              </button>

              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: 6,
                  fontSize: 11,
                  color: "rgba(255,255,255,0.3)",
                }}
              >
                <svg
                  width="12"
                  height="12"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                >
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                  <path d="M7 11V7a5 5 0 0110 0v4" />
                </svg>
                Backend clones &amp; analyses · no code is modified
              </div>
            </div>
          )}

          {step === "connecting" && (
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: 16,
                padding: "32px 0",
              }}
            >
              <div
                style={{
                  width: 44,
                  height: 44,
                  borderRadius: "50%",
                  border: "2px solid rgba(0,229,255,0.15)",
                  borderTop: "2px solid #00e5ff",
                  animation: "lp-spin 0.8s linear infinite",
                }}
              />
              <div style={{ color: "rgba(255,255,255,0.7)", fontSize: 14 }}>
                Handing off to IBM Bob…
              </div>
              <div style={{ color: "rgba(255,255,255,0.3)", fontSize: 12 }}>
                Connecting to WatsonX backend
              </div>
            </div>
          )}
        </div>

        <div
          style={{
            position: "fixed",
            bottom: 0,
            left: "50%",
            transform: "translateX(-50%)",
            width: 400,
            height: 200,
            background:
              "radial-gradient(ellipse, rgba(0,229,255,0.12) 0%, transparent 70%)",
            pointerEvents: "none",
            zIndex: 0,
          }}
        />
      </main>
    </>
  );
}
