import type { Metadata, Viewport } from "next";
import { Geist_Mono } from "next/font/google";
import "./globals.css";
import BottomNav from "@/components/BottomNav";

const mono = Geist_Mono({ variable: "--font-mono", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Trading Agent",
  description: "Swing + Day Trading Control Panel",
  manifest: "/manifest.json",
  appleWebApp: { capable: true, statusBarStyle: "black-translucent", title: "Trading Agent" },
};

export const viewport: Viewport = {
  themeColor: "#0f172a",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${mono.variable} h-full`}>
      <body className="min-h-full bg-slate-950 text-slate-100 font-mono pb-16 md:pb-0 md:pl-16">
        <aside className="hidden md:flex fixed left-0 top-0 h-full w-16 bg-slate-900 border-r border-slate-800 flex-col items-center py-4 gap-6 z-10">
          <SideNav />
        </aside>
        <main className="max-w-5xl mx-auto px-3 py-4">{children}</main>
        <BottomNav />
      </body>
    </html>
  );
}

function SideNav() {
  return (
    <>
      <NavIcon href="/" label="Fleet" icon="◉" />
      <NavIcon href="/swing" label="Swing" icon="↗" />
      <NavIcon href="/daytrader" label="Day" icon="⚡" />
      <NavIcon href="/positions" label="Positions" icon="◈" />
      <NavIcon href="/settings" label="Settings" icon="⚙" />
    </>
  );
}

function NavIcon({ href, label, icon }: { href: string; label: string; icon: string }) {
  return (
    <a href={href} title={label}
       className="w-10 h-10 flex items-center justify-center rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors text-lg">
      {icon}
    </a>
  );
}
