import { fetchState } from "@/lib/api";
import PostureBar from "@/components/PostureBar";
import Link from "next/link";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  let state: any = null;
  let error = "";
  try {
    state = await fetchState();
  } catch {
    error = "API offline — start the backend with: uvicorn api.main:app --port 8000";
  }

  if (error || !state) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4 text-center">
        <div className="text-4xl">⚠️</div>
        <p className="text-slate-400 text-sm max-w-sm">{error}</p>
      </div>
    );
  }

  const account = state.account ?? {};
  const equity = parseFloat(account.equity ?? 0);
  const cash = parseFloat(account.cash ?? 0);
  const dayPl = equity - parseFloat(account.last_equity ?? equity);
  const dayPlPct = equity > 0 ? (dayPl / equity) * 100 : 0;
  const positions: any[] = state.positions ?? [];
  const pendingSetups: any[] = state.pending_setups ?? [];
  const session = state.day_trading_session ?? {};
  const paused = state.paused ?? false;

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold text-white">Trading Agent</h1>
        <span className={`text-xs px-2 py-1 rounded-full ${paused ? "bg-yellow-500/20 text-yellow-400" : "bg-emerald-500/20 text-emerald-400"}`}>
          {paused ? "⏸ Paused" : "● Live"}
        </span>
      </div>

      <PostureBar posture={state.market_posture ?? "UNKNOWN"} />

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <StatCard label="Equity" value={`$${equity.toLocaleString("en-US", { maximumFractionDigits: 0 })}`} />
        <StatCard label="Cash" value={`$${cash.toLocaleString("en-US", { maximumFractionDigits: 0 })}`} />
        <StatCard
          label="Day P&L"
          value={`${dayPl >= 0 ? "+" : ""}$${Math.abs(dayPl).toLocaleString("en-US", { maximumFractionDigits: 0 })}`}
          sub={`${dayPlPct >= 0 ? "+" : ""}${dayPlPct.toFixed(2)}%`}
          color={dayPl >= 0 ? "text-emerald-400" : "text-red-400"}
        />
        <StatCard label="Positions" value={String(positions.length)} sub={`${pendingSetups.length} pending`} />
      </div>

      <div className="grid grid-cols-2 gap-3">
        <QuickCard href="/swing" icon="↗" title="Swing Setups"
          count={pendingSetups.filter((s) => s.approved === "PENDING").length}
          label="awaiting approval" />
        <QuickCard href="/daytrader" icon="⚡" title="Day Engine"
          count={session.session_approved ? (session.trades_taken ?? 0) : 0}
          label={session.session_approved ? `${session.trades_taken}/${session.max_trades} trades` : "session off"}
          active={session.session_approved} />
        <QuickCard href="/positions" icon="◈" title="Open Positions" count={positions.length} label="holdings" />
        <QuickCard href="/settings" icon="⚙" title="Settings"
          count={state.watchlist_count ?? 0} label="symbols tracked" />
      </div>
    </div>
  );
}

function StatCard({ label, value, sub, color = "text-white" }: {
  label: string; value: string; sub?: string; color?: string;
}) {
  return (
    <div className="bg-slate-900 rounded-lg p-3 border border-slate-800">
      <div className="text-xs text-slate-500 mb-1">{label}</div>
      <div className={`text-lg font-semibold ${color}`}>{value}</div>
      {sub && <div className="text-xs text-slate-500 mt-0.5">{sub}</div>}
    </div>
  );
}

function QuickCard({ href, icon, title, count, label, active }: {
  href: string; icon: string; title: string; count: number; label: string; active?: boolean;
}) {
  return (
    <Link href={href}
      className="bg-slate-900 rounded-lg p-3 border border-slate-800 hover:border-slate-600 transition-colors flex items-start gap-3">
      <span className="text-2xl">{icon}</span>
      <div>
        <div className="text-sm font-medium text-white">{title}</div>
        <div className={`text-lg font-bold ${active === false ? "text-slate-500" : "text-emerald-400"}`}>{count}</div>
        <div className="text-xs text-slate-500">{label}</div>
      </div>
    </Link>
  );
}
