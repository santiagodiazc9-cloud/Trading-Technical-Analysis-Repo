"use client";

import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import type { AgentDef, AgentStatus } from "@/lib/agents";
import StarField from "./MatrixRain";

const COLOR_HEX: Record<string, string> = {
  emerald: "#10b981",
  amber:   "#f59e0b",
  purple:  "#8b5cf6",
  blue:    "#3b82f6",
  orange:  "#f97316",
  cyan:    "#06b6d4",
};

// Planet colors for system nodes
const SYSTEM_NODES = [
  { id: "alpaca",  label: "ALPACA",   sub: "BROKER API",    x: 18, y: 28, r: 22, color: "#00d4ff", ring: "#00aaff" },
  { id: "discord", label: "DISCORD",  sub: "COMMS RELAY",   x: 82, y: 28, r: 20, color: "#7c3aed", ring: "#a855f7" },
  { id: "tavily",  label: "TAVILY",   sub: "INTEL FEED",    x: 18, y: 72, r: 20, color: "#0ea5e9", ring: "#38bdf8" },
  { id: "memory",  label: "MEMORY",   sub: "DATA CORE",     x: 82, y: 72, r: 20, color: "#64748b", ring: "#94a3b8" },
  { id: "scanner", label: "SCANNER",  sub: "650 SYMBOLS",   x: 50, y: 50, r: 24, color: "#6366f1", ring: "#818cf8" },
];

const AGENT_NODES = [
  { id: "swing-trader",  x: 50, y: 22, r: 34, agentColor: "emerald", designation: "SA-01" },
  { id: "day-trader",    x: 50, y: 78, r: 28, agentColor: "amber",   designation: "SA-02" },
  { id: "market-oracle", x: 10, y: 50, r: 18, agentColor: "purple",  designation: "SA-03" },
  { id: "compute-broker",x: 90, y: 50, r: 18, agentColor: "cyan",    designation: "SA-04" },
  { id: "alpha-feed",    x: 50, y: 95, r: 18, agentColor: "amber",   designation: "SA-05" },
];

const EDGES = [
  { from: "swing-trader", to: "alpaca",   active: true,  dir: 1 },
  { from: "swing-trader", to: "discord",  active: true,  dir: 1 },
  { from: "swing-trader", to: "scanner",  active: true,  dir: 1 },
  { from: "swing-trader", to: "memory",   active: true,  dir: 1 },
  { from: "day-trader",   to: "alpaca",   active: false, dir: 1 },
  { from: "day-trader",   to: "tavily",   active: true,  dir: 1 },
  { from: "day-trader",   to: "scanner",  active: false, dir: 1 },
  { from: "scanner",      to: "memory",   active: true,  dir: 1 },
];

function pct(val: number, total: number) { return (val / 100) * total; }

function nodeCenter(id: string, w: number, h: number) {
  const sn = SYSTEM_NODES.find(n => n.id === id);
  if (sn) return { x: pct(sn.x, w), y: pct(sn.y, h) };
  const an = AGENT_NODES.find(n => n.id === id);
  if (an) return { x: pct(an.x, w), y: pct(an.y, h) };
  return { x: w / 2, y: h / 2 };
}

function curvePath(fromId: string, toId: string, w: number, h: number) {
  const f = nodeCenter(fromId, w, h);
  const t = nodeCenter(toId, w, h);
  const cx = (f.x + t.x) / 2 + (Math.random() > 0.5 ? 1 : -1) * 20;
  const cy = (f.y + t.y) / 2 - 15;
  return `M ${f.x} ${f.y} Q ${cx} ${cy} ${t.x} ${t.y}`;
}

export interface WarpEvent { agentId: string; routinePath: string; }

interface CanvasProps {
  agents: AgentDef[];
  liveMap: Record<string, { status: AgentStatus; metric?: { label: string; value: string }; currentTask?: string }>;
  onSelectAgent?: (id: string) => void;
  warpEvent?: WarpEvent | null;
  alertSymbols?: string[];
}

export default function NetworkCanvas({ agents, liveMap, onSelectAgent, warpEvent, alertSymbols = [] }: CanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [size, setSize] = useState({ w: 900, h: 600 });
  const [shaking, setShaking] = useState(false);
  const [warpBeam, setWarpBeam] = useState<{ from: string; to: string; color: string } | null>(null);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const ro = new ResizeObserver(e => {
      const r = e[0].contentRect;
      setSize({ w: r.width, h: r.height });
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  // Hyperspace warp beam + screen shake
  useEffect(() => {
    if (!warpEvent) return;
    const agent = agents.find(a => a.id === warpEvent.agentId);
    if (!agent) return;
    const hex = COLOR_HEX[agent.color] ?? "#00d4ff";
    const target = warpEvent.routinePath.includes("market") ? "scanner" : "discord";
    setWarpBeam({ from: warpEvent.agentId, to: target, color: hex });
    setShaking(true);
    const t1 = setTimeout(() => setWarpBeam(null), 900);
    const t2 = setTimeout(() => setShaking(false), 500);
    return () => { clearTimeout(t1); clearTimeout(t2); };
  }, [warpEvent, agents]);

  const { w, h } = size;

  // Pre-compute stable edge paths (no random in render)
  const edgePaths = EDGES.map((edge, i) => {
    const f = nodeCenter(edge.from, w, h);
    const t = nodeCenter(edge.to, w, h);
    const offset = ((i % 3) - 1) * 18;
    const cx = (f.x + t.x) / 2 + offset;
    const cy = (f.y + t.y) / 2 - 18;
    return `M ${f.x} ${f.y} Q ${cx} ${cy} ${t.x} ${t.y}`;
  });

  return (
    <div
      ref={containerRef}
      className={`relative flex-1 overflow-hidden nebula-bg space-grid scan-sweep${shaking ? " shake" : ""}`}
    >
      {/* Star field */}
      <StarField />

      {/* Nebula blobs */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute rounded-full"
          style={{ width: 300, height: 200, left: "10%", top: "20%",
            background: "radial-gradient(ellipse, rgba(88,28,135,0.18) 0%, transparent 70%)",
            filter: "blur(40px)", animation: "float 12s ease-in-out infinite" }} />
        <div className="absolute rounded-full"
          style={{ width: 250, height: 250, right: "10%", bottom: "20%",
            background: "radial-gradient(ellipse, rgba(30,58,138,0.2) 0%, transparent 70%)",
            filter: "blur(50px)", animation: "float 15s ease-in-out 3s infinite reverse" }} />
      </div>

      {/* SVG network */}
      <svg className="absolute inset-0 w-full h-full" viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none">
        <defs>
          {/* Agent glows */}
          {["emerald","amber","purple","blue","orange","cyan"].map(c => (
            <filter key={c} id={`glow-${c}`} x="-100%" y="-100%" width="300%" height="300%">
              <feGaussianBlur stdDeviation="8" result="blur"/>
              <feMerge><feMergeNode in="blur"/><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
          ))}
          <filter id="glow-sys" x="-80%" y="-80%" width="260%" height="260%">
            <feGaussianBlur stdDeviation="5" result="blur"/>
            <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
          <filter id="glow-strong" x="-150%" y="-150%" width="400%" height="400%">
            <feGaussianBlur stdDeviation="14" result="blur"/>
            <feMerge><feMergeNode in="blur"/><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>

          {/* Star burst */}
          <radialGradient id="starGrad" cx="50%" cy="50%" r="50%">
            <stop offset="0%"  stopColor="#ffffff" stopOpacity="1"/>
            <stop offset="40%" stopColor="#ffd700" stopOpacity="0.6"/>
            <stop offset="100%" stopColor="transparent" stopOpacity="0"/>
          </radialGradient>

          {/* Black hole gravitational lensing filter */}
          <filter id="blackhole-warp" x="-60%" y="-60%" width="220%" height="220%">
            <feTurbulence type="turbulence" baseFrequency="0.015" numOctaves="3"
              seed="2" result="turb">
              <animate attributeName="seed" values="1;8;1" dur="12s" repeatCount="indefinite"/>
            </feTurbulence>
            <feDisplacementMap in="SourceGraphic" in2="turb" scale="6"
              xChannelSelector="R" yChannelSelector="G"/>
          </filter>

          {/* Radar sweep radial gradient */}
          <radialGradient id="radarFill" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#00d4ff" stopOpacity="0.15"/>
            <stop offset="100%" stopColor="#00d4ff" stopOpacity="0"/>
          </radialGradient>

          {/* Warp beam gradient */}
          <linearGradient id="warpGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%"  stopColor="white" stopOpacity="0"/>
            <stop offset="50%" stopColor="white" stopOpacity="1"/>
            <stop offset="100%" stopColor="white" stopOpacity="0"/>
          </linearGradient>
        </defs>

        {/* ── EDGES ─────────────────────────────────────────── */}
        {EDGES.map((edge, i) => {
          const d = edgePaths[i];
          const fromAgent = agents.find(a => a.id === edge.from);
          const stroke = fromAgent ? (COLOR_HEX[fromAgent.color] ?? "#00d4ff") : "#6366f1";
          const pathId = `ep-${i}`;
          return (
            <g key={i}>
              {/* Named path for particle motion */}
              <path id={pathId} d={d} fill="none" stroke="none"/>

              {/* Dim static lane */}
              <path d={d} fill="none"
                stroke={edge.active ? stroke : "#1e293b"}
                strokeWidth={edge.active ? 1.5 : 0.8}
                strokeDasharray="6 8"
                opacity={edge.active ? 0.25 : 0.1}/>

              {/* Animated dash flow */}
              {edge.active && (
                <path d={d} fill="none" stroke={stroke} strokeWidth={1.5} opacity={0.6}>
                  <animate attributeName="stroke-dashoffset"
                    from="0" to="-50" dur={`${1.8 + i * 0.25}s`} repeatCount="indefinite"/>
                  <animate attributeName="stroke-dasharray"
                    values="0 50;10 40;0 50" dur={`${1.8 + i * 0.25}s`} repeatCount="indefinite"/>
                </path>
              )}

              {/* Traveling particles */}
              {edge.active && [0, 0.4, 0.75].map((offset, pi) => (
                <circle key={pi} r={pi === 0 ? 3.5 : 2} fill={stroke} opacity={0.9}
                  filter="url(#glow-sys)">
                  <animateMotion dur={`${2.5 + i * 0.3}s`} repeatCount="indefinite"
                    begin={`${offset * (2.5 + i * 0.3)}s`}>
                    <mpath href={`#${pathId}`}/>
                  </animateMotion>
                </circle>
              ))}
            </g>
          );
        })}

        {/* ── RADAR SWEEP ──────────────────────────────────── */}
        {(() => {
          const cx = w / 2;
          const cy = h / 2;
          const radius = Math.max(w, h) * 0.7;
          return (
            <g>
              {/* Sector fill */}
              <path fill="url(#radarFill)" opacity={0.6}>
                <animateTransform attributeName="transform"
                  type="rotate" from={`0 ${cx} ${cy}`} to={`360 ${cx} ${cy}`}
                  dur="10s" repeatCount="indefinite"/>
                <animate attributeName="d"
                  values={`M${cx},${cy} L${cx},${cy-radius} A${radius},${radius} 0 0,1 ${cx+radius*Math.sin(Math.PI/9)},${cy-radius*Math.cos(Math.PI/9)} Z`}
                  dur="0.1s" repeatCount="indefinite"/>
              </path>
              {/* Main beam */}
              <line x1={cx} y1={cy} x2={cx} y2={cy - radius}
                stroke="#00d4ff" strokeWidth={1.5} opacity={0.7}
                style={{ filter: "drop-shadow(0 0 4px #00d4ff)" }}>
                <animateTransform attributeName="transform"
                  type="rotate" from={`0 ${cx} ${cy}`} to={`360 ${cx} ${cy}`}
                  dur="10s" repeatCount="indefinite"/>
              </line>
              {/* Trail lines */}
              {[12, 22, 32].map((deg, ti) => (
                <line key={ti} x1={cx} y1={cy} x2={cx} y2={cy - radius}
                  stroke="#00d4ff" strokeWidth={0.8}
                  opacity={0.22 - ti * 0.06}>
                  <animateTransform attributeName="transform"
                    type="rotate"
                    from={`${-deg} ${cx} ${cy}`} to={`${360 - deg} ${cx} ${cy}`}
                    dur="10s" repeatCount="indefinite"/>
                </line>
              ))}
            </g>
          );
        })()}

        {/* ── WARP BEAM ─────────────────────────────────────── */}
        {warpBeam && (() => {
          const f = nodeCenter(warpBeam.from, w, h);
          const t = nodeCenter(warpBeam.to, w, h);
          return (
            <g style={{ animation: "warpFlash 0.9s ease-out forwards" }}>
              <line x1={f.x} y1={f.y} x2={t.x} y2={t.y}
                stroke={warpBeam.color} strokeLinecap="round" opacity={0.9}
                style={{ filter: `drop-shadow(0 0 12px ${warpBeam.color})` }}>
                <animate attributeName="strokeWidth" values="0;10;4;0" dur="0.9s" fill="freeze"/>
                <animate attributeName="opacity" values="0;1;0.8;0" dur="0.9s" fill="freeze"/>
              </line>
              {/* Secondary glow */}
              <line x1={f.x} y1={f.y} x2={t.x} y2={t.y}
                stroke="white" strokeLinecap="round" opacity={0.5}>
                <animate attributeName="strokeWidth" values="0;4;2;0" dur="0.9s" fill="freeze"/>
                <animate attributeName="opacity" values="0;0.8;0.4;0" dur="0.9s" fill="freeze"/>
              </line>
            </g>
          );
        })()}

        {/* ── SYSTEM NODES (planets) ────────────────────────── */}
        {SYSTEM_NODES.map(n => {
          const px = pct(n.x, w);
          const py = pct(n.y, h);

          // ── BLACK HOLE (scanner node) ──
          if (n.id === "scanner") {
            const INFALL_PATHS = [
              `M ${px+50} ${py} A 50 18 0 1 1 ${px+50-0.1} ${py}`,
              `M ${px} ${py-40} A 40 14 0 1 1 ${px-0.1} ${py-40}`,
              `M ${px-38} ${py+12} A 38 12 0 1 1 ${px-38-0.1} ${py+12}`,
            ];
            return (
              <g key={n.id}>
                {/* Gravitational lensing warp zone */}
                <circle cx={px} cy={py} r={n.r + 30}
                  fill="none" stroke="transparent" filter="url(#blackhole-warp)" opacity={0.8}/>

                {/* Accretion disk rings — 3 tilted ellipses */}
                {[
                  { rx: n.r+22, ry: 7,  dur: "4s",  color: "#6366f1", dash: "none" },
                  { rx: n.r+34, ry: 11, dur: "7s",  color: "#818cf8", dash: "4 3"  },
                  { rx: n.r+44, ry: 15, dur: "11s", color: "#a5b4fc", dash: "3 5"  },
                ].map((ring, ri) => (
                  <ellipse key={ri} cx={px} cy={py} rx={ring.rx} ry={ring.ry}
                    fill="none" stroke={ring.color} strokeWidth={ri === 0 ? 2 : 1}
                    strokeDasharray={ring.dash} opacity={0.6 - ri * 0.12}
                    style={{ transformOrigin: `${px}px ${py}px`,
                      animation: `orbit ${ring.dur} linear infinite` }}/>
                ))}

                {/* Particle infall paths (named) */}
                {INFALL_PATHS.map((d, pi) => (
                  <path key={pi} id={`infall-${pi}`} d={d} fill="none" stroke="none"/>
                ))}

                {/* Infalling particles */}
                {INFALL_PATHS.map((_, pi) =>
                  [0, 0.33, 0.66].map((off, oi) => (
                    <circle key={`${pi}-${oi}`} r={1.5} fill="#818cf8" opacity={0.7}>
                      <animateMotion dur={`${3 + pi * 1.5}s`} repeatCount="indefinite"
                        begin={`${off * (3 + pi * 1.5)}s`}>
                        <mpath href={`#infall-${pi}`}/>
                      </animateMotion>
                      <animate attributeName="opacity" values="0;0.8;0" dur={`${3 + pi * 1.5}s`}
                        begin={`${off * (3 + pi * 1.5)}s`} repeatCount="indefinite"/>
                    </circle>
                  ))
                )}

                {/* Event horizon — absolute black */}
                <circle cx={px} cy={py} r={n.r}
                  fill="#000000" stroke="#1e1b4b" strokeWidth={1.5}
                  style={{ filter: "drop-shadow(0 0 10px rgba(99,102,241,0.4))" }}/>

                {/* Singularity point */}
                <circle cx={px} cy={py} r={4} fill="white"
                  style={{ filter: "drop-shadow(0 0 8px white) drop-shadow(0 0 16px #c7d2fe)" }}>
                  <animate attributeName="r" values="3;5;3" dur="2s" repeatCount="indefinite"/>
                  <animate attributeName="opacity" values="0.7;1;0.7" dur="2s" repeatCount="indefinite"/>
                </circle>

                {/* Labels */}
                <text x={px} y={py + n.r + 14} textAnchor="middle"
                  fontSize="7" fill="#818cf8" opacity={0.7} fontFamily="monospace" fontWeight="bold" letterSpacing="1.5">
                  MARKET SCANNER
                </text>
                <text x={px} y={py + n.r + 24} textAnchor="middle"
                  fontSize="6" fill="#6366f1" opacity={0.5} fontFamily="monospace">
                  650 SYMBOLS
                </text>
              </g>
            );
          }

          return (
            <g key={n.id} filter="url(#glow-sys)">
              {/* Planetary ring */}
              <ellipse cx={px} cy={py} rx={n.r + 10} ry={5}
                fill="none" stroke={n.ring} strokeWidth={1.5} opacity={0.35}
                style={{ transformOrigin: `${px}px ${py}px`,
                  animation: `orbit ${8 + n.r * 0.3}s linear infinite` }}/>

              {/* Planet body */}
              <circle cx={px} cy={py} r={n.r}
                fill={`rgba(6,18,40,0.9)`}
                stroke={n.color} strokeWidth={1.2} opacity={0.8}/>

              {/* Surface detail arc */}
              <path d={`M ${px - n.r * 0.6} ${py - n.r * 0.5} Q ${px} ${py - n.r * 0.8} ${px + n.r * 0.6} ${py - n.r * 0.5}`}
                fill="none" stroke={n.color} strokeWidth={0.5} opacity={0.4}/>

              {/* Labels */}
              <text x={px} y={py - 1} textAnchor="middle" dominantBaseline="middle"
                fontSize="7" fill={n.color} fontFamily="monospace" fontWeight="bold" letterSpacing="1">
                {n.label}
              </text>
              <text x={px} y={py + 8} textAnchor="middle" dominantBaseline="middle"
                fontSize="5.5" fill={n.color} fontFamily="monospace" opacity={0.5}>
                {n.sub}
              </text>
              <text x={px} y={py + n.r + 11} textAnchor="middle"
                fontSize="6.5" fill={n.color} opacity={0.6} fontFamily="monospace" letterSpacing="1">
                {n.id.toUpperCase()}
              </text>
            </g>
          );
        })}

        {/* ── AGENT NODES (star systems) ────────────────────── */}
        {AGENT_NODES.map(an => {
          const agent = agents.find(a => a.id === an.id);
          if (!agent) return null;
          const live = liveMap[an.id];
          const status: AgentStatus = live?.status ?? agent.defaultStatus;
          const hex = COLOR_HEX[an.agentColor] ?? "#64748b";
          const isActive = status === "active";
          const isStub = !!agent.stub;
          const px = pct(an.x, w);
          const py = pct(an.y, h);
          const r = an.r;

          // ── STUB NODES — small dormant spheres ──────────────
          if (isStub) {
            return (
              <g key={an.id} style={{ cursor: "pointer" }} opacity={0.35}
                onClick={() => onSelectAgent ? onSelectAgent(an.id) : (window.location.href = `/agents/${an.id}`)}>
                {/* Dormant glow */}
                <circle cx={px} cy={py} r={r + 8} fill="none"
                  stroke={hex} strokeWidth={0.5} opacity={0.3} strokeDasharray="3 5">
                  <animate attributeName="opacity" values="0.2;0.5;0.2" dur="4s" repeatCount="indefinite"/>
                </circle>
                {/* Body */}
                <circle cx={px} cy={py} r={r} fill="rgba(2,8,20,0.9)"
                  stroke={hex} strokeWidth={1} strokeDasharray="4 4"/>
                {/* IN DEV label inside */}
                <text x={px} y={py - 3} textAnchor="middle" dominantBaseline="middle"
                  fontSize="5" fill={hex} fontFamily="monospace" letterSpacing="0.5">
                  {an.designation}
                </text>
                <text x={px} y={py + 5} textAnchor="middle" dominantBaseline="middle"
                  fontSize="4.5" fill={hex} fontFamily="monospace" opacity={0.6}>
                  STAGED
                </text>
                {/* Agent name below */}
                <text x={px} y={py + r + 12} textAnchor="middle"
                  fontSize="7" fill={hex} opacity={0.6} fontFamily="monospace" letterSpacing="1.5">
                  {agent.name.toUpperCase()}
                </text>
              </g>
            );
          }

          return (
            <g key={an.id} style={{ cursor: "pointer" }}
              onClick={() => onSelectAgent ? onSelectAgent(an.id) : (window.location.href = `/agents/${an.id}`)}>


              {/* Triple pulse rings for active */}
              {isActive && [r + 14, r + 24, r + 36].map((pr, ri) => (
                <circle key={ri} cx={px} cy={py} r={pr} fill="none"
                  stroke={hex} strokeWidth={0.8}
                  style={{ transformOrigin: `${px}px ${py}px` }}>
                  <animate attributeName="r" values={`${pr};${pr + 18};${pr}`}
                    dur={`${2.8 + ri * 0.6}s`} repeatCount="indefinite"/>
                  <animate attributeName="opacity" values="0.4;0;0.4"
                    dur={`${2.8 + ri * 0.6}s`} repeatCount="indefinite"/>
                </circle>
              ))}

              {/* Outer corona glow */}
              <circle cx={px} cy={py} r={r + 6} fill="none"
                stroke={hex} strokeWidth={2} opacity={isActive ? 0.3 : 0.1}
                filter={isActive ? `url(#glow-${an.agentColor})` : undefined}/>

              {/* Orbital ring 1 — tilted */}
              <ellipse cx={px} cy={py} rx={r + 18} ry={7}
                fill="none" stroke={hex} strokeWidth={1.5}
                opacity={isActive ? 0.5 : 0.15}
                style={{ transformOrigin: `${px}px ${py}px`,
                  animation: `orbit ${6}s linear infinite` }}/>

              {/* Orbital ring 2 — counter, thinner */}
              <ellipse cx={px} cy={py} rx={r + 28} ry={10}
                fill="none" stroke={hex} strokeWidth={0.8} strokeDasharray="4 6"
                opacity={isActive ? 0.3 : 0.08}
                style={{ transformOrigin: `${px}px ${py}px`,
                  animation: `orbitR 10s linear infinite` }}/>

              {/* Satellite dot on ring 1 */}
              {isActive && (
                <circle r={3} fill={hex} opacity={0.9} filter={`url(#glow-${an.agentColor})`}>
                  <animateMotion dur="6s" repeatCount="indefinite">
                    <mpath href={`#orbit-path-${an.id}`}/>
                  </animateMotion>
                </circle>
              )}
              <path id={`orbit-path-${an.id}`} fill="none" stroke="none"
                d={`M ${px + r + 18} ${py} a ${r+18} 7 0 1 1 -0.1 0 z`}/>

              {/* Main body */}
              <circle cx={px} cy={py} r={r} fill={`rgba(2,8,20,0.9)`}
                stroke={hex} strokeWidth={isActive ? 2.5 : 1.2}
                opacity={isActive ? 1 : 0.5}
                filter={isActive ? `url(#glow-strong)` : undefined}/>

              {/* Inner atmosphere */}
              <circle cx={px} cy={py} r={r - 6} fill="none"
                stroke={hex} strokeWidth={0.5} opacity={isActive ? 0.3 : 0.1}
                strokeDasharray={isActive ? "none" : "3 5"}/>

              {/* Pixel art avatar */}
              <foreignObject x={px - 16} y={py - 18} width={32} height={32}
                style={{ overflow: "visible" }}>
                <div
                  dangerouslySetInnerHTML={{ __html: agent.pixelArt }}
                  style={{ width: 32, height: 32, opacity: isActive ? 1 : 0.35,
                    filter: isActive ? `drop-shadow(0 0 6px ${hex})` : undefined }}
                />
              </foreignObject>

              {/* Designation badge */}
              <rect x={px - 18} y={py + r + 4} width={36} height={10} rx={2}
                fill={`${hex}18`} stroke={`${hex}40`} strokeWidth={0.5}/>
              <text x={px} y={py + r + 11} textAnchor="middle"
                fontSize="6.5" fill={hex} opacity={0.8} fontFamily="monospace" fontWeight="bold" letterSpacing="1.5">
                {an.designation}
              </text>

              {/* Agent name */}
              <text x={px} y={py + r + 24} textAnchor="middle"
                fontSize="9" fill={hex} opacity={0.95} fontFamily="monospace" fontWeight="bold" letterSpacing="2">
                {agent.name.toUpperCase()}
              </text>

              {/* Status */}
              <text x={px} y={py + r + 34} textAnchor="middle"
                fontSize="6.5" fill={hex} opacity={0.5} fontFamily="monospace" letterSpacing="1">
                {status === "active" ? "ORBIT NOMINAL" : status === "idle" ? "STANDBY" : "OFFLINE"}
              </text>
            </g>
          );
        })}
      </svg>

      {/* ── Floating task cards ─────────────────────────────── */}
      <AnimatePresence>
        {AGENT_NODES.map(an => {
          const agent = agents.find(a => a.id === an.id);
          if (!agent) return null;
          const live = liveMap[an.id];
          const task = live?.currentTask ?? agent.currentTask;
          if (!task || task === "OFFLINE") return null;
          const hex = COLOR_HEX[an.agentColor] ?? "#00d4ff";
          const isRight = an.x > 50;
          return (
            <motion.div key={an.id}
              className="absolute pointer-events-none"
              style={{
                left: `${an.x + (isRight ? -22 : 10)}%`,
                top: `${an.y - 18}%`,
                transform: "translate(-50%, -50%)",
              }}
              initial={{ opacity: 0, scale: 0.7 }}
              animate={{ opacity: 1, scale: 1, y: [0, -6, 0] }}
              transition={{ y: { repeat: Infinity, duration: 4, ease: "easeInOut" } }}
            >
              <div className="px-2.5 py-1.5 rounded-sm text-[9px] tracking-widest whitespace-nowrap"
                style={{
                  background: `rgba(2,8,20,0.92)`,
                  border: `1px solid ${hex}50`,
                  color: hex,
                  boxShadow: `0 0 12px ${hex}20, inset 0 0 8px ${hex}08`,
                  fontFamily: "monospace",
                }}>
                ▸ {task}
              </div>
            </motion.div>
          );
        })}
      </AnimatePresence>

      {/* ── HUD corners ───────────────────────────────────────── */}
      {[
        "top-3 left-3 hud-corner-tl",
        "top-3 right-3 hud-corner-tr",
        "bottom-3 left-3 hud-corner-bl",
        "bottom-3 right-3 hud-corner-br",
      ].map(cls => (
        <div key={cls} className={`absolute w-5 h-5 opacity-40 ${cls}`} />
      ))}

      {/* ── Sector label ─────────────────────────────────────── */}
      <div className="absolute bottom-5 left-1/2 -translate-x-1/2 text-[9px] tracking-[0.3em] text-slate-700">
        SECTOR ALPHA · GRID 7B
      </div>
    </div>
  );
}
