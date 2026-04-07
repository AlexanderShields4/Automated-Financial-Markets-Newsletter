"use client";

import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { format, parseISO } from 'date-fns';

interface SpreadChartProps {
  spreadData: Record<string, number | null>;
  title: string;
}

export default function SpreadChart({ spreadData, title }: SpreadChartProps) {
  // Transform the { "YYYY-MM-DD": value } into sorted array
  const data = Object.entries(spreadData || {})
    .filter(([_, val]) => val !== null && !isNaN(val))
    .map(([date, val]) => ({
      date,
      value: val as number,
      dateFormatted: format(parseISO(date), 'MMM d')
    }))
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

  if (data.length === 0) return <div className="p-4 text-sm text-gray-500">No data available</div>;

  const latestVal = data[data.length - 1].value;

  return (
    <div className="w-full flex justify-center flex-col relative h-[250px]">
      <div className="absolute top-2 right-4 bg-[var(--background)] px-2 py-1 rounded-md border border-[var(--border)] text-xs font-bold text-[var(--primary)] z-10 shadow-sm">
        Latest: {latestVal.toFixed(2)}%
      </div>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 20, right: 10, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id={`colorValue-${title}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="var(--primary)" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
          <XAxis 
            dataKey="dateFormatted" 
            stroke="var(--foreground)" 
            fontSize={10} 
            tickLine={false} 
            axisLine={false}
            tick={{ fill: 'var(--foreground)', opacity: 0.6 }}
            minTickGap={20}
          />
          <YAxis 
            stroke="var(--foreground)" 
            fontSize={10} 
            tickLine={false} 
            axisLine={false} 
            tickFormatter={(v) => `${v}%`}
            tick={{ fill: 'var(--foreground)', opacity: 0.6 }}
          />
          <Tooltip 
            contentStyle={{ backgroundColor: 'var(--card)', border: '1px solid var(--border)', borderRadius: '12px', color: '#f8fafc', fontSize: '12px', backdropFilter: 'blur(16px)', boxShadow: '0 4px 20px rgba(0,0,0,0.5)' }}
            itemStyle={{ color: '#8b5cf6', fontWeight: 'bold' }}
            formatter={(value: any) => [`${Number(value).toFixed(2)}%`, 'Spread']}
            labelFormatter={(label) => `Date: ${label}`}
          />
          <ReferenceLine y={0} stroke="var(--accent)" strokeDasharray="3 3" />
          <Area type="monotone" dataKey="value" stroke="var(--primary)" strokeWidth={2} fillOpacity={1} fill={`url(#colorValue-${title})`} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
