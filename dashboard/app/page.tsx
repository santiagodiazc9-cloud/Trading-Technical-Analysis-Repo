import { fetchState, fetchAgents } from "@/lib/api";
import { AGENTS } from "@/lib/agents";
import type { AgentStatus } from "@/lib/agents";
import AgentCard from "@/components/AgentCard";
import ClockWidget from "@/components/ClockWidget";
import Link from "next/link";

export const dynamic = "force-dynamic";

export default async function FleetPage() {
  let state: any = null;
  let liveAgents: any[] = [];

  try {
    [state, liveAgents] = await Promise.all([fetchState(), fetchAgents()]);
  } catch {
    // API offline — render shell with offline indicators
  }

  const liveMap = Object.fromEntries(liveAgents.map((a: any) => [a.id, a]));

  const equity = parseFloat(state?.account?.equity ?? 0);
  const lastEq = parseFloat(state?.account?.last_equity ?? equity);
  const netPl = equity - lastEq;
  const netPlStr = `${netPl >= 0 ? "+" : ""}$${Math.abs(netPl).toLocaleString("en-US", { maximumFractionDigits: 0 })}`;

  const activeCount = liveAgents.filter((a: any) => a.status === "active").length;
  const offlineCount = AGENTS.length - activeCount;

  return (
    <div className="flex flex-col gap-3">
      {/* ── Fleet header ─────────────────────────────────────────────── */}
      <div className="sticky top-0 z-10 bg-[#0A0D12] border-b border-slate-800 -mx-3 px-3 py-2 flex items-center justify-between gap-2 text-xs">
        <div className="flex items-center gap-2 font-bold text-white">
          <span className="text-emerald-400">◉</span>
          <span className="tracking-widest">AGENT FLEET</span>
        </div>
        <div className="flex items-center gap-3 text-slate-400">
          {activeCount > 0 && (
            <span className="text-emerald-400">
              ● {activeCount} ACTIVE
            </span>
          )}
          {offlineCount > 0 && (
            <span>○ {offlineCount} OFFLINE</span>
          )}
          {state && (
            <span>
              NET P&amp;L:{" "}
              <span className={netPl >= 0 ? "text-emerald-400" : "text-red-400"}>
                {netPlStr}
              </span>
            </span>
          )}
          <ClockWidget />
        </div>
      </div>

      {/* ── Agent grid ───────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {AGENTS.map((agent) => {
          const live = liveMap[agent.id];
          return (
            <AgentCard
              key={agent.id}
              agent={agent}
              liveStatus={live?.status as AgentStatus | undefined}
              liveMetric={live?.metric}
            />
          );
        })}

        {/* Deploy slot */}
        <Link
          href="/agents"
          className="flex flex-col items-center justify-center gap-2 rounded-lg p-3 border border-dashed border-slate-700 bg-[#0f1318] hover:border-slate-500 transition-colors text-slate-600 hover:text-slate-400 min-h-[120px]"
        >
          <span className="text-2xl">+</span>
          <span className="text-[10px] tracking-wider">DEPLOY AGENT</span>
        </Link>
      </div>
    </div>
  );
}
