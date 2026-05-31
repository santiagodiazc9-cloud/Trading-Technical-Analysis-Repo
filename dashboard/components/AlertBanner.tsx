"use client";

import { motion, AnimatePresence } from "framer-motion";

interface Alert {
  symbol: string;
  pct: number;
  stopPrice: number;
  currentPrice: number;
}

interface AlertBannerProps {
  alerts: Alert[];
}

export default function AlertBanner({ alerts }: AlertBannerProps) {
  return (
    <AnimatePresence>
      {alerts.map((alert, i) => (
        <motion.div
          key={alert.symbol}
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 32, opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          transition={{ duration: 0.3 }}
          className="shrink-0 overflow-hidden alert-border"
          style={{
            background: "rgba(127, 29, 29, 0.3)",
            borderBottom: "1px solid rgba(239,68,68,0.4)",
            borderTop: i === 0 ? "1px solid rgba(239,68,68,0.4)" : "none",
          }}
        >
          <div className="flex items-center gap-4 px-5 h-8">
            <motion.span
              animate={{ opacity: [1, 0.3, 1] }}
              transition={{ duration: 0.6, repeat: Infinity }}
              className="text-red-400 text-[11px]"
            >
              ⚠
            </motion.span>
            <span className="text-[9px] font-bold tracking-[0.2em] text-red-400">
              CRITICAL ALERT
            </span>
            <span className="w-px h-3 bg-red-900"/>
            <span className="text-[9px] text-red-300 tracking-wide">
              {alert.symbol} AT {alert.pct.toFixed(2)}% — APPROACHING -7% MANUAL CUT
            </span>
            <span className="w-px h-3 bg-red-900"/>
            <span className="text-[9px] text-red-500">
              CURRENT: ${alert.currentPrice.toFixed(2)}
            </span>
            <span className="text-[9px] text-red-700">
              STOP: ${alert.stopPrice.toFixed(2)}
            </span>
            <div className="ml-auto text-[8px] text-red-800 tracking-widest animate-pulse">
              MONITOR POSITION
            </div>
          </div>
        </motion.div>
      ))}
    </AnimatePresence>
  );
}
