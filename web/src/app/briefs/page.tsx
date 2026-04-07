import { supabase } from "@/lib/supabase";
import Link from "next/link";
import { FolderArchive, ChevronRight, Activity } from "lucide-react";

export const revalidate = 3600;

export default async function BriefsIndex() {
  const { data: briefs, error } = await supabase
    .from('daily_briefs')
    .select('date')
    .order('date', { ascending: false });

  if (error || !briefs || briefs.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center h-[60vh]">
        <h2 className="text-3xl font-extrabold mb-2 heading-gradient">Archive Is Empty</h2>
        <p className="text-slate-400">The database appears to hold no past records.</p>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto flex flex-col gap-10 relative z-10">
      <div className="flex flex-col items-center text-center max-w-2xl mx-auto space-y-6">
        <div className="p-4 bg-indigo-500/10 rounded-full shadow-[0_0_30px_rgba(99,102,241,0.2)]">
          <FolderArchive className="w-10 h-10 text-indigo-400" />
        </div>
        <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-br from-indigo-100 to-purple-400">
          Historical Archives
        </h1>
        <p className="text-slate-400 text-lg md:text-xl leading-relaxed">
          Browse our extensive database of AI-generated daily market briefs, covering macroeconomic data, yield curves, and global news highlights.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-6">
        {briefs.map((brief) => (
          <Link 
            key={brief.date} 
            href={`/briefs/${brief.date}`}
            className="group relative glass-panel rounded-2xl p-6 transition-all hover:-translate-y-1 hover:shadow-lg hover:shadow-indigo-500/20 focus:outline-none focus:ring-2 focus:ring-indigo-500 overflow-hidden"
          >
            <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-indigo-500/0 via-indigo-500/50 to-purple-500/0 opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div className="flex items-center justify-between mb-4">
              <span className="font-bold text-lg tracking-wide text-slate-200 group-hover:text-white transition-colors">{brief.date}</span>
              <div className="w-8 h-8 rounded-full bg-slate-800/50 flex items-center justify-center group-hover:bg-indigo-500/20 transition-colors">
                <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-indigo-300 transition-colors" />
              </div>
            </div>
            <div className="flex items-center gap-2 text-xs font-medium text-slate-500 uppercase tracking-widest group-hover:text-indigo-400/80 transition-colors">
              <Activity className="w-3 h-3" />
              Market Brief
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
