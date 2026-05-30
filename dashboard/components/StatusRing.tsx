import type { AgentStatus } from "@/lib/agents";

const COLOR_MAP: Record<string, string> = {
  emerald: "#10b981",
  amber:   "#f59e0b",
  purple:  "#8b5cf6",
  blue:    "#3b82f6",
  orange:  "#f97316",
  cyan:    "#06b6d4",
};

export default function StatusRing({
  status,
  color,
}: {
  status: AgentStatus;
  color: string;
}) {
  const hex = COLOR_MAP[color] ?? "#94a3b8";
  const isActive = status === "active";
  const isStub = status === "stub";

  return (
    <span
      className="relative inline-flex h-3 w-3 rounded-full"
      title={status}
    >
      {isActive && (
        <span
          className="absolute inline-flex h-full w-full rounded-full opacity-75 animate-ping"
          style={{ backgroundColor: hex }}
        />
      )}
      <span
        className="relative inline-flex h-3 w-3 rounded-full"
        style={{
          backgroundColor: isStub ? "transparent" : hex,
          border: isStub ? `2px solid #475569` : `2px solid ${hex}`,
          opacity: status === "offline" ? 0.4 : 1,
        }}
      />
    </span>
  );
}
