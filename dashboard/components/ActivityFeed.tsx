"use client";

import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { fetchEvents } from "@/lib/api";

interface FeedEvent { time: string; agent: string; message: string; type: string; }

const TYPE_COLOR: Record<string, string> = {
  trade:    "#10b981",
  research: "#00d4ff",
  alert:    "#f59e0b",
  system:   "#475569",
};
const TYPE_ICON: Record<string, string> = {
  trade:    "◈",
  research: "◉",
  alert:    "⚠",
  system:   "◌",
};
const AGENT_COLOR: Record<string, string> = {
  "swing-trader": "#10b981",
  "day-trader":   "#f59e0b",
  "system":       "#475569",
};

// Static placeholder events shown when journal is empty
const BOOT_EVENTS: FeedEvent[] = [
  { time: "BOOT", agent: "system",       message: "Mission Control systems initialized. All sensors nominal.", type: "system" },
  { time: "BOOT", agent: "system",       message: "Sector Alpha grid online. Crew manifest loaded: 6 agents.", type: "system" },
  { time: "BOOT", agent: "swing-trader", message: "SA-01 Swing Trader entered standby orbit. Awaiting transmission window.", type: "system" },
  { time: "BOOT", agent: "day-trader",   message: "SA-02 Day Trader session not started. Standby orbit confirmed.", type: "system" },
  { time: "BOOT", agent: "system",       message: "GHA failsafe armed. Discord relay nominal. Alpaca API connected.", type: "system" },
];

export default function ActivityFeed() {
  const [events, setEvents] = useState<FeedEvent[]>(BOOT_EVENTS);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const load = async () => {
      const data = await fetchEvents();
      if (Array.isArray(data) && data.length > 0) {
        setEvents([...data.slice(-40).reverse(), ...BOOT_EVENTS]);
      }
    };
    load();
    const id = setInterval(load, 30_000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="h-[108px] shrink-0 relative overflow-hidden"
      style={{
        background: "rgba(0,4,14,0.98)",
        borderTop: "1px solid rgba(0,212,255,0.08)",
      }}>

      {/* Header label */}
      <div className="absolute left-4 top-2 z-10 flex items-center gap-2">
        <div className="w-1 h-1 rounded-full bg-emerald-500 animate-ping opacity-70"/>
        <span className="text-[8px] tracking-[0.3em] text-emerald-600 opacity-70 flicker">
          COMMS LOG
        </span>
      </div>

      {/* Left/right fade */}
      <div className="absolute left-0 top-0 bottom-0 w-20 z-10 pointer-events-none"
        style={{ background: "linear-gradient(90deg, rgba(0,4,14,1) 0%, transparent 100%)" }}/>
      <div className="absolute right-0 top-0 bottom-0 w-20 z-10 pointer-events-none"
        style={{ background: "linear-gradient(90deg, transparent 0%, rgba(0,4,14,1) 100%)" }}/>

      {/* Scrollable horizontal feed */}
      <div ref={scrollRef}
        className="absolute inset-0 flex items-end pl-24 pr-8 pb-3 pt-9 gap-2.5 overflow-x-auto"
        style={{ scrollbarWidth: "none" }}>
        <AnimatePresence>
          {events.map((ev, i) => {
            const typeColor = TYPE_COLOR[ev.type] ?? "#475569";
            const agentColor = AGENT_COLOR[ev.agent] ?? "#475569";
            return (
              <motion.div key={`${ev.time}-${i}`}
                initial={{ opacity: 0, x: -10, scale: 0.95 }}
                animate={{ opacity: 1, x: 0, scale: 1 }}
                transition={{ delay: Math.min(i * 0.03, 0.4) }}
                className="feed-item shrink-0 rounded-sm px-3 py-1.5 max-w-[280px]"
                style={{
                  background: "rgba(0,8,24,0.8)",
                  border: `1px solid ${typeColor}22`,
                  backdropFilter: "blur(8px)",
                }}>

                {/* Top row */}
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-[9px]" style={{ color: typeColor }}>
                    {TYPE_ICON[ev.type] ?? "◌"}
                  </span>
                  <span className="text-[8px] font-bold tracking-widest" style={{ color: agentColor }}>
                    {ev.agent.toUpperCase().replace(/-/g, " ")}
                  </span>
                  <span className="ml-auto text-[8px] text-slate-700 pl-2 shrink-0 tabular-nums">
                    {ev.time}
                  </span>
                </div>

                {/* Message */}
                <p className="text-[9px] leading-snug line-clamp-2"
                  style={{ color: "#6b7280" }}>
                  {ev.message}
                </p>

                {/* Bottom accent */}
                <div className="mt-1.5 h-px"
                  style={{ background: `linear-gradient(90deg, ${typeColor}30, transparent)` }}/>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </div>
  );
}
