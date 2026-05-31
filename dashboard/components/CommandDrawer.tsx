"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import type { AgentDef, AgentStatus } from "@/lib/agents";
import { triggerRoutine, approveSetup, denySetup, pauseAgent, resumeAgent } from "@/lib/api";

const COLOR_HEX: Record<string, string> = {
  emerald: "#10b981",
  amber:   "#f59e0b",
  purple:  "#8b5cf6",
  blue:    "#3b82f6",
  orange:  "#f97316",
  cyan:    "#06b6d4",
};

const DESIGNATIONS: Record<string, string> = {
  "swing-trader": "SA-01",
  "day-trader":   "SA-02",
};

function routineLabel(path: string) {
  return path
    .split("/").pop()!
    .replace(/^\d+_/, "")
    .replace(/_/g, " ")
    .replace(/\.md$/, "")
    .toUpperCase();
}

interface SetupCard {
  setup_id: string;
  symbol: string;
  direction: string;
  confidence?: number;
  entry_low?: number;
  entry_high?: number;
  stop?: number;
  target_low?: number;
  target_high?: number;
}

interface DrawerProps {
  agent: AgentDef;
  live?: { status: AgentStatus; metric?: { label: string; value: string }; currentTask?: string };
  state: any;
  onClose: () => void;
  onRoutineLaunched?: (agentId: string, routinePath: string) => void;
}

export default function CommandDrawer({ agent, live, state, onClose, onRoutineLaunched }: DrawerProps) {
  const hex = COLOR_HEX[agent.color] ?? "#00d4ff";
  const status: AgentStatus = live?.status ?? agent.defaultStatus;
  const isActive = status === "active";
  const isPaused = status === "paused";
  const desig = DESIGNATIONS[agent.id] ?? "SA-XX";

  // Routine trigger state: routinePath → "idle" | "sending" | "queued" | "error"
  const [routineStates, setRoutineStates] = useState<Record<string, string>>({});

  // Setup states: setupId → "idle" | "approved" | "denied" | "sending"
  const [setupStates, setSetupStates] = useState<Record<string, string>>({});

  // Agent state toggle
  const [agentStateLoading, setAgentStateLoading] = useState(false);

  const pendingSetups: SetupCard[] = (state?.pending_setups ?? []).filter(
    (s: SetupCard) => !setupStates[s.setup_id] || setupStates[s.setup_id] === "idle"
  );

  const handleTrigger = async (routine: string) => {
    setRoutineStates(p => ({ ...p, [routine]: "sending" }));
    try {
      await triggerRoutine(routine);
      setRoutineStates(p => ({ ...p, [routine]: "queued" }));
      onRoutineLaunched?.(agent.id, routine);
      setTimeout(() => setRoutineStates(p => ({ ...p, [routine]: "idle" })), 3000);
    } catch {
      setRoutineStates(p => ({ ...p, [routine]: "error" }));
      setTimeout(() => setRoutineStates(p => ({ ...p, [routine]: "idle" })), 2000);
    }
  };

  const handleApprove = async (setupId: string) => {
    setSetupStates(p => ({ ...p, [setupId]: "sending" }));
    try {
      await approveSetup(setupId);
      setSetupStates(p => ({ ...p, [setupId]: "approved" }));
    } catch {
      setSetupStates(p => ({ ...p, [setupId]: "idle" }));
    }
  };

  const handleDeny = async (setupId: string) => {
    setSetupStates(p => ({ ...p, [setupId]: "sending" }));
    try {
      await denySetup(setupId);
      setSetupStates(p => ({ ...p, [setupId]: "denied" }));
    } catch {
      setSetupStates(p => ({ ...p, [setupId]: "idle" }));
    }
  };

  const handleAgentState = async () => {
    setAgentStateLoading(true);
    try {
      if (isPaused) await resumeAgent();
      else await pauseAgent("paused via mission control");
    } finally {
      setAgentStateLoading(false);
    }
  };

  return (
    <>
      {/* Backdrop */}
      <motion.div
        className="absolute inset-0 z-20"
        style={{ background: "rgba(0,3,10,0.5)", backdropFilter: "blur(2px)" }}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      />

      {/* Drawer */}
      <motion.div
        className="absolute right-0 top-0 bottom-0 z-30 w-[360px] flex flex-col overflow-hidden"
        style={{
          background: "linear-gradient(180deg, rgba(0,8,26,0.98) 0%, rgba(0,4,16,0.99) 100%)",
          borderLeft: `1px solid ${hex}30`,
          boxShadow: `-8px 0 40px rgba(0,0,0,0.6), -1px 0 0 ${hex}15`,
        }}
        initial={{ x: 360 }}
        animate={{ x: 0 }}
        exit={{ x: 360 }}
        transition={{ type: "spring", damping: 28, stiffness: 280 }}
      >
        {/* Header */}
        <div className="px-5 py-4 flex items-center gap-3"
          style={{ borderBottom: `1px solid ${hex}18` }}>

          {/* Status ring */}
          <div className="relative shrink-0">
            {isActive && (
              <span className="absolute inset-0 rounded-full animate-ping opacity-40"
                style={{ backgroundColor: hex }}/>
            )}
            <div className="w-3 h-3 rounded-full relative"
              style={{ backgroundColor: isActive ? hex : "transparent",
                border: `2px solid ${hex}`,
                boxShadow: isActive ? `0 0 8px ${hex}` : undefined }}/>
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-[9px] tracking-widest" style={{ color: `${hex}70` }}>{desig}</span>
              <span className="text-[11px] font-bold tracking-wider" style={{ color: hex }}>
                {agent.name.toUpperCase()}
              </span>
            </div>
            <p className="text-[9px] text-slate-700 tracking-widest mt-0.5">
              {status === "active" ? "ORBIT NOMINAL" : status === "idle" ? "STANDBY ORBIT" : status.toUpperCase()}
            </p>
          </div>

          {live?.metric && (
            <div className="text-right shrink-0">
              <p className="text-[8px] text-slate-700">{live.metric.label}</p>
              <p className="text-base font-bold" style={{ color: hex }}>{live.metric.value}</p>
            </div>
          )}

          <button onClick={onClose}
            className="ml-2 w-7 h-7 flex items-center justify-center rounded text-slate-600 hover:text-slate-300 transition-colors text-lg shrink-0"
            style={{ border: "1px solid rgba(255,255,255,0.06)" }}>
            ✕
          </button>
        </div>

        {/* Scrollable body */}
        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-5">

          {/* ── INITIATE SEQUENCE ─────────────────────── */}
          {agent.routines && agent.routines.length > 0 && (
            <section>
              <p className="text-[8px] tracking-[0.3em] text-slate-700 mb-2.5 flicker">
                INITIATE SEQUENCE
              </p>
              <div className="space-y-1.5">
                {agent.routines.map(routine => {
                  const rs = routineStates[routine] ?? "idle";
                  return (
                    <button key={routine}
                      onClick={() => handleTrigger(routine)}
                      disabled={rs === "sending"}
                      className="w-full flex items-center gap-3 px-3 py-2 rounded-sm text-left transition-all"
                      style={{
                        background: rs === "queued" ? `${hex}15` : "rgba(0,8,24,0.6)",
                        border: `1px solid ${rs === "queued" ? hex + "40" : "rgba(255,255,255,0.06)"}`,
                        opacity: rs === "sending" ? 0.6 : 1,
                      }}
                    >
                      <span style={{ color: rs === "queued" ? hex : "#475569" }}>
                        {rs === "sending" ? "◌" : rs === "queued" ? "✓" : rs === "error" ? "✕" : "▸"}
                      </span>
                      <span className="text-[9px] tracking-wider flex-1"
                        style={{ color: rs === "queued" ? hex : "#94a3b8" }}>
                        {routineLabel(routine)}
                      </span>
                      <span className="text-[8px] tracking-widest"
                        style={{ color: rs === "queued" ? hex : "#334155" }}>
                        {rs === "queued" ? "QUEUED" : rs === "sending" ? "..." : "LAUNCH"}
                      </span>
                    </button>
                  );
                })}
              </div>
            </section>
          )}

          {/* ── AGENT STATE ───────────────────────────── */}
          <section>
            <p className="text-[8px] tracking-[0.3em] text-slate-700 mb-2.5 flicker">
              AGENT STATE
            </p>
            <button
              onClick={handleAgentState}
              disabled={agentStateLoading || !live}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-sm transition-all"
              style={{
                background: isPaused ? "rgba(16,185,129,0.08)" : "rgba(239,68,68,0.06)",
                border: `1px solid ${isPaused ? "rgba(16,185,129,0.25)" : "rgba(239,68,68,0.2)"}`,
                opacity: (!live || agentStateLoading) ? 0.4 : 1,
              }}
            >
              <span style={{ color: isPaused ? "#10b981" : "#ef4444", fontSize: 14 }}>
                {isPaused ? "▶" : "⏸"}
              </span>
              <span className="text-[9px] tracking-widest"
                style={{ color: isPaused ? "#10b981" : "#ef4444" }}>
                {agentStateLoading ? "TRANSMITTING..." : isPaused ? "RESUME AGENT" : "PAUSE AGENT"}
              </span>
            </button>
            {!live && (
              <p className="text-[8px] text-slate-700 mt-1 px-1">
                Live data unavailable — state toggle disabled
              </p>
            )}
          </section>

          {/* ── PENDING MISSIONS ──────────────────────── */}
          {pendingSetups.length > 0 && (
            <section>
              <p className="text-[8px] tracking-[0.3em] text-slate-700 mb-2.5 flicker">
                PENDING MISSIONS
              </p>
              <div className="space-y-2">
                {pendingSetups.map((setup: SetupCard) => {
                  const ss = setupStates[setup.setup_id] ?? "idle";
                  const resolved = ss === "approved" || ss === "denied";
                  return (
                    <div key={setup.setup_id}
                      className="rounded-sm px-3 py-3"
                      style={{
                        background: resolved
                          ? (ss === "approved" ? "rgba(16,185,129,0.08)" : "rgba(239,68,68,0.06)")
                          : "rgba(0,8,24,0.7)",
                        border: `1px solid ${resolved
                          ? (ss === "approved" ? "rgba(16,185,129,0.25)" : "rgba(239,68,68,0.2)")
                          : "rgba(255,255,255,0.06)"}`,
                      }}>

                      {/* Setup header */}
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-base font-bold" style={{ color: hex }}>
                          {setup.symbol}
                        </span>
                        <span className="text-[8px] px-1.5 py-0.5 rounded-sm font-bold tracking-wider"
                          style={{
                            background: setup.direction === "LONG" ? "rgba(16,185,129,0.15)" : "rgba(239,68,68,0.15)",
                            color: setup.direction === "LONG" ? "#10b981" : "#ef4444",
                            border: `1px solid ${setup.direction === "LONG" ? "rgba(16,185,129,0.3)" : "rgba(239,68,68,0.3)"}`,
                          }}>
                          {setup.direction}
                        </span>
                        {setup.confidence && (
                          <span className="ml-auto text-[9px] text-slate-600">
                            {setup.confidence}/10
                          </span>
                        )}
                      </div>

                      {/* Price levels */}
                      {(setup.entry_low || setup.stop || setup.target_low) && (
                        <div className="grid grid-cols-3 gap-1 mb-2.5 text-[8px]">
                          {setup.entry_low && (
                            <div>
                              <p className="text-slate-700">ENTRY</p>
                              <p className="text-slate-400">${setup.entry_low}–{setup.entry_high}</p>
                            </div>
                          )}
                          {setup.stop && (
                            <div>
                              <p className="text-slate-700">STOP</p>
                              <p className="text-red-500">${setup.stop}</p>
                            </div>
                          )}
                          {setup.target_low && (
                            <div>
                              <p className="text-slate-700">TARGET</p>
                              <p className="text-emerald-500">${setup.target_low}</p>
                            </div>
                          )}
                        </div>
                      )}

                      {/* Action buttons */}
                      {resolved ? (
                        <div className="text-center text-[9px] font-bold tracking-widest py-1"
                          style={{ color: ss === "approved" ? "#10b981" : "#ef4444" }}>
                          {ss === "approved" ? "✓ MISSION APPROVED" : "✕ MISSION DENIED"}
                        </div>
                      ) : (
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleApprove(setup.setup_id)}
                            disabled={ss === "sending"}
                            className="flex-1 py-1.5 rounded-sm text-[9px] font-bold tracking-widest transition-all"
                            style={{
                              background: "rgba(16,185,129,0.12)",
                              border: "1px solid rgba(16,185,129,0.3)",
                              color: "#10b981",
                              opacity: ss === "sending" ? 0.5 : 1,
                            }}>
                            ✓ APPROVE
                          </button>
                          <button
                            onClick={() => handleDeny(setup.setup_id)}
                            disabled={ss === "sending"}
                            className="flex-1 py-1.5 rounded-sm text-[9px] font-bold tracking-widest transition-all"
                            style={{
                              background: "rgba(239,68,68,0.08)",
                              border: "1px solid rgba(239,68,68,0.25)",
                              color: "#ef4444",
                              opacity: ss === "sending" ? 0.5 : 1,
                            }}>
                            ✕ DENY
                          </button>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </section>
          )}
        </div>

        {/* Footer */}
        <div className="px-5 py-3" style={{ borderTop: `1px solid ${hex}18` }}>
          <Link href={`/agents/${agent.id}`}
            className="flex items-center justify-between w-full px-3 py-2 rounded-sm text-[9px] tracking-widest transition-all"
            style={{
              background: "rgba(0,8,24,0.6)",
              border: `1px solid ${hex}20`,
              color: hex,
            }}>
            <span>OPEN FULL COMMAND CENTER</span>
            <span>→</span>
          </Link>
        </div>
      </motion.div>
    </>
  );
}
