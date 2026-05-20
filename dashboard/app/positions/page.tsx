import { fetchState } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function PositionsPage() {
  let state: any = null;
  try { state = await fetchState(); } catch {}

  const positions: any[] = state?.positions ?? [];

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-lg font-semibold text-white">Open Positions</h1>

      {positions.length === 0 && (
        <div className="bg-slate-900 rounded-lg p-6 border border-slate-800 text-center text-slate-500 text-sm">
          No open positions.
        </div>
      )}

      {positions.map((p: any) => {
        const unrealizedPl = parseFloat(p.unrealized_pl ?? 0);
        const unrealizedPlPct = parseFloat(p.unrealized_plpc ?? 0) * 100;
        const positive = unrealizedPl >= 0;
        return (
          <div key={p.symbol} className="bg-slate-900 rounded-lg p-4 border border-slate-800">
            <div className="flex items-start justify-between mb-2">
              <div>
                <span className="font-bold text-white">{p.symbol}</span>
                <span className="ml-2 text-xs text-slate-500">{p.qty} shares</span>
              </div>
              <div className={`text-right ${positive ? "text-emerald-400" : "text-red-400"}`}>
                <div className="font-semibold">{positive ? "+" : ""}${Math.abs(unrealizedPl).toFixed(2)}</div>
                <div className="text-xs">{positive ? "+" : ""}{unrealizedPlPct.toFixed(2)}%</div>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-2 text-xs">
              <div><span className="text-slate-500">Avg entry</span><br /><span className="text-white">${parseFloat(p.avg_entry_price ?? 0).toFixed(2)}</span></div>
              <div><span className="text-slate-500">Current</span><br /><span className="text-white">${parseFloat(p.current_price ?? 0).toFixed(2)}</span></div>
              <div><span className="text-slate-500">Market val</span><br /><span className="text-white">${parseFloat(p.market_value ?? 0).toFixed(0)}</span></div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
