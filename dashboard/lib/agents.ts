export type AgentStatus = "active" | "idle" | "paused" | "offline" | "stub";

export type AgentDef = {
  id: string;
  name: string;
  icon: string;
  color: string; // "emerald" | "amber" | "purple" | "blue" | "orange" | "cyan"
  description: string;
  defaultStatus: AgentStatus;
  pixelArt: string; // inline SVG
  metric: { label: string; value: string };
  currentTask?: string;
  routines?: string[];
  detailRoute?: string;
  stub?: { tagline: string; potential: string };
};

// 32×32 SVG pixel-art characters using 4px rects (8×8 effective pixel grid).
// Palette: #f5cba7 skin, agent-color shirt, dark detail.

const SWING_TRADER_SVG = `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" shape-rendering="crispEdges">
  <!-- head -->
  <rect x="12" y="0" width="8" height="4" fill="#f5cba7"/>
  <rect x="8"  y="4" width="16" height="4" fill="#f5cba7"/>
  <!-- eyes -->
  <rect x="10" y="4" width="4" height="4" fill="#1a1a2e"/>
  <rect x="18" y="4" width="4" height="4" fill="#1a1a2e"/>
  <!-- body / shirt (emerald) -->
  <rect x="8"  y="8"  width="16" height="12" fill="#10b981"/>
  <!-- arm left down -->
  <rect x="4"  y="8"  width="4"  height="8"  fill="#10b981"/>
  <!-- arm right raised pointing up-right -->
  <rect x="24" y="4"  width="4"  height="4"  fill="#10b981"/>
  <rect x="28" y="0"  width="4"  height="4"  fill="#10b981"/>
  <!-- pants -->
  <rect x="8"  y="20" width="6"  height="8"  fill="#1e293b"/>
  <rect x="18" y="20" width="6"  height="8"  fill="#1e293b"/>
  <!-- shoes -->
  <rect x="6"  y="28" width="8"  height="4"  fill="#0f172a"/>
  <rect x="18" y="28" width="8"  height="4"  fill="#0f172a"/>
  <!-- chart line in background (top-right) -->
  <rect x="20" y="12" width="4" height="4" fill="#34d399" opacity="0.6"/>
  <rect x="24" y="8"  width="4" height="4" fill="#34d399" opacity="0.6"/>
  <rect x="28" y="4"  width="4" height="4" fill="#34d399" opacity="0.6"/>
</svg>`;

const DAY_TRADER_SVG = `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" shape-rendering="crispEdges">
  <!-- head -->
  <rect x="12" y="0" width="8" height="4" fill="#f5cba7"/>
  <rect x="8"  y="4" width="16" height="4" fill="#f5cba7"/>
  <!-- eyes focused -->
  <rect x="10" y="4" width="4" height="4" fill="#1a1a2e"/>
  <rect x="18" y="4" width="4" height="4" fill="#1a1a2e"/>
  <!-- body leaning forward (amber) -->
  <rect x="6"  y="8"  width="16" height="8"  fill="#f59e0b"/>
  <rect x="8"  y="16" width="12" height="4"  fill="#f59e0b"/>
  <!-- arms on desk -->
  <rect x="2"  y="16" width="6"  height="4"  fill="#f5cba7"/>
  <rect x="24" y="16" width="6"  height="4"  fill="#f5cba7"/>
  <!-- desk -->
  <rect x="0"  y="20" width="32" height="4"  fill="#334155"/>
  <!-- two monitors -->
  <rect x="2"  y="8"  width="6"  height="8"  fill="#0f172a"/>
  <rect x="3"  y="9"  width="4"  height="6"  fill="#fbbf24"/>
  <rect x="24" y="8"  width="6"  height="8"  fill="#0f172a"/>
  <rect x="25" y="9"  width="4"  height="6"  fill="#fbbf24"/>
  <!-- legs -->
  <rect x="8"  y="24" width="6"  height="8"  fill="#1e293b"/>
  <rect x="18" y="24" width="6"  height="8"  fill="#1e293b"/>
</svg>`;

const CRYPTO_SVG = `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" shape-rendering="crispEdges">
  <!-- head -->
  <rect x="12" y="0" width="8" height="4" fill="#f5cba7"/>
  <rect x="8"  y="4" width="16" height="4" fill="#f5cba7"/>
  <!-- eyes -->
  <rect x="10" y="4" width="4" height="4" fill="#1a1a2e"/>
  <rect x="18" y="4" width="4" height="4" fill="#1a1a2e"/>
  <!-- body (purple) -->
  <rect x="8"  y="8"  width="16" height="12" fill="#8b5cf6"/>
  <!-- coin held in right hand -->
  <rect x="24" y="8"  width="4"  height="8"  fill="#f5cba7"/>
  <rect x="24" y="4"  width="8"  height="8"  fill="#fbbf24"/>
  <rect x="26" y="6"  width="4"  height="4"  fill="#8b5cf6"/>
  <!-- B symbol on coin -->
  <rect x="27" y="6"  width="2"  height="4"  fill="#fbbf24"/>
  <!-- left arm down -->
  <rect x="4"  y="8"  width="4"  height="8"  fill="#8b5cf6"/>
  <!-- pants -->
  <rect x="8"  y="20" width="6"  height="8"  fill="#1e293b"/>
  <rect x="18" y="20" width="6"  height="8"  fill="#1e293b"/>
  <!-- shoes -->
  <rect x="6"  y="28" width="8"  height="4"  fill="#0f172a"/>
  <rect x="18" y="28" width="8"  height="4"  fill="#0f172a"/>
</svg>`;

const CONTENT_SVG = `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" shape-rendering="crispEdges">
  <!-- head -->
  <rect x="12" y="0" width="8" height="4" fill="#f5cba7"/>
  <rect x="8"  y="4" width="16" height="4" fill="#f5cba7"/>
  <!-- eyes -->
  <rect x="10" y="4" width="4" height="4" fill="#1a1a2e"/>
  <rect x="18" y="4" width="4" height="4" fill="#1a1a2e"/>
  <!-- body seated (blue) -->
  <rect x="8"  y="8"  width="16" height="8"  fill="#3b82f6"/>
  <rect x="8"  y="16" width="16" height="4"  fill="#3b82f6"/>
  <!-- desk -->
  <rect x="0"  y="20" width="28" height="4"  fill="#334155"/>
  <!-- keyboard on desk -->
  <rect x="4"  y="16" width="20" height="4"  fill="#1e293b"/>
  <rect x="6"  y="17" width="16" height="2"  fill="#475569"/>
  <!-- paper flying -->
  <rect x="24" y="4"  width="8"  height="8"  fill="#f8fafc"/>
  <rect x="25" y="5"  width="6"  height="1"  fill="#94a3b8"/>
  <rect x="25" y="7"  width="6"  height="1"  fill="#94a3b8"/>
  <rect x="25" y="9"  width="4"  height="1"  fill="#94a3b8"/>
  <!-- legs -->
  <rect x="8"  y="24" width="6"  height="8"  fill="#1e293b"/>
  <rect x="18" y="24" width="6"  height="8"  fill="#1e293b"/>
</svg>`;

const FREELANCE_SVG = `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" shape-rendering="crispEdges">
  <!-- head -->
  <rect x="12" y="0" width="8" height="4" fill="#f5cba7"/>
  <rect x="8"  y="4" width="16" height="4" fill="#f5cba7"/>
  <!-- eyes -->
  <rect x="10" y="4" width="4" height="4" fill="#1a1a2e"/>
  <rect x="18" y="4" width="4" height="4" fill="#1a1a2e"/>
  <!-- body (orange) with tie -->
  <rect x="8"  y="8"  width="16" height="12" fill="#f97316"/>
  <rect x="14" y="8"  width="4"  height="10" fill="#ea580c"/>
  <!-- briefcase in right hand -->
  <rect x="24" y="12" width="8"  height="8"  fill="#92400e"/>
  <rect x="26" y="10" width="4"  height="4"  fill="#92400e"/>
  <rect x="27" y="11" width="2"  height="2"  fill="#d97706"/>
  <!-- left arm swinging -->
  <rect x="4"  y="12" width="4"  height="8"  fill="#f97316"/>
  <!-- pants -->
  <rect x="8"  y="20" width="6"  height="8"  fill="#1e293b"/>
  <rect x="18" y="20" width="6"  height="8"  fill="#1e293b"/>
  <!-- shoes mid-step -->
  <rect x="6"  y="28" width="8"  height="4"  fill="#0f172a"/>
  <rect x="20" y="28" width="6"  height="4"  fill="#0f172a"/>
</svg>`;

const ARBITRAGE_SVG = `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" shape-rendering="crispEdges">
  <!-- head -->
  <rect x="12" y="0" width="8" height="4" fill="#f5cba7"/>
  <rect x="8"  y="4" width="16" height="4" fill="#f5cba7"/>
  <!-- magnifying glass over eye -->
  <rect x="16" y="0" width="12" height="12" fill="none"/>
  <rect x="18" y="0" width="8"  height="8"  fill="#06b6d4" opacity="0.4"/>
  <rect x="19" y="1" width="6"  height="6"  fill="#cffafe" opacity="0.3"/>
  <rect x="24" y="8" width="4"  height="4"  fill="#0891b2"/>
  <!-- eyes -->
  <rect x="10" y="4" width="4" height="4" fill="#1a1a2e"/>
  <rect x="18" y="4" width="4" height="4" fill="#1a1a2e"/>
  <!-- body (cyan) -->
  <rect x="8"  y="8"  width="16" height="12" fill="#06b6d4"/>
  <!-- right arm raised holding glass -->
  <rect x="24" y="4"  width="4"  height="8"  fill="#f5cba7"/>
  <!-- left arm -->
  <rect x="4"  y="8"  width="4"  height="8"  fill="#06b6d4"/>
  <!-- pants -->
  <rect x="8"  y="20" width="6"  height="8"  fill="#1e293b"/>
  <rect x="18" y="20" width="6"  height="8"  fill="#1e293b"/>
  <!-- shoes -->
  <rect x="6"  y="28" width="8"  height="4"  fill="#0f172a"/>
  <rect x="18" y="28" width="8"  height="4"  fill="#0f172a"/>
</svg>`;

export const AGENTS: AgentDef[] = [
  {
    id: "swing-trader",
    name: "Swing Trader",
    icon: "📈",
    color: "emerald",
    description: "Multi-day equity setups",
    defaultStatus: "active",
    pixelArt: SWING_TRADER_SVG,
    metric: { label: "P&L", value: "$0.00" },
    currentTask: "AWAITING MARKET OPEN",
    routines: [
      "routines/1_pre_market_research.md",
      "routines/2_market_open_execution.md",
      "routines/3_midday_scan.md",
      "routines/4_end_of_day_review.md",
    ],
    detailRoute: "/swing",
  },
  {
    id: "day-trader",
    name: "Day Trader",
    icon: "⚡",
    color: "amber",
    description: "Intraday ML-scored scalps",
    defaultStatus: "idle",
    pixelArt: DAY_TRADER_SVG,
    metric: { label: "Trades", value: "0 / 0" },
    currentTask: "SESSION NOT STARTED",
    routines: ["routines/2_market_open_execution.md"],
    detailRoute: "/daytrader",
  },
  // ── FRONTIER UNITS (in development this week) ──────────────

  {
    id: "market-oracle",
    name: "Market Oracle",
    icon: "🔮",
    color: "purple",
    description: "Prediction market latency arb",
    defaultStatus: "stub",
    pixelArt: `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" shape-rendering="crispEdges">
  <!-- robe body -->
  <rect x="8"  y="12" width="16" height="14" fill="#8b5cf6"/>
  <rect x="6"  y="14" width="4"  height="10" fill="#8b5cf6"/>
  <rect x="22" y="14" width="4"  height="10" fill="#8b5cf6"/>
  <!-- head -->
  <rect x="11" y="4"  width="10" height="8"  fill="#f5cba7"/>
  <!-- eyes -->
  <rect x="13" y="6"  width="2"  height="2"  fill="#1a1a2e"/>
  <rect x="17" y="6"  width="2"  height="2"  fill="#1a1a2e"/>
  <!-- hat -->
  <rect x="9"  y="0"  width="14" height="4"  fill="#6d28d9"/>
  <rect x="6"  y="4"  width="20" height="2"  fill="#6d28d9"/>
  <!-- crystal ball -->
  <rect x="12" y="22" width="8"  height="8"  fill="#c4b5fd"/>
  <rect x="13" y="23" width="6"  height="6"  fill="#a78bfa"/>
  <rect x="14" y="24" width="2"  height="2"  fill="#ede9fe"/>
  <!-- glow -->
  <rect x="10" y="20" width="12" height="2"  fill="#7c3aed" opacity="0.5"/>
  <rect x="11" y="30" width="10" height="2"  fill="#4c1d95"/>
</svg>`,
    metric: { label: "Edge", value: "—" },
    currentTask: "IN DEVELOPMENT",
    stub: {
      tagline: "This week's build",
      potential: "News breaks → 30-120s window → Kalshi/Polymarket positions before market reprices. 100% legal. < 50 systematic operators worldwide.",
    },
  },

  {
    id: "compute-broker",
    name: "Compute Broker",
    icon: "⚙️",
    color: "cyan",
    description: "GPU spot price arbitrage",
    defaultStatus: "stub",
    pixelArt: `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" shape-rendering="crispEdges">
  <!-- server rack body -->
  <rect x="6"  y="2"  width="20" height="28" fill="#0e7490"/>
  <rect x="7"  y="3"  width="18" height="26" fill="#164e63"/>
  <!-- rack units -->
  <rect x="8"  y="4"  width="16" height="4"  fill="#0e7490"/>
  <rect x="8"  y="9"  width="16" height="4"  fill="#0e7490"/>
  <rect x="8"  y="14" width="16" height="4"  fill="#0e7490"/>
  <rect x="8"  y="19" width="16" height="4"  fill="#0e7490"/>
  <rect x="8"  y="24" width="16" height="4"  fill="#0e7490"/>
  <!-- LEDs green/active -->
  <rect x="9"  y="5"  width="2"  height="2"  fill="#00ff41"/>
  <rect x="9"  y="10" width="2"  height="2"  fill="#00ff41"/>
  <rect x="9"  y="15" width="2"  height="2"  fill="#ffd700"/>
  <rect x="9"  y="20" width="2"  height="2"  fill="#00ff41"/>
  <rect x="9"  y="25" width="2"  height="2"  fill="#ef4444"/>
  <!-- price tag -->
  <rect x="18" y="5"  width="5"  height="3"  fill="#06b6d4"/>
  <rect x="19" y="6"  width="3"  height="1"  fill="#ffffff"/>
</svg>`,
    metric: { label: "Spread", value: "—" },
    currentTask: "IN DEVELOPMENT",
    stub: {
      tagline: "This week's build",
      potential: "H100 spot prices swing 3–8x in 24h across CoreWeave/Lambda/RunPod. Buy cheap, resell as managed inference. $50–300K/mo ceiling.",
    },
  },

  {
    id: "alpha-feed",
    name: "Alpha Feed",
    icon: "📡",
    color: "amber",
    description: "Trading signals as a subscription",
    defaultStatus: "stub",
    pixelArt: `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" shape-rendering="crispEdges">
  <!-- dish base -->
  <rect x="14" y="24" width="4"  height="6"  fill="#78350f"/>
  <rect x="10" y="28" width="12" height="2"  fill="#92400e"/>
  <!-- dish body -->
  <rect x="6"  y="14" width="20" height="12" fill="#f59e0b"/>
  <rect x="8"  y="12" width="16" height="4"  fill="#f59e0b"/>
  <rect x="10" y="10" width="12" height="4"  fill="#f59e0b"/>
  <rect x="12" y="8"  width="8"  height="4"  fill="#f59e0b"/>
  <rect x="14" y="6"  width="4"  height="4"  fill="#f59e0b"/>
  <!-- inner dish -->
  <rect x="10" y="16" width="12" height="8"  fill="#fbbf24"/>
  <rect x="12" y="14" width="8"  height="4"  fill="#fbbf24"/>
  <!-- signal waves -->
  <rect x="2"  y="8"  width="2"  height="2"  fill="#ffd700" opacity="0.8"/>
  <rect x="0"  y="6"  width="2"  height="6"  fill="#ffd700" opacity="0.5"/>
  <rect x="28" y="8"  width="2"  height="2"  fill="#ffd700" opacity="0.8"/>
  <rect x="30" y="6"  width="2"  height="6"  fill="#ffd700" opacity="0.5"/>
  <!-- focal point -->
  <rect x="15" y="2"  width="2"  height="4"  fill="#b45309"/>
  <rect x="14" y="0"  width="4"  height="2"  fill="#ffd700"/>
</svg>`,
    metric: { label: "Subs", value: "—" },
    currentTask: "IN DEVELOPMENT",
    stub: {
      tagline: "This week's build",
      potential: "Package the swing trader's signals as $97/mo alerts. 30 subscribers = $2,910/mo = API costs covered. Proof-of-system marketing flywheel.",
    },
  },
];

export function getAgent(id: string): AgentDef | undefined {
  return AGENTS.find((a) => a.id === id);
}
