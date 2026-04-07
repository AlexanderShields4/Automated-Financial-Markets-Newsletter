"use client";

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface YieldCurveChartProps {
  yieldData: Record<string, Record<string, number | null>>;
  reportDate: string;
}

const tenors = ['3M', '6M', '1Y', '2Y', '3Y', '5Y', '7Y', '10Y', '20Y', '30Y'];

export default function YieldCurveChart({ yieldData, reportDate }: YieldCurveChartProps) {
  // Transform data for the chosen date
  const data = tenors.map(tenor => {
    const series = yieldData[tenor] || {};
    // Use the value for reportDate, or fallback to the latest available in the series
    let val = series[reportDate];
    if (val === undefined || val === null) {
      const vals = Object.values(series).filter(v => v !== null);
      if (vals.length > 0) val = vals[vals.length - 1];
    }
    return {
      tenor,
      yield: val
    };
  }).filter(d => d.yield !== undefined && d.yield !== null);

  return (
    <div className="w-full h-[300px]">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 10, right: 10, left: 10, bottom: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
          <XAxis dataKey="tenor" stroke="var(--foreground)" fontSize={12} tickLine={false} axisLine={false} />
          <YAxis stroke="var(--foreground)" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(v) => `${v}%`} />
          <Tooltip 
            contentStyle={{ backgroundColor: 'var(--card)', border: '1px solid var(--border)', borderRadius: '12px', color: '#f8fafc', fontSize: '13px', backdropFilter: 'blur(16px)', boxShadow: '0 4px 20px rgba(0,0,0,0.5)' }}
            itemStyle={{ color: '#8b5cf6', fontWeight: 'bold', fontSize: '15px' }}
            formatter={(value: any) => [`${value}%`, 'Yield']}
          />
          <Line type="monotone" dataKey="yield" stroke="var(--primary)" strokeWidth={3} dot={{ r: 4, fill: 'var(--primary)' }} activeDot={{ r: 6 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
