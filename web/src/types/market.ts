export interface MarketData {
  indice_data_str: string;
  ticker_data: string;
  newsstr: string;
  yield_data: Record<string, Record<string, number | null>>;
  yield_spreads: Record<string, Record<string, number | null>>;
  tenyrtwoyr?: string[];
}

export interface DailyBrief {
  date: string;
  full_text: string;
  structured_data: MarketData;
}
