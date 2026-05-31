import type { Metadata, Viewport } from "next";
import { Geist_Mono } from "next/font/google";
import "./globals.css";

const mono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Agent Fleet — Mission Control",
  description: "Autonomous AI agent command center",
  manifest: "/manifest.json",
  appleWebApp: { capable: true, statusBarStyle: "black-translucent", title: "Agent Fleet" },
};

export const viewport: Viewport = {
  themeColor: "#020510",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${mono.variable} h-full`}>
      <body className="h-full bg-[#020510] text-slate-100 font-mono overflow-hidden">
        {children}
      </body>
    </html>
  );
}
