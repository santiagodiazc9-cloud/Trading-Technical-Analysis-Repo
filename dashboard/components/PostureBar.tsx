const COLORS: Record<string, string> = {
  GREEN: "bg-emerald-500 text-emerald-950",
  CAUTION: "bg-yellow-400 text-yellow-950",
  RED: "bg-red-500 text-white",
  BEAR: "bg-slate-600 text-white",
  UNKNOWN: "bg-slate-700 text-slate-300",
};

const EMOJI: Record<string, string> = {
  GREEN: "🟢", CAUTION: "🟡", RED: "🔴", BEAR: "⚫", UNKNOWN: "⬜",
};

export default function PostureBar({ posture }: { posture: string }) {
  const color = COLORS[posture] ?? COLORS.UNKNOWN;
  return (
    <div className={`rounded-lg px-4 py-2 text-sm font-semibold flex items-center gap-2 ${color}`}>
      <span>{EMOJI[posture] ?? "⬜"}</span>
      <span>Market Posture: {posture}</span>
    </div>
  );
}
