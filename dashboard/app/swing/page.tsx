"use client";
import { useState, useEffect } from "react";
import { fetchState, approveSetup, denySetup } from "@/lib/api";

export default function SwingPage() {
  const [state, setState] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [actioning, setActioning] = useState<string | null>(null);

  const load = async () => {
    try {
      const s = await fetchState();
      setState(s);
    } catch {}
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  const handleApprove = async (id: string) => {
    setActioning(id);
    await approveSetup(id);
    await load();
    setActioning(null);
  };

  const handleDeny = async (id: string) => {
    setActioning(id);
    const reason = window.prompt("Reason for denial (optional)") ?? "denied via dashboard";
    await denySetup(id, reason);
    await load();
    setActioning(null);
  };

  if (loading) return <Skeleton />;

  const setups: any[] = state?.pending_setups ?? [];

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-lg font-semibold text-white">Swing Setups</h1>

      {setups.length === 0 && (
        <div className="bg-slate-900 rounded-lg p-6 border border-slate-800 text-center text-slate-500 text-sm">
          No pending setups. The pre-market routine will populate these.
        </div>
      )}

      {setups.map((s) => (
        <SetupCard key={s.setup_id} setup={s}
          onApprove={() => handleApprove(s.setup_id)}
          onDeny={() => handleDeny(s.setup_id)}
          actioning={actioning === s.setup_id} />
      ))}
    </div>
  );
}

function SetupCard({ setup, onApprove, onDeny, actioning }: {
  setup: any; onApprove: () => void; onDeny: () => void; actioning: boolean;
}) {
  const approved = setup.approved;
  const isLong = setup.direction === "LONG";
  const dirColor = isLong ? "text-emerald-400" : "text-red-400";
  const statusBg = approved === "YES" ? "bg-emerald-500/10 border-emerald-500/30"
    : approved === "NO" ? "bg-red-500/10 border-red-500/30"
    : "bg-slate-900 border-slate-800";

  return (
    <div className={`rounded-lg p-4 border ${statusBg}`}>
      <div className="flex items-start justify-between mb-3">
        <div>
          <span className="font-bold text-white text-base">{setup.symbol}</span>
          <span className={`ml-2 text-sm font-semibold ${dirColor}`}>{setup.direction}</span>
          <div className="text-xs text-slate-500 mt-0.5">{setup.setup_id}</div>
        </div>
        <StatusBadge status={approved} />
      </div>

      <div className="grid grid-cols-3 gap-2 text-xs mb-3">
        <Field label="Entry" value={`$${setup.entry_low}–$${setup.entry_high}`} />
        <Field label="Stop" value={`$${setup.stop}`} color="text-red-400" />
        <Field label="Target" value={`$${setup.target_low}–$${setup.target_high}`} color="text-emerald-400" />
      </div>

      {approved === "PENDING" && (
        <div className="flex gap-2 mt-2">
          <button onClick={onApprove} disabled={actioning}
            className="flex-1 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-black text-sm font-semibold disabled:opacity-50 transition-colors">
            {actioning ? "…" : "✓ Approve"}
          </button>
          <button onClick={onDeny} disabled={actioning}
            className="flex-1 py-2 rounded-lg bg-red-500/20 hover:bg-red-500/30 text-red-400 text-sm font-semibold disabled:opacity-50 transition-colors">
            {actioning ? "…" : "✗ Deny"}
          </button>
        </div>
      )}
    </div>
  );
}

function Field({ label, value, color = "text-white" }: { label: string; value: string; color?: string }) {
  return (
    <div>
      <div className="text-slate-500">{label}</div>
      <div className={`font-medium ${color}`}>{value}</div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  if (status === "YES") return <span className="text-xs bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded-full">Approved</span>;
  if (status === "NO") return <span className="text-xs bg-red-500/20 text-red-400 px-2 py-0.5 rounded-full">Denied</span>;
  return <span className="text-xs bg-yellow-500/20 text-yellow-400 px-2 py-0.5 rounded-full">Pending</span>;
}

function Skeleton() {
  return (
    <div className="flex flex-col gap-4">
      <div className="h-7 w-32 bg-slate-800 rounded animate-pulse" />
      {[1, 2].map((i) => <div key={i} className="h-36 bg-slate-900 rounded-lg border border-slate-800 animate-pulse" />)}
    </div>
  );
}
