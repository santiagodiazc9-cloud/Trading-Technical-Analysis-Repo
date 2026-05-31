"use client";
import { useState, useEffect, use } from "react";
import { useRouter } from "next/navigation";
import { AGENTS, getAgent } from "@/lib/agents";
import type { AgentStatus } from "@/lib/agents";
import StatusRing from "@/components/StatusRing";
import {
  fetchAgents,
  fetchJournal,
  fetchChatHistory,
  postChat,
  triggerRoutine,
} from "@/lib/api";
import Link from "next/link";

const GLOW_COLOR: Record<string, string> = {
  emerald: "#10b981",
  amber:   "#f59e0b",
  purple:  "#8b5cf6",
  blue:    "#3b82f6",
  orange:  "#f97316",
  cyan:    "#06b6d4",
};

export default function AgentDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const router = useRouter();
  const agent = getAgent(id);

  const [liveStatus, setLiveStatus] = useState<AgentStatus | undefined>();
  const [liveMetric, setLiveMetric] = useState<{ label: string; value: string } | undefined>();
  const [journal, setJournal] = useState<{ content: string; date: string; exists: boolean } | null>(null);
  const [chatHistory, setChatHistory] = useState<any[]>([]);
  const [question, setQuestion] = useState("");
  const [sending, setSending] = useState(false);
  const [triggered, setTriggered] = useState<string | null>(null);

  useEffect(() => {
    if (!agent) return;
    const load = async () => {
      try {
        const [agents, j, ch] = await Promise.all([
          fetchAgents(),
          fetchJournal(),
          fetchChatHistory(),
        ]);
        const live = agents.find((a: any) => a.id === id);
        if (live) {
          setLiveStatus(live.status);
          setLiveMetric(live.metric);
        }
        setJournal(j);
        setChatHistory(ch?.items ?? []);
      } catch {}
    };
    load();
    const iv = setInterval(load, 30_000);
    return () => clearInterval(iv);
  }, [id, agent]);

  if (!agent) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-3 text-center">
        <div className="text-slate-500 text-4xl">404</div>
        <p className="text-slate-400 text-sm">Agent not found</p>
        <Link href="/" className="text-xs text-slate-500 hover:text-white">← Fleet</Link>
      </div>
    );
  }

  const glow = GLOW_COLOR[agent.color] ?? "#475569";
  const status = liveStatus ?? agent.defaultStatus;

  // ── Stub page ────────────────────────────────────────────────────────────────
  if (agent.stub) {
    return (
      <div className="flex flex-col gap-4">
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <Link href="/" className="hover:text-white">Fleet</Link>
          <span>/</span>
          <span>{agent.name}</span>
        </div>

        <div
          className="rounded-xl border p-6 bg-[#0f1318] flex flex-col gap-4"
          style={{ borderColor: `${glow}33` }}
        >
          <div className="flex items-start justify-between gap-4">
            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-2">
                <StatusRing status="stub" color={agent.color} />
                <span className="text-xs tracking-widest text-slate-500">NOT DEPLOYED</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-3xl">{agent.icon}</span>
                <h1 className="text-xl font-bold text-white">{agent.name}</h1>
              </div>
              <p className="text-sm text-slate-400">{agent.description}</p>
            </div>
            <div
              dangerouslySetInnerHTML={{ __html: agent.pixelArt }}
              style={{ imageRendering: "pixelated", width: 64, height: 64, transform: "scale(2)", transformOrigin: "top right", flexShrink: 0 }}
            />
          </div>

          <div className="border-t border-slate-800 pt-4 flex flex-col gap-3">
            <div className="text-xs text-slate-500 uppercase tracking-widest">What would this agent do?</div>
            <p className="text-sm text-slate-300">
              <span className="font-semibold" style={{ color: glow }}>{agent.stub.tagline}</span>
              {" — "}
              {agent.stub.potential}
            </p>
          </div>

          <div className="rounded-lg p-4 text-center text-sm"
            style={{
              border: agent.currentTask === "IN DEVELOPMENT"
                ? `1px dashed ${glow}40`
                : "1px dashed #334155",
              background: agent.currentTask === "IN DEVELOPMENT"
                ? `${glow}06`
                : "transparent",
            }}>
            {agent.currentTask === "IN DEVELOPMENT" ? (
              <>
                <div className="flex items-center justify-center gap-2 mb-1">
                  <span className="w-1.5 h-1.5 rounded-full animate-ping" style={{ backgroundColor: glow, opacity: 0.7 }}/>
                  <span className="text-[10px] tracking-widest font-bold" style={{ color: glow }}>IN DEVELOPMENT THIS WEEK</span>
                </div>
                <span className="text-slate-500 text-[11px]">Building now — check back soon.</span>
              </>
            ) : (
              <>
                <span className="text-slate-500">Not deployed yet. </span>
                <span className="text-slate-400">Come back soon.</span>
              </>
            )}
          </div>
        </div>

        <Link href="/" className="text-xs text-slate-600 hover:text-slate-400">← Back to fleet</Link>
      </div>
    );
  }

  // ── Live agent page ──────────────────────────────────────────────────────────
  const handleAsk = async () => {
    if (!question.trim()) return;
    setSending(true);
    await postChat(question.trim());
    setQuestion("");
    const ch = await fetchChatHistory();
    setChatHistory(ch?.items ?? []);
    setSending(false);
  };

  const handleTrigger = async (routine: string) => {
    setTriggered(routine);
    await triggerRoutine(routine);
    setTimeout(() => setTriggered(null), 2000);
  };

  return (
    <div className="flex flex-col gap-4">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-500">
        <Link href="/" className="hover:text-white">Fleet</Link>
        <span>/</span>
        <span style={{ color: glow }}>{agent.name}</span>
      </div>

      {/* Agent header */}
      <div
        className="rounded-xl border p-4 bg-[#0f1318] flex items-center justify-between gap-4"
        style={{ borderColor: `${glow}44`, boxShadow: `0 0 20px ${glow}1a` }}
      >
        <div className="flex items-center gap-3">
          <div
            dangerouslySetInnerHTML={{ __html: agent.pixelArt }}
            style={{ imageRendering: "pixelated", width: 40, height: 40, flexShrink: 0 }}
          />
          <div>
            <div className="flex items-center gap-2">
              <StatusRing status={status} color={agent.color} />
              <span className="text-lg font-bold text-white">{agent.icon} {agent.name}</span>
            </div>
            <p className="text-xs text-slate-400">{agent.description}</p>
          </div>
        </div>
        {liveMetric && (
          <div className="text-right">
            <div className="text-xs text-slate-500">{liveMetric.label}</div>
            <div className="text-xl font-bold" style={{ color: glow }}>{liveMetric.value}</div>
          </div>
        )}
      </div>

      {/* 3-panel grid */}
      <div className="grid md:grid-cols-3 gap-3">

        {/* Journal feed */}
        <div className="flex flex-col gap-2 bg-[#0f1318] rounded-lg border border-slate-800 p-3">
          <div className="text-xs font-bold tracking-widest text-slate-500">TODAY&apos;S JOURNAL</div>
          {journal?.exists ? (
            <pre className="text-xs text-slate-300 whitespace-pre-wrap leading-relaxed overflow-auto max-h-64">
              {journal.content.slice(0, 1200)}{journal.content.length > 1200 ? "\n…" : ""}
            </pre>
          ) : (
            <p className="text-xs text-slate-600 italic">No journal entry yet for {journal?.date ?? "today"}.</p>
          )}
        </div>

        {/* Chat */}
        <div className="flex flex-col gap-2 bg-[#0f1318] rounded-lg border border-slate-800 p-3">
          <div className="text-xs font-bold tracking-widest text-slate-500">ASK THE AGENT</div>
          <div className="flex gap-1">
            <input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleAsk()}
              placeholder="Ask a question…"
              className="flex-1 bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-slate-500"
            />
            <button
              onClick={handleAsk}
              disabled={sending || !question.trim()}
              className="px-2 py-1 rounded text-xs font-bold disabled:opacity-40 transition-opacity"
              style={{ backgroundColor: glow, color: "#000" }}
            >
              {sending ? "…" : "→"}
            </button>
          </div>
          <div className="flex flex-col gap-1 overflow-auto max-h-48">
            {chatHistory.length === 0 && (
              <p className="text-xs text-slate-600 italic">No questions queued.</p>
            )}
            {[...chatHistory].reverse().map((item: any, i: number) => (
              <div key={i} className="text-xs border border-slate-800 rounded p-2">
                <div className="text-slate-300">{item.question}</div>
                <div className="text-slate-600 mt-0.5">{item.queued_at?.slice(0, 16).replace("T", " ")}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Controls */}
        <div className="flex flex-col gap-2 bg-[#0f1318] rounded-lg border border-slate-800 p-3">
          <div className="text-xs font-bold tracking-widest text-slate-500">CONTROLS</div>

          {/* Deep page link */}
          {agent.detailRoute && (
            <Link
              href={agent.detailRoute}
              className="text-xs rounded px-3 py-2 text-center font-bold transition-opacity hover:opacity-80"
              style={{ backgroundColor: `${glow}22`, color: glow, border: `1px solid ${glow}44` }}
            >
              Open {agent.name} Panel →
            </Link>
          )}

          {/* Trigger routines */}
          {agent.routines && agent.routines.length > 0 && (
            <>
              <div className="text-[10px] text-slate-600 uppercase tracking-wider mt-1">Trigger routine</div>
              {agent.routines.map((r) => {
                const label = r.split("/").pop()?.replace(".md", "").replace(/_/g, " ") ?? r;
                const isTriggered = triggered === r;
                return (
                  <button
                    key={r}
                    onClick={() => handleTrigger(r)}
                    disabled={!!triggered}
                    className="text-xs rounded px-3 py-1.5 text-left text-slate-300 border border-slate-700 hover:border-slate-500 disabled:opacity-40 transition-all"
                    style={isTriggered ? { borderColor: glow, color: glow } : {}}
                  >
                    {isTriggered ? "✓ Queued" : `▶ ${label}`}
                  </button>
                );
              })}
            </>
          )}
        </div>
      </div>

      <Link href="/" className="text-xs text-slate-600 hover:text-slate-400">← Back to fleet</Link>
    </div>
  );
}
