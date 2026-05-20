"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/", label: "Home", icon: "⊞" },
  { href: "/swing", label: "Swing", icon: "↗" },
  { href: "/daytrader", label: "Day", icon: "⚡" },
  { href: "/positions", label: "Hold", icon: "◈" },
  { href: "/settings", label: "Setup", icon: "⚙" },
];

export default function BottomNav() {
  const path = usePathname();
  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-slate-900 border-t border-slate-800 flex justify-around py-2 z-10">
      {links.map((l) => (
        <Link key={l.href} href={l.href}
          className={`flex flex-col items-center gap-0.5 text-xs px-3 py-1 rounded-lg transition-colors
            ${path === l.href ? "text-emerald-400" : "text-slate-500 hover:text-slate-300"}`}>
          <span className="text-base">{l.icon}</span>
          <span>{l.label}</span>
        </Link>
      ))}
    </nav>
  );
}
