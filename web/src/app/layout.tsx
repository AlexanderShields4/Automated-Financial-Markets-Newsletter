import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Link from 'next/link';
import { Network, Calendar, LayoutDashboard } from 'lucide-react';

const inter = Inter({ subsets: ["latin"], display: 'swap' });

export const metadata: Metadata = {
  title: "Automated Financial Markets",
  description: "AI-powered specialized financial intelligence tool",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} min-h-screen text-slate-100 selection:bg-indigo-500/30 selection:text-indigo-200`}>
        {/* Animated Background */}
        <div className="blob-bg">
          <div className="blob blob-1"></div>
          <div className="blob blob-2"></div>
          <div className="blob blob-3"></div>
        </div>

        <div className="flex flex-col min-h-screen relative z-0">
          <header className="fixed top-0 w-full z-50 glass-panel border-b border-white/10 border-t-0 border-x-0 !shadow-none !rounded-none backdrop-blur-xl bg-black/40">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
              <Link href="/" className="flex items-center gap-3 group">
                <div className="p-2 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl shadow-lg shadow-indigo-500/20 group-hover:shadow-indigo-500/40 transition-all">
                  <Network className="h-5 w-5 text-white" />
                </div>
                <span className="font-bold text-xl tracking-wide bg-clip-text text-transparent bg-gradient-to-r from-indigo-200 via-white to-purple-200">
                  Market<span className="font-light">AI</span>
                </span>
              </Link>
              <nav className="flex items-center gap-1 sm:gap-2">
                <Link href="/" className="text-sm font-medium text-slate-300 hover:text-white hover:bg-white/10 px-4 py-2 rounded-lg transition-all flex items-center gap-2">
                  <LayoutDashboard className="w-4 h-4" />
                  <span className="hidden sm:inline">Dashboard</span>
                </Link>
                <Link href="/briefs" className="text-sm font-medium text-slate-300 hover:text-white hover:bg-white/10 px-4 py-2 rounded-lg transition-all flex items-center gap-2">
                  <Calendar className="w-4 h-4" />
                  <span className="hidden sm:inline">Archives</span>
                </Link>
              </nav>
            </div>
          </header>

          <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-28 pb-12">
            {children}
          </main>

          <footer className="mt-auto border-t border-white/5 bg-black/20 backdrop-blur-md">
            <div className="max-w-7xl mx-auto px-4 py-8 flex items-center justify-center text-sm text-slate-500">
              <p className="flex items-center gap-1">
                © {new Date().getFullYear()} Automated Financial Markets • Built with Gemini & Supabase
              </p>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
