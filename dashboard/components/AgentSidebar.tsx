"use client";

import { motion } from "framer-motion";
import type { AgentDef, AgentStatus } from "@/lib/agents";

const COLOR_HEX: Record<string, string> = {
  emerald: "#10b981",
  amber:   "#f59e0b",
  purple:  "#8b5cf6",
  blue:    "#3b82f6",
  orange:  "#f97316",
  cyan:    "#06b6d4",
};

const STATUS_LABEL: Record<AgentStatus, string> = {
  active:  "ORBIT NOMINAL",
  idle:    "STANDBY ORBIT",
  paused:  "TRAJECTORY HOLD",
  offline: "SIGNAL LOST",
  stub:    "UNDEPLOYED",
};

const DESIGNATIONS = ["SA-01", "SA-02", "SA-03", "SA-04", "SA-05", "SA-06"];

function AgentRow({ agent, live, index }: {
  agent: AgentDef;
  live?: { status: AgentStatus; metric?: { label: string; value: string }; currentTask?: string };
  index: number;
}) {
  const status: AgentStatus = live?.status ?? agent.defaultStatus;
  const metric = live?.metric ?? agent.metric;
  const task = live?.currentTask ?? agent.currentTask ?? "STANDBY";
  const hex = COLOR_HEX[agent.color] ?? "#64748b";
  const isActive = status === "active";
  const isIdle   = status === "idle";
  const isLive   = isActive || isIdle;
  const desig    = DESIGNATIONS[index] ?? `SA-0${index + 1}`;

  return (
    <motion.div
      initial={{ opacity: 0, x: -16 }}
      animate={{ opacity: isLive ? 1 : 0.28 }}
      transition={{ delay: index * 0.07 }}
      className="mx-2 rounded-sm px-3 py-2.5 relative overflow-hidden cursor-pointer"
      style={{
        borderLeft: `2px solid ${isActive ? hex : isIdle ? hex + "60" : "#1e293b"}`,
        background: isActive ? `${hex}06` : "rgba(0,0,0,0)",
      }}
      whileHover={{ background: `rgba(0,0,0,0)` }}
    >
      {/* Active glow sweep */}
      {isActive && (
        <div className="absolute inset-0 pointer-events-none"
          style={{ background: `linear-gradient(90deg, ${hex}08 0%, transparent 70%)` }}/>
      )}

      {/* Row 1: designation + name + status dot */}
      <div className="flex items-center gap-2">
        <span className="text-[8px] font-bold tracking-wider" style={{ color: `${hex}70` }}>
          {desig}
        </span>
        <span className="text-[10px] font-bold tracking-wider" style={{ color: isLive ? hex : "#334155" }}>
          {agent.name.toUpperCase()}
        </span>
        <span className="ml-auto relative flex h-2 w-2 shrink-0">
          {isActive && (
            <span className="absolute inline-flex h-full w-full rounded-full animate-ping opacity-60"
              style={{ backgroundColor: hex }}/>
          )}
          <span className="relative inline-flex rounded-full h-2 w-2"
            style={{
              backgroundColor: isLive ? hex : "rgba(0,0,0,0)",
              border: `1.5px solid ${isLive ? hex : "#1e293b"}`,
            }}/>
        </span>
      </div>

      {/* Row 2: status text */}
      <div className="mt-0.5 pl-[42px] text-[8px] tracking-wider" style={{ color: `${hex}55` }}>
        {STATUS_LABEL[status]}
      </div>

      {/* Row 3: current task */}
      {isLive && (
        <div className="mt-1.5 pl-[42px] text-[9px] tracking-wide truncate" style={{ color: "#475569" }}>
          ▸ <span className="cursor">{task}</span>
        </div>
      )}

      {/* Row 4: metric */}
      {isLive && (
        <div className="mt-1 pl-[42px] flex items-center gap-1.5">
          <span className="text-[8px] text-slate-700">{metric.label.toUpperCase()}</span>
          <span className="text-[11px] font-bold" style={{ color: hex }}>{metric.value}</span>
        </div>
      )}
    </motion.div>
  );
}

interface SidebarProps {
  agents: AgentDef[];
  liveMap: Record<string, { status: AgentStatus; metric?: { label: string; value: string }; currentTask?: string }>;
  onSelectAgent?: (id: string) => void;
}

export default function AgentSidebar({ agents, liveMap, onSelectAgent }: SidebarProps) {
  return (
    <aside className="w-[268px] shrink-0 flex flex-col overflow-hidden"
      style={{
        background: "linear-gradient(180deg, rgba(0,8,24,0.95) 0%, rgba(0,4,16,0.98) 100%)",
        borderRight: "1px solid rgba(0,212,255,0.08)",
      }}>

      {/* Header */}
      <div className="px-4 py-3 border-b border-[rgba(0,212,255,0.07)]">
        <div className="flex items-center gap-2">
          <div className="w-1 h-1 rounded-full bg-[#00d4ff] animate-ping opacity-70"/>
          <p className="text-[9px] tracking-[0.3em] text-[#00d4ff] opacity-60 flicker">
            CREW MANIFEST
          </p>
        </div>
        <p className="text-[8px] text-slate-800 mt-0.5 tracking-widest">
          MISSION CONTROL · SECTOR ALPHA
        </p>
      </div>

      {/* Agent list */}
      <div className="flex-1 overflow-y-auto py-2 space-y-0.5">
        {agents.map((agent, i) => (
          <div key={agent.id} onClick={() => !agent.stub && onSelectAgent?.(agent.id)}
            style={{ cursor: agent.stub ? "default" : "pointer" }}>
          <AgentRow
            agent={agent}
            live={liveMap[agent.id]}
            index={i}
          />
          </div>
        ))}
      </div>

      {/* Footer telemetry bar */}
      <div className="px-4 py-2.5 border-t border-[rgba(0,212,255,0.06)] space-y-1.5">
        {[
          { label: "FLEET STATUS", val: "2 ACTIVE · 4 STAGED", col: "#10b981" },
          { label: "COMMS", val: "DISCORD RELAY ONLINE", col: "#00d4ff" },
          { label: "UPLINK", val: "GHA FAILSAFE ARMED", col: "#ffd700" },
        ].map(row => (
          <div key={row.label} className="flex justify-between items-center">
            <span className="text-[8px] tracking-wider text-slate-700">{row.label}</span>
            <span className="text-[8px] tracking-wide" style={{ color: row.col }}>{row.val}</span>
          </div>
        ))}
      </div>
    </aside>
  );
}
