import Link from "next/link";
import type { AgentDef, AgentStatus } from "@/lib/agents";
import StatusRing from "./StatusRing";

const GLOW_COLOR: Record<string, string> = {
  emerald: "#10b981",
  amber:   "#f59e0b",
  purple:  "#8b5cf6",
  blue:    "#3b82f6",
  orange:  "#f97316",
  cyan:    "#06b6d4",
};

const STATUS_LABEL: Record<AgentStatus, string> = {
  active:  "ACTIVE",
  idle:    "IDLE",
  paused:  "PAUSED",
  offline: "OFFLINE",
  stub:    "STUB",
};

export default function AgentCard({
  agent,
  liveStatus,
  liveMetric,
}: {
  agent: AgentDef;
  liveStatus?: AgentStatus;
  liveMetric?: { label: string; value: string };
}) {
  const status = liveStatus ?? agent.defaultStatus;
  const metric = liveMetric ?? agent.metric;
  const glow = GLOW_COLOR[agent.color] ?? "#475569";
  const href = agent.stub ? `/agents/${agent.id}` : (agent.detailRoute ?? `/agents/${agent.id}`);
  const isActive = status === "active";

  return (
    <Link
      href={href}
      className="relative flex flex-col gap-2 rounded-lg p-3 border border-slate-800 bg-[#0f1318] hover:border-slate-600 transition-all cursor-pointer overflow-hidden"
      style={{
        boxShadow: isActive ? `0 0 14px 2px ${glow}33, inset 0 0 20px ${glow}0a` : "none",
        borderColor: isActive ? `${glow}66` : undefined,
      }}
    >
      {/* Top row: status + name + pixel art */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex flex-col gap-1 min-w-0">
          <div className="flex items-center gap-1.5">
            <StatusRing status={status} color={agent.color} />
            <span className="text-[10px] font-bold tracking-widest text-slate-400">
              {STATUS_LABEL[status]}
            </span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-base leading-none">{agent.icon}</span>
            <span className="text-sm font-semibold text-white truncate">{agent.name}</span>
          </div>
        </div>
        {/* Pixel art character */}
        <div
          className="flex-shrink-0 opacity-90"
          dangerouslySetInnerHTML={{ __html: agent.pixelArt }}
          style={{ imageRendering: "pixelated", width: 32, height: 32 }}
        />
      </div>

      {/* Description */}
      <p className="text-xs text-slate-500 leading-tight">{agent.description}</p>

      {/* Metric */}
      {!agent.stub ? (
        <div className="flex items-baseline gap-1">
          <span className="text-xs text-slate-500">{metric.label}:</span>
          <span
            className="text-sm font-bold"
            style={{ color: glow }}
          >
            {metric.value}
          </span>
        </div>
      ) : (
        <div className="text-xs text-slate-600 italic">{agent.stub.tagline}</div>
      )}

      {/* CTA */}
      <div className="text-[10px] text-slate-500 mt-auto">
        {agent.stub ? "Configure →" : "Enter →"}
      </div>
    </Link>
  );
}
