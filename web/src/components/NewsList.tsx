"use client";

import { useState } from "react";
import { Filter, ExternalLink } from "lucide-react";

interface NewsListProps {
  newsStr: string;
}

export default function NewsList({ newsStr }: NewsListProps) {
  const [selectedCategories, setSelectedCategories] = useState<string[]>(['Markets', 'Economy']);

  if (!newsStr) return <div className="text-sm text-slate-500">No news data available.</div>;

  const lines = newsStr.split('\n').slice(2); // Skip header lines
  
  const allCategories = ["Markets", "Economy", "Companies", "Commodities", "Currencies"];
  const keywords = {
    "Markets": ["stock", "market", "index", "s&p", "dow", "nasdaq"],
    "Economy": ["gdp", "inflation", "economy", "fed", "rates"],
    "Companies": ["inc", "corp", "company", "ceo"],
    "Commodities": ["oil", "gold", "commodity", "crude"],
    "Currencies": ["dollar", "currency", "forex", "usd"]
  };

  const getCategories = (headline: string) => {
    const categories: string[] = [];
    Object.entries(keywords).forEach(([cat, words]) => {
      if (words.some(word => headline.toLowerCase().includes(word))) {
        categories.push(cat);
      }
    });
    return categories.length > 0 ? categories : ["Other"];
  };

  const newsItems = lines.filter(l => l.trim()).map(line => {
    const parts = line.split("Source:");
    const headline = parts[0].replace(/^\d+\.\s*/, '').trim(); // Remove leading number
    let source = "Unknown";
    let url = "";
    
    if (parts.length > 1) {
      const sourceUrlParts = parts[1].split("URL:");
      source = sourceUrlParts[0].trim();
      if (sourceUrlParts.length > 1) url = sourceUrlParts[1].trim();
    }
    
    return { headline, source, url, categories: getCategories(headline) };
  });

  const filteredItems = newsItems.filter(item => 
    selectedCategories.length === 0 || item.categories.some(cat => selectedCategories.includes(cat))
  ).slice(0, 15); // Show top 15

  const toggleCategory = (cat: string) => {
    if (selectedCategories.includes(cat)) {
      setSelectedCategories(selectedCategories.filter(c => c !== cat));
    } else {
      setSelectedCategories([...selectedCategories, cat]);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center gap-2 mb-2 p-1">
        <Filter className="w-4 h-4 text-slate-500 mr-2" />
        {allCategories.map(cat => (
          <button
            key={cat}
            onClick={() => toggleCategory(cat)}
            className={`px-4 py-1.5 text-xs rounded-full font-bold tracking-wide transition-all shadow-sm ${
              selectedCategories.includes(cat) 
              ? 'bg-gradient-to-r from-pink-500 to-rose-500 text-white shadow-pink-500/30' 
              : 'bg-white/5 border border-white/10 text-slate-400 hover:text-white hover:bg-white/10'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-4">
        {filteredItems.map((item, idx) => (
          <a
            key={idx}
            href={item.url || '#'}
            target="_blank"
            rel="noopener noreferrer"
            className="group block p-5 rounded-2xl glass-panel border-l-[3px] border-l-pink-500/80 hover:border-l-pink-500 transition-all hover:translate-x-1 hover:shadow-lg hover:shadow-pink-500/10 focus:outline-none focus:ring-2 focus:ring-pink-500"
          >
            <div className="flex items-start justify-between gap-4 relative">
              <h4 className="font-bold text-base sm:text-lg leading-snug mb-3 text-slate-200 group-hover:text-white transition-colors">{item.headline}</h4>
              <ExternalLink className="w-4 h-4 text-slate-600 group-hover:text-pink-400 flex-shrink-0 mt-1 transition-colors" />
            </div>
            
            <div className="flex items-center gap-2 flex-wrap mt-1">
              <span className="inline-flex px-2.5 py-1 rounded-md bg-black/40 text-slate-300 border border-white/5 text-[0.65rem] uppercase font-bold tracking-wider">
                {item.source}
              </span>
              {item.categories.map(cat => (
                <span key={cat} className="inline-flex px-2.5 py-1 rounded-md bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 text-[0.65rem] uppercase font-bold tracking-wider">
                  {cat}
                </span>
              ))}
            </div>
          </a>
        ))}
        {filteredItems.length === 0 && (
           <p className="text-sm text-slate-500 py-8 text-center glass-panel rounded-2xl">No news matches the selected filters.</p>
        )}
      </div>
    </div>
  );
}
