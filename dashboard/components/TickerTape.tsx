"use client";

import { useEffect, useState } from "react";
import { fetchState } from "@/lib/api";

interface Chip {
  symbol: string;
  price: number;
  pctChange: number;
  isPosition: boolean;
}

const WATCHLIST_SYMBOLS = ["SPY", "QQQ", "XLK", "GOOGL", "NVDA", "AMZN", "MSFT", "META"];

export default function TickerTape() {
  const [chips, setChips] = useState<Chip[]>([]);

  useEffect(() => {
    const load = async () => {
      try {
        const state = await fetchState();
        const result: Chip[] = [];

        // Open positions first
        const positions: any[] = state?.positions ?? [];
        for (const p of positions) {
          result.push({
            symbol: p.symbol,
            price: parseFloat(p.current_price ?? 0),
            pctChange: parseFloat(p.unrealized_pnl_pct ?? 0),
            isPosition: true,
          });
        }

        // Add placeholder market data for watchlist symbols
        // (Alpaca snapshot would need a separate endpoint; use bars data as fallback)
        for (const sym of WATCHLIST_SYMBOLS) {
          if (result.find(c => c.symbol === sym)) continue;
          result.push({
            symbol: sym,
            price: 0,
            pctChange: 0,
            isPosition: false,
          });
        }

        setChips(result);
      } catch { /* fail silently */ }
    };
    load();
    const id = setInterval(load, 30_000);
    return () => clearInterval(id);
  }, []);

  if (chips.length === 0) return null;

  // Duplicate chips for seamless loop
  const doubled = [...chips, ...chips];

  return (
    <div
      className="shrink-0 h-7 overflow-hidden relative"
      style={{
        background: "rgba(0,4,14,0.95)",
        borderBottom: "1px solid rgba(0,212,255,0.06)",
      }}
    >
      {/* Left fade */}
      <div className="absolute left-0 top-0 bottom-0 w-12 z-10 pointer-events-none"
        style={{ background: "linear-gradient(90deg, rgba(0,4,14,1) 0%, transparent 100%)" }}/>
      <div className="absolute right-0 top-0 bottom-0 w-12 z-10 pointer-events-none"
        style={{ background: "linear-gradient(90deg, transparent 0%, rgba(0,4,14,1) 100%)" }}/>

      {/* Label */}
      <div className="absolute left-3 top-0 bottom-0 z-20 flex items-center gap-1.5">
        <span className="w-1 h-1 rounded-full bg-emerald-500 animate-ping opacity-60"/>
        <span className="text-[8px] tracking-[0.2em] text-slate-700">LIVE</span>
      </div>

      <div className="ticker-track h-full items-center pl-20">
        {doubled.map((chip, i) => {
          const positive = chip.pctChange >= 0;
          const color = chip.isPosition
            ? (positive ? "#10b981" : "#ef4444")
            : "#475569";
          return (
            <div key={i} className="flex items-center gap-2 px-4 h-full border-r border-[rgba(0,212,255,0.06)] shrink-0">
              <span className="text-[9px] font-bold tracking-widest"
                style={{ color: chip.isPosition ? color : "#64748b" }}>
                {chip.symbol}
              </span>
              {chip.price > 0 && (
                <>
                  <span className="text-[9px] tabular-nums" style={{ color: "#94a3b8" }}>
                    ${chip.price.toFixed(2)}
                  </span>
                  <span className="text-[9px] font-bold tabular-nums" style={{ color }}>
                    {positive ? "▲" : "▼"} {Math.abs(chip.pctChange).toFixed(2)}%
                  </span>
                </>
              )}
              {chip.price === 0 && (
                <span className="text-[9px] text-slate-800">——</span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
