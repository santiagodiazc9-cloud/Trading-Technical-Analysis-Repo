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
    routines: ["routines/2_market_open_execution.md"],
    detailRoute: "/daytrader",
  },
  {
    id: "crypto-screener",
    name: "Crypto Screener",
    icon: "₿",
    color: "purple",
    description: "24/7 on-chain + CEX momentum",
    defaultStatus: "stub",
    pixelArt: CRYPTO_SVG,
    metric: { label: "Signals", value: "—" },
    stub: { tagline: "Always on", potential: "Crypto trend momentum" },
  },
  {
    id: "content-engine",
    name: "Content Engine",
    icon: "✍",
    color: "blue",
    description: "SEO posts → affiliate rev",
    defaultStatus: "stub",
    pixelArt: CONTENT_SVG,
    metric: { label: "Posts", value: "—" },
    stub: { tagline: "Passive income", potential: "Affiliate + ad revenue" },
  },
  {
    id: "freelance-agent",
    name: "Freelance Agent",
    icon: "🤝",
    color: "orange",
    description: "Auto-bids Upwork / Fiverr gigs",
    defaultStatus: "stub",
    pixelArt: FREELANCE_SVG,
    metric: { label: "Bids", value: "—" },
    stub: { tagline: "Gig economy", potential: "Contract revenue" },
  },
  {
    id: "arbitrage-scout",
    name: "Arbitrage Scout",
    icon: "🔄",
    color: "cyan",
    description: "Cross-platform price gaps",
    defaultStatus: "stub",
    pixelArt: ARBITRAGE_SVG,
    metric: { label: "Gaps", value: "—" },
    stub: { tagline: "Price delta", potential: "Arbitrage spread" },
  },
];

export function getAgent(id: string): AgentDef | undefined {
  return AGENTS.find((a) => a.id === id);
}
