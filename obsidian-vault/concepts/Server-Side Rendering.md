# Server-Side Rendering (SSR)

## The Rendering Spectrum

```
Server-Side Rendering ◄────────────────────► Client-Side Rendering
(HTML generated on server)                    (HTML generated in browser)

SSR          SSG          ISR          CSR
│            │            │            │
Server       Build-time   Hybrid       Browser
renders      pre-renders  revalidates  renders
per request  all pages    periodically everything
```

## CSR (Client-Side Rendering) - The Baseline

Traditional React SPA approach:

```
1. Browser requests page
2. Server sends empty HTML + big JS bundle
3. Browser downloads and executes JS
4. JS fetches data from APIs
5. React renders the UI

Time to content: ████████████████ (slow)
```

**Problems:**
- Blank screen until JS loads ("white flash")
- Poor SEO (search engines see empty HTML)
- Large JavaScript bundles
- Every user re-does the same work

## SSR (Server-Side Rendering)

How Next.js works:

```
1. Browser requests page
2. Server runs React components
3. Server fetches data (direct DB access!)
4. Server generates complete HTML
5. Browser receives ready-to-display HTML
6. Browser hydrates (attaches JS for interactivity)

Time to content: ████ (fast)
```

**Benefits:**
- Immediate content display
- Great SEO (search engines see full HTML)
- Server fetches data faster (closer to DB)
- Less JavaScript sent to browser

## How Next.js 16 App Router Handles This

### Server Components (Default)

Every component in the `app/` directory is a Server Component by default:

```tsx
// This component runs ONLY on the server
// No JavaScript is sent to the client for this component
export default async function DashboardPage() {
    // Direct database query - no API endpoint needed
    const { data } = await supabase
        .from("daily_briefs")
        .select("*")
        .order("date", { ascending: false })
        .limit(1)
        .single();

    return (
        <div>
            <h1>Latest Brief: {data.date}</h1>
            <p>{data.full_text}</p>
        </div>
    );
}
```

**What happens:**
1. Server executes the component (including the DB query)
2. Server generates HTML
3. HTML is sent to the client
4. No React JavaScript for this component is sent to the client

### Client Components (Opt-in)

When you need interactivity:

```tsx
"use client";  // This directive makes it a Client Component

import { useState } from "react";

export default function NewsFilter() {
    const [category, setCategory] = useState("all");

    return (
        <div>
            <button onClick={() => setCategory("markets")}>Markets</button>
            <button onClick={() => setCategory("economy")}>Economy</button>
            {/* ... */}
        </div>
    );
}
```

**Client Components are needed for:**
- `useState`, `useEffect`, `useRef`
- Event handlers (`onClick`, `onChange`)
- Browser APIs (`window`, `document`)
- Third-party libraries that use hooks (Recharts, Framer Motion)

### The Composition Pattern

```tsx
// Server Component (page.tsx) - fetches data
export default async function Page() {
    const data = await fetchData();  // Runs on server

    return (
        <div>
            <h1>Dashboard</h1>                      {/* Server-rendered */}
            <YieldCurveChart data={data.yields} />  {/* Client Component */}
            <SpreadChart data={data.spreads} />      {/* Client Component */}
        </div>
    );
}
```

The page fetches data on the server and passes it as props to interactive Client Components. Best of both worlds: server-side data fetching + client-side interactivity.

## Hydration

The process of making server-rendered HTML interactive:

```
Server HTML:  <button>Click me (0)</button>     ← Static HTML
                         │
                    Hydration
                         │
Interactive:  <button onClick={increment}>Click me (0)</button>  ← Now works!
```

1. Browser receives and displays HTML immediately (fast first paint)
2. React JS loads and "hydrates" - attaches event listeners to existing HTML
3. Page becomes interactive

**Hydration mismatch:** If the server HTML doesn't match what React expects, you get console warnings. This happens when using browser-only values (like `window.innerWidth`) during server rendering.

## How This Project Uses SSR

| Page | Rendering | Why |
|------|-----------|-----|
| `/` (Dashboard) | SSR | Fetches latest brief from Supabase on each request |
| `/briefs` (Archives) | SSR | Lists all dates from DB |
| `/briefs/[date]` | SSR | Fetches specific brief by date |
| Charts (Recharts) | Client | Requires browser DOM for canvas rendering |
| News filter | Client | Requires `useState` for filter state |
| Animations (Framer) | Client | Requires browser APIs |

## Related Notes
- [[Next.js Frontend]] - The framework implementing SSR
- [[Frontend Architecture]] - Overall frontend strategy
