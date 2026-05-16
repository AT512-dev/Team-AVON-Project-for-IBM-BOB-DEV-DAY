// "use client";

// import React, { useState } from "react";
// import {
//   Search,
//   Wifi,
//   WifiOff,
//   Settings,
//   Loader2,
//   ChevronRight,
// } from "lucide-react";
// import { TopNavBarProps } from "@/types";

// export default function TopNavBar({
//   onAnalyze,
//   isConnected,
//   selectedModule,
//   currentView = "constellation",
//   onViewChange,
// }: TopNavBarProps) {
//   const [isAnalyzing, setIsAnalyzing] = useState(false);
//   const [taskInput, setTaskInput] = useState("");

//   const handleAnalyze = async () => {
//     if (isAnalyzing) return;
//     setIsAnalyzing(true);
//     await onAnalyze();
//     setTimeout(() => setIsAnalyzing(false), 2500);
//   };

//   return (
//     <nav
//       style={{
//         height: 52,
//         background: "#0d1117",
//         borderBottom: "1px solid rgba(255,255,255,0.06)",
//         display: "flex",
//         alignItems: "center",
//         padding: "0 20px",
//         gap: 16,
//         flexShrink: 0,
//         zIndex: 20,
//         position: "relative",
//       }}
//     >
//       {/* Left side — breadcrumb OR search */}
//       <div
//         style={{
//           display: "flex",
//           alignItems: "center",
//           gap: 12,
//           flex: 1,
//           minWidth: 0,
//         }}
//       >
//         {selectedModule ? (
//           /* Breadcrumb when inside a module */
//           <div
//             style={{
//               display: "flex",
//               alignItems: "center",
//               gap: 6,
//               flexShrink: 0,
//             }}
//           >
//             {/* All modules pill */}
//             <div
//               style={{
//                 display: "flex",
//                 alignItems: "center",
//                 gap: 6,
//                 padding: "4px 10px",
//                 background: "rgba(255,255,255,0.04)",
//                 border: "1px solid rgba(255,255,255,0.08)",
//                 borderRadius: 6,
//                 fontSize: 12,
//                 color: "rgba(255,255,255,0.5)",
//                 cursor: "pointer",
//               }}
//             >
//               All modules
//             </div>
//             <ChevronRight size={13} color="rgba(255,255,255,0.2)" />
//             {/* Module name pill */}
//             <div
//               style={{
//                 display: "flex",
//                 alignItems: "center",
//                 gap: 6,
//                 padding: "4px 10px",
//                 background: "rgba(255,255,255,0.06)",
//                 border: "1px solid rgba(255,255,255,0.12)",
//                 borderRadius: 6,
//                 fontSize: 12,
//                 fontWeight: 600,
//                 color: "rgba(255,255,255,0.9)",
//                 textTransform: "uppercase",
//               }}
//             >
//               {selectedModule}
//               {/* small dropdown arrow */}
//               <svg width="10" height="10" viewBox="0 0 24 24" fill="none">
//                 <path
//                   d="M6 9L12 15L18 9"
//                   stroke="rgba(255,255,255,0.4)"
//                   strokeWidth="2"
//                   strokeLinecap="round"
//                 />
//               </svg>
//             </div>
//           </div>
//         ) : (
//           /* Search bar on home view */
//           <div style={{ flex: 1, maxWidth: 480, position: "relative" }}>
//             <Search
//               size={13}
//               style={{
//                 position: "absolute",
//                 left: 10,
//                 top: "50%",
//                 transform: "translateY(-50%)",
//                 color: "rgba(255,255,255,0.2)",
//                 pointerEvents: "none",
//               }}
//             />
//             <input
//               type="text"
//               placeholder="Describe your task — e.g. Fix the authentication bug..."
//               value={taskInput}
//               onChange={(e) => setTaskInput(e.target.value)}
//               onKeyDown={(e) => e.key === "Enter" && handleAnalyze()}
//               style={{
//                 width: "100%",
//                 height: 32,
//                 background: "rgba(255,255,255,0.04)",
//                 border: "1px solid rgba(255,255,255,0.08)",
//                 borderRadius: 7,
//                 paddingLeft: 30,
//                 paddingRight: 12,
//                 color: "rgba(255,255,255,0.6)",
//                 fontSize: 12,
//                 outline: "none",
//                 fontFamily: "inherit",
//                 transition: "border-color 0.2s",
//               }}
//               onFocus={(e) =>
//                 (e.target.style.borderColor = "rgba(6,182,212,0.4)")
//               }
//               onBlur={(e) =>
//                 (e.target.style.borderColor = "rgba(255,255,255,0.08)")
//               }
//             />
//           </div>
//         )}
//       </div>

//       {/* Center — View Toggle */}
//       {onViewChange && (
//         <div
//           style={{
//             position: "absolute",
//             left: "50%",
//             transform: "translateX(-50%)",
//             display: "flex",
//             gap: 8,
//           }}
//         >
//           <button
//             onClick={() => onViewChange("constellation")}
//             style={{
//               display: "flex",
//               alignItems: "center",
//               gap: 6,
//               padding: "6px 14px",
//               background:
//                 currentView === "constellation" ? "#6d5ce7" : "transparent",
//               border: "1px solid rgba(109,92,231,0.4)",
//               borderRadius: 8,
//               color:
//                 currentView === "constellation"
//                   ? "#fff"
//                   : "rgba(255,255,255,0.5)",
//               fontSize: 12,
//               fontWeight: 600,
//               cursor: "pointer",
//               transition: "all 0.2s",
//             }}
//           >
//             <span style={{ fontSize: 14 }}>⭐</span>
//             Constellation
//           </button>
//           <button
//             onClick={() => onViewChange("levelMap")}
//             style={{
//               display: "flex",
//               alignItems: "center",
//               gap: 6,
//               padding: "6px 14px",
//               background:
//                 currentView === "levelMap" ? "#6d5ce7" : "transparent",
//               border: "1px solid rgba(109,92,231,0.4)",
//               borderRadius: 8,
//               color:
//                 currentView === "levelMap" ? "#fff" : "rgba(255,255,255,0.5)",
//               fontSize: 12,
//               fontWeight: 600,
//               cursor: "pointer",
//               transition: "all 0.2s",
//             }}
//           >
//             <span style={{ fontSize: 14 }}>📊</span>
//             Level Map
//           </button>
//         </div>
//       )}

//       {/* Right side — progress (when in module) + connection + analyze */}
//       <div
//         style={{
//           display: "flex",
//           alignItems: "center",
//           gap: 10,
//           flexShrink: 0,
//         }}
//       >
//         {/* Module progress pill (shown when inside a module) */}
//         {selectedModule && (
//           <div
//             style={{
//               display: "flex",
//               alignItems: "center",
//               gap: 10,
//               padding: "5px 14px",
//               background: "rgba(255,255,255,0.04)",
//               border: "1px solid rgba(255,255,255,0.08)",
//               borderRadius: 8,
//               fontSize: 12,
//             }}
//           >
//             <span
//               style={{ color: "rgba(255,255,255,0.5)", whiteSpace: "nowrap" }}
//             >
//               {selectedModule.toUpperCase()} onboarding
//               <span style={{ color: "rgba(255,255,255,0.8)", fontWeight: 600 }}>
//                 {" "}
//                 3 / 8 lessons
//               </span>
//             </span>
//             {/* Progress bar */}
//             <div
//               style={{
//                 width: 80,
//                 height: 4,
//                 background: "rgba(255,255,255,0.08)",
//                 borderRadius: 2,
//                 overflow: "hidden",
//               }}
//             >
//               <div
//                 style={{
//                   width: "37%",
//                   height: "100%",
//                   borderRadius: 2,
//                   background: "linear-gradient(90deg, #06b6d4, #6d5ce7)",
//                 }}
//               />
//             </div>
//             <span style={{ color: "#06b6d4", fontWeight: 700, fontSize: 12 }}>
//               37%
//             </span>
//           </div>
//         )}

//         {/* IBM Bob connection badge */}
//         <div
//           style={{
//             display: "flex",
//             alignItems: "center",
//             gap: 6,
//             padding: "4px 10px",
//             background: isConnected
//               ? "rgba(52,211,153,0.06)"
//               : "rgba(255,255,255,0.04)",
//             border: `1px solid ${isConnected ? "rgba(52,211,153,0.2)" : "rgba(255,255,255,0.08)"}`,
//             borderRadius: 6,
//             fontSize: 11,
//             fontWeight: 500,
//             color: isConnected ? "#34d399" : "rgba(255,255,255,0.3)",
//           }}
//         >
//           {isConnected ? <Wifi size={11} /> : <WifiOff size={11} />}
//           <span>{isConnected ? "IBM Bob Connected" : "Disconnected"}</span>
//           {isConnected && (
//             <span
//               style={{
//                 position: "relative",
//                 display: "inline-flex",
//                 width: 6,
//                 height: 6,
//               }}
//             >
//               <span
//                 style={{
//                   position: "absolute",
//                   inset: 0,
//                   borderRadius: "50%",
//                   background: "#34d399",
//                   opacity: 0.5,
//                   animation: "tnPing 1.6s ease-in-out infinite",
//                 }}
//               />
//               <span
//                 style={{
//                   width: 6,
//                   height: 6,
//                   borderRadius: "50%",
//                   background: "#34d399",
//                   position: "relative",
//                 }}
//               />
//             </span>
//           )}
//         </div>

//         {/* Analyze button */}
//         <button
//           onClick={handleAnalyze}
//           disabled={isAnalyzing}
//           style={{
//             display: "flex",
//             alignItems: "center",
//             gap: 6,
//             padding: "5px 13px",
//             background: isAnalyzing
//               ? "rgba(109,92,231,0.3)"
//               : "linear-gradient(135deg, #6d5ce7, #4f8ef7)",
//             border: "1px solid rgba(109,92,231,0.35)",
//             borderRadius: 7,
//             color: "#fff",
//             fontSize: 12,
//             fontWeight: 600,
//             cursor: isAnalyzing ? "not-allowed" : "pointer",
//             boxShadow: isAnalyzing ? "none" : "0 0 16px rgba(109,92,231,0.25)",
//             transition: "all 0.2s",
//             whiteSpace: "nowrap",
//           }}
//         >
//           {isAnalyzing ? (
//             <>
//               <Loader2
//                 size={12}
//                 style={{ animation: "tnSpin 1s linear infinite" }}
//               />{" "}
//               Analyzing...
//             </>
//           ) : (
//             <>
//               <svg width="11" height="11" viewBox="0 0 24 24" fill="none">
//                 <path
//                   d="M13 2L4.5 13.5H11L10 22L19.5 10.5H13L13 2Z"
//                   fill="white"
//                 />
//               </svg>{" "}
//               Analyze with IBM Bob
//             </>
//           )}
//         </button>

//         {/* Settings */}
//         <button
//           style={{
//             width: 30,
//             height: 30,
//             display: "flex",
//             alignItems: "center",
//             justifyContent: "center",
//             background: "transparent",
//             border: "1px solid rgba(255,255,255,0.08)",
//             borderRadius: 7,
//             cursor: "pointer",
//             color: "rgba(255,255,255,0.25)",
//             transition: "all 0.15s",
//           }}
//           onMouseEnter={(e) => {
//             (e.currentTarget as HTMLButtonElement).style.color =
//               "rgba(255,255,255,0.6)";
//           }}
//           onMouseLeave={(e) => {
//             (e.currentTarget as HTMLButtonElement).style.color =
//               "rgba(255,255,255,0.25)";
//           }}
//         >
//           <Settings size={13} />
//         </button>
//       </div>

//       <style>{`
//         @keyframes tnPing { 0%,100%{transform:scale(1);opacity:0.5} 50%{transform:scale(2);opacity:0} }
//         @keyframes tnSpin { to{transform:rotate(360deg)} }
//       `}</style>
//     </nav>
//   );
// }

// // Made with Bob
