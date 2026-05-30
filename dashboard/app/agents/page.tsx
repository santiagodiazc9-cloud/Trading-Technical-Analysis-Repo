import Link from "next/link";
import { AGENTS } from "@/lib/agents";

export default function AgentsIndexPage() {
  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold text-white">Agent Roster</h1>
        <Link href="/" className="text-xs text-slate-500 hover:text-white">← Fleet</Link>
      </div>
      <p className="text-sm text-slate-400">
        Add a new agent by wiring a config entry in <code className="text-slate-300">dashboard/lib/agents.ts</code> and
        an API data source in <code className="text-slate-300">api/main.py /agents</code>.
      </p>
      <div className="flex flex-col gap-2">
        {AGENTS.map((a) => (
          <Link
            key={a.id}
            href={`/agents/${a.id}`}
            className="flex items-center gap-3 rounded-lg border border-slate-800 bg-[#0f1318] p-3 hover:border-slate-600 transition-colors"
          >
            <span className="text-xl">{a.icon}</span>
            <div>
              <div className="text-sm font-medium text-white">{a.name}</div>
              <div className="text-xs text-slate-500">{a.description}</div>
            </div>
            <span className="ml-auto text-xs text-slate-600">
              {a.stub ? "stub" : "live"}
            </span>
          </Link>
        ))}
      </div>
    </div>
  );
}
