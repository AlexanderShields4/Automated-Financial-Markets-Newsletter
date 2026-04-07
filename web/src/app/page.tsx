import { supabase } from "@/lib/supabase";
import { DailyBrief } from "@/types/market";
import YieldCurveChart from "@/components/YieldCurveChart";
import SpreadChart from "@/components/SpreadChart";
import NewsList from "@/components/NewsList";
import ReactMarkdown from 'react-markdown';
import { CalendarDays, AlertCircle } from 'lucide-react';

export const revalidate = 3600;

export default async function Home() {
  const { data: briefs, error } = await supabase
    .from('daily_briefs')
    .select('*')
    .order('date', { ascending: false })
    .limit(1);

  if (error || !briefs || briefs.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center h-[60vh]">
        <AlertCircle className="w-16 h-16 text-pink-500 mb-6 drop-shadow-md" />
        <h2 className="text-3xl font-extrabold mb-3 heading-gradient">No Market Data Found</h2>
        <p className="text-slate-400">Ensure the Supabase database contains recent entries.</p>
      </div>
    );
  }

  const latestBrief = briefs[0] as DailyBrief;
  const marketData = latestBrief.structured_data;

  const spreadsToPlot = [
    { title: '10Y-2Y Spread', key: '10Y-2Y' },
    { title: '10Y-3M Spread', key: '10Y-3M' },
    { title: '5Y-2Y Spread', key: '5Y-2Y' },
    { title: '30Y-5Y Spread', key: '30Y-5Y' }
  ];

  return (
    <div className="flex flex-col gap-8">
      {/* Premium Hero Section */}
      <section className="mb-4">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-panel mb-6 border-indigo-500/30 text-indigo-200 shadow-[0_0_15px_rgba(99,102,241,0.2)]">
          <CalendarDays className="w-4 h-4 text-indigo-400" />
          <span className="text-sm font-semibold tracking-wide">LATEST BRIEFING: {latestBrief.date}</span>
        </div>
        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-4 text-transparent bg-clip-text bg-gradient-to-r from-slate-100 via-white to-slate-400 drop-shadow-sm">
          Market <span className="text-transparent bg-clip-text bg-gradient-to-br from-indigo-400 to-purple-500">Intelligence</span>
        </h1>
        <p className="text-xl text-slate-400 max-w-2xl leading-relaxed">
          AI-generated synthesis of today&apos;s macroeconomic indicators, yield variations, and top tier corporate news.
        </p>
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 relative z-10">
        {/* Main Analysis Column */}
        <div className="lg:col-span-7 xl:col-span-8 flex flex-col gap-8">
          <section className="glass-panel rounded-3xl overflow-hidden relative">
            <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-indigo-500 to-purple-500"></div>
            <div className="p-8 md:p-10">
              <h2 className="text-2xl font-bold mb-8 flex items-center gap-3">
                <span className="p-2 bg-indigo-500/10 rounded-xl text-indigo-400">📝</span>
                Executive Summary
              </h2>
              <div className="prose prose-premium prose-lg max-w-none">
                <ReactMarkdown>{latestBrief.full_text}</ReactMarkdown>
              </div>
            </div>
          </section>

          <section className="glass-panel rounded-3xl overflow-hidden p-8 md:p-10">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-3 border-b border-white/5 pb-6">
              <span className="p-2 bg-pink-500/10 rounded-xl text-pink-400">📰</span>
              Global Headlines
            </h2>
            <NewsList newsStr={marketData.newsstr} />
          </section>
        </div>

        {/* Tactical Charts Column */}
        <div className="lg:col-span-5 xl:col-span-4 flex flex-col gap-6">
          <div className="glass-panel rounded-3xl p-6 lg:p-8 relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/10 rounded-full blur-3xl -mr-16 -mt-16 transition-all group-hover:bg-indigo-500/20"></div>
            <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
              U.S. Treasury Curve
              <span className="flex h-2 w-2 relative ml-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
              </span>
            </h3>
            <YieldCurveChart yieldData={marketData.yield_data} reportDate={latestBrief.date} />
          </div>

          {spreadsToPlot.map((spread) => {
            const data = marketData.yield_spreads?.[spread.key];
            if (!data) return null;
            return (
              <div key={spread.key} className="glass-panel rounded-3xl p-6 lg:p-8 relative overflow-hidden group transition-all hover:bg-white/5">
                <h3 className="text-sm font-bold text-slate-400 mb-4 tracking-widest uppercase">{spread.title}</h3>
                <SpreadChart spreadData={data as Record<string, number>} title={spread.title} />
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
