import { supabase } from "@/lib/supabase";
import { DailyBrief } from "@/types/market";
import YieldCurveChart from "@/components/YieldCurveChart";
import SpreadChart from "@/components/SpreadChart";
import NewsList from "@/components/NewsList";
import ReactMarkdown from 'react-markdown';
import { CalendarDays, AlertCircle, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export const revalidate = 3600; 

interface PageProps {
  params: { date: string };
}

export default async function BriefDetail({ params }: PageProps) {
  const { date } = params;

  const { data: briefs, error } = await supabase
    .from('daily_briefs')
    .select('*')
    .eq('date', date)
    .limit(1);

  if (error || !briefs || briefs.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center h-[60vh]">
        <AlertCircle className="w-16 h-16 text-pink-500 mb-6 drop-shadow-md" />
        <h2 className="text-3xl font-extrabold mb-2 heading-gradient">Data Not Found</h2>
        <p className="text-slate-400 mb-8">No newsletter archive found for {date}</p>
        <Link href="/briefs" className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium transition-colors shadow-lg shadow-indigo-500/30">
          <ArrowLeft className="w-4 h-4" /> Return to Archives
        </Link>
      </div>
    );
  }

  const brief = briefs[0] as DailyBrief;
  const marketData = brief.structured_data;

  const spreadsToPlot = [
    { title: '10Y-2Y Spread', key: '10Y-2Y' },
    { title: '10Y-3M Spread', key: '10Y-3M' },
    { title: '5Y-2Y Spread', key: '5Y-2Y' },
    { title: '30Y-5Y Spread', key: '30Y-5Y' }
  ];

  return (
    <div className="flex flex-col gap-8">
      {/* Header Actions */}
      <div className="flex items-center">
        <Link href="/briefs" className="inline-flex items-center gap-2 px-4 py-2 glass-panel rounded-xl text-slate-300 hover:text-white hover:bg-white/10 transition-all font-medium text-sm">
          <ArrowLeft className="w-4 h-4" /> Back to Archives
        </Link>
      </div>

      <section className="mb-2">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-panel mb-6 border-pink-500/30 text-pink-200">
          <CalendarDays className="w-4 h-4 text-pink-400" />
          <span className="text-sm font-semibold tracking-wide">HISTORICAL ARCHIVE: {date}</span>
        </div>
        <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-slate-100 via-white to-slate-400 drop-shadow-sm">
          Market Brief <span className="text-slate-500 font-light">/ {date}</span>
        </h1>
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 relative z-10">
        {/* Main Analysis Column */}
        <div className="lg:col-span-7 xl:col-span-8 flex flex-col gap-8">
          <section className="glass-panel rounded-3xl overflow-hidden relative">
            <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-pink-500 to-purple-500"></div>
            <div className="p-8 md:p-10">
              <h2 className="text-2xl font-bold mb-8 flex items-center gap-3">
                <span className="p-2 bg-indigo-500/10 rounded-xl text-indigo-400">📝</span>
                Executive Summary
              </h2>
              <div className="prose prose-premium prose-lg max-w-none">
                <ReactMarkdown>{brief.full_text}</ReactMarkdown>
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
          <div className="glass-panel rounded-3xl p-6 lg:p-8 relative overflow-hidden">
            <h3 className="text-xl font-bold mb-6">📉 U.S. Treasury Curve</h3>
            <YieldCurveChart yieldData={marketData.yield_data} reportDate={date} />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 gap-6">
            {spreadsToPlot.map((spread) => {
              const data = marketData.yield_spreads?.[spread.key];
              if (!data) return null;
              return (
                <div key={spread.key} className="glass-panel rounded-3xl p-6 lg:p-8 relative overflow-hidden transition-all hover:bg-white/5">
                  <h3 className="text-sm font-bold text-slate-400 mb-4 tracking-widest uppercase">{spread.title}</h3>
                  <SpreadChart spreadData={data as Record<string, number>} title={spread.title} />
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
