# Frontend Architecture

## Dual Frontend Strategy

This project has **two frontends**, each serving a different purpose:

| | Streamlit | Next.js |
|---|---|---|
| **Purpose** | Rapid prototyping, data exploration | Production web app |
| **Users** | Developer/analyst (you) | End users / portfolio |
| **Features** | Interactive charts, RAG chat | Archives, responsive UI |
| **Rendering** | Server-rendered Python | SSR + client hydration |
| **Styling** | Built-in Streamlit widgets | Tailwind CSS + Framer Motion |

## Streamlit Dashboard (`newsletter_dashboard.py`)

### Features

**Tab 1: Dashboard**
- Latest brief display with formatted sections
- Plotly interactive yield curve chart
- Plotly spread charts (4 key spreads)
- News articles with category filtering
- Market index cards

**Tab 2: Market Chat**
- RAG-powered Q&A interface
- Uses `rag_engine.py` to search historical briefs
- Chat history maintained in `st.session_state`

### Key Streamlit Concepts

```python
# Session state - persists across reruns
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Columns layout
col1, col2 = st.columns([2, 1])
with col1:
    st.plotly_chart(yield_curve_fig)
with col2:
    st.metric("S&P 500", "5,234.18", "+1.2%")

# Caching - prevents re-fetching on every interaction
@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_latest_brief():
    return supabase.table("daily_briefs")...
```

### Credential Handling
```python
# Supports both Streamlit Cloud and local deployment
try:
    url = st.secrets["SUPABASE_URL"]       # Streamlit Cloud
except:
    url = os.environ["SUPABASE_URL"]        # Local / Docker
```

## Next.js Web App (`web/`)

### Stack

- **Next.js 16** with App Router
- **React 19** with Server Components
- **TypeScript 5** in strict mode
- **Tailwind CSS 4** for styling
- **Recharts 3** for data visualization
- **Framer Motion 12** for animations
- **Supabase JS SDK** for data fetching

> See [[Next.js Frontend]] for detailed stack explanation.

### Route Structure (App Router)

```
web/src/app/
├── layout.tsx          # Root layout (header, footer, providers)
├── page.tsx            # / → Dashboard (latest brief)
├── globals.css         # Global styles, Tailwind imports
└── briefs/
    ├── page.tsx        # /briefs → Archives grid
    └── [date]/
        └── page.tsx    # /briefs/2024-01-15 → Specific brief
```

### Key Components

**`YieldCurveChart.tsx`**
- Recharts `LineChart` rendering 10 Treasury tenors
- X-axis: dates, Y-axis: yield percentages
- Color-coded lines for each tenor

**`SpreadChart.tsx`**
- Recharts `AreaChart` with gradient fills
- Shows 10Y-2Y, 10Y-3M, 5Y-2Y, 30Y-5Y over time
- Visual indicator of yield curve inversion (negative values)

**`NewsList.tsx`**
- Filterable news article list
- Categories: Markets, Economy, Companies, Commodities, Currencies
- Each article shows title, source, and publication date

### TypeScript Interfaces

```typescript
// types/market.ts
interface MarketData {
    yield_data: Record<string, Record<string, number>>;
    yield_spreads: Record<string, Record<string, number>>;
    indice_data_str: string;
    ticker_data: string;
    newsstr: string;
    economic_indicators: Record<string, number>;
}

interface DailyBrief {
    id: string;
    date: string;
    full_text: string;
    structured_data: MarketData;
    created_at: string;
}
```

### Data Fetching Pattern

```typescript
// Server Component (runs on server, no client JS)
export default async function DashboardPage() {
    const { data } = await supabase
        .from("daily_briefs")
        .select("*")
        .order("date", { ascending: false })
        .limit(1)
        .single();

    return <BriefDisplay brief={data} />;
}
```

**Server Components** (default in App Router):
- Fetch data on the server
- No JavaScript sent to client for data fetching
- Better SEO, faster initial load
- Can't use hooks or browser APIs

**Client Components** (marked with `"use client"`):
- Charts, interactive elements
- Can use `useState`, `useEffect`, event handlers
- Hydrated on the client after server render

### Styling Approach

```css
/* globals.css */
@import "tailwindcss";
@import "tailwindcss/theme" theme(static);

/* Custom theme variables */
:root {
    --background: #0a0a0a;
    --foreground: #ededed;
}
```

Uses Tailwind utility classes throughout:
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
```

## Related Notes
- [[Next.js Frontend]] - Detailed stack deep dive
- [[Server-Side Rendering]] - SSR concepts
- [[Supabase]] - Data source for both frontends
