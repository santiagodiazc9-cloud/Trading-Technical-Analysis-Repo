"use client";
import { useEffect, useRef } from "react";
import { createChart, ColorType, CandlestickSeries, LineSeries } from "lightweight-charts";

interface Bar {
  datetime: string;
  open: number;
  high: number;
  low: number;
  close: number;
  ema_9?: number | null;
  ema_21?: number | null;
  vwap?: number | null;
}

export default function CandleChart({ bars, symbol }: { bars: Bar[]; symbol: string }) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current || !bars.length) return;

    const chart = createChart(containerRef.current, {
      layout: { background: { type: ColorType.Solid, color: "#0f172a" }, textColor: "#94a3b8" },
      grid: { vertLines: { color: "#1e293b" }, horzLines: { color: "#1e293b" } },
      rightPriceScale: { borderColor: "#334155" },
      timeScale: { borderColor: "#334155", timeVisible: true },
      width: containerRef.current.clientWidth,
      height: 280,
    });

    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: "#10b981", downColor: "#ef4444",
      borderUpColor: "#10b981", borderDownColor: "#ef4444",
      wickUpColor: "#10b981", wickDownColor: "#ef4444",
    });

    const toTs = (dt: string) => Math.floor(new Date(dt).getTime() / 1000);

    candleSeries.setData(
      bars.map((b) => ({ time: toTs(b.datetime) as any, open: b.open, high: b.high, low: b.low, close: b.close }))
    );

    const ema9Series = chart.addSeries(LineSeries, { color: "#f59e0b", lineWidth: 1 });
    ema9Series.setData(
      bars.filter((b) => b.ema_9 != null).map((b) => ({ time: toTs(b.datetime) as any, value: b.ema_9! }))
    );

    const ema21Series = chart.addSeries(LineSeries, { color: "#3b82f6", lineWidth: 1 });
    ema21Series.setData(
      bars.filter((b) => b.ema_21 != null).map((b) => ({ time: toTs(b.datetime) as any, value: b.ema_21! }))
    );

    const vwapSeries = chart.addSeries(LineSeries, { color: "#a855f7", lineWidth: 1, lineStyle: 2 });
    vwapSeries.setData(
      bars.filter((b) => b.vwap != null).map((b) => ({ time: toTs(b.datetime) as any, value: b.vwap! }))
    );

    chart.timeScale().fitContent();

    const observer = new ResizeObserver(() => {
      if (containerRef.current) chart.applyOptions({ width: containerRef.current.clientWidth });
    });
    observer.observe(containerRef.current);

    return () => { chart.remove(); observer.disconnect(); };
  }, [bars]);

  return (
    <div className="rounded-lg overflow-hidden bg-slate-950 border border-slate-800">
      <div className="px-3 pt-2 pb-1 text-xs text-slate-400 flex gap-4">
        <span className="font-semibold text-white">{symbol} — 5 min</span>
        <span className="text-yellow-400">── EMA 9</span>
        <span className="text-blue-400">── EMA 21</span>
        <span className="text-purple-400">┄ VWAP</span>
      </div>
      <div ref={containerRef} />
    </div>
  );
}
