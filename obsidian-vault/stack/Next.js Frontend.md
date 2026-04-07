# Next.js Frontend

## Next.js 16 with App Router

Next.js is a **React framework** that adds server-side rendering, routing, and build tooling on top of React.

### App Router vs Pages Router

This project uses the **App Router** (introduced in Next.js 13, now the default):

| Feature | App Router (this project) | Pages Router (legacy) |
|---------|--------------------------|----------------------|
| Directory | `src/app/` | `src/pages/` |
| Components | Server Components default | Client Components default |
| Layouts | Nested `layout.tsx` files | `_app.tsx` wrapper |
| Data fetching | `async` components, `fetch()` | `getServerSideProps`, `getStaticProps` |
| Streaming | Built-in with Suspense | Not supported |

### Server Components vs Client Components

**Server Components** (default - no directive needed):
```tsx
// This runs on the server only
export default async function Page() {
    const data = await fetchFromDB();  // Direct DB call, no API route needed
    return <div>{data.title}</div>;    // HTML sent to client, no JS bundle
}
```

**Client Components** (opt-in with `"use client"`):
```tsx
"use client";
import { useState } from "react";

export default function Counter() {
    const [count, setCount] = useState(0);
    return <button onClick={() => setCount(count + 1)}>{count}</button>;
}
```

> See [[Server-Side Rendering]] for the full SSR lifecycle.

### File-Based Routing

```
src/app/
├── layout.tsx          → Wraps ALL pages (root layout)
├── page.tsx            → renders at /
├── globals.css         → Global styles
└── briefs/
    ├── page.tsx        → renders at /briefs
    └── [date]/
        └── page.tsx    → renders at /briefs/2024-01-15
```

- `page.tsx` = a route
- `layout.tsx` = wraps child routes (persistent across navigation)
- `[date]` = dynamic route segment (accessible via `params.date`)

## React 19

Key features used:
- **Server Components** - Default in App Router
- **Suspense boundaries** - For streaming SSR
- **Improved hydration** - Faster client-side activation

## TypeScript 5

Strict mode enabled in `tsconfig.json`:
```json
{
  "compilerOptions": {
    "strict": true,
    "paths": { "@/*": ["./src/*"] }  // Path aliases
  }
}
```

The `@/*` alias means `import { supabase } from "@/lib/supabase"` resolves to `src/lib/supabase.ts`.

## Tailwind CSS 4

Utility-first CSS framework. Instead of writing CSS classes, you compose styles inline:

```tsx
// Traditional CSS approach
<div className="card">...</div>
// .card { display: flex; padding: 1rem; border-radius: 0.5rem; }

// Tailwind approach
<div className="flex p-4 rounded-lg">...</div>
```

**Tailwind 4** changes (vs 3):
- CSS-first configuration (no `tailwind.config.js` needed)
- Uses `@import "tailwindcss"` in CSS
- Faster build with Rust-based engine (Oxide)
- Theme customization via CSS variables

### Helper Libraries

**`tailwind-merge`** - Intelligently merges Tailwind classes (avoids conflicts):
```tsx
twMerge("p-4 p-6") // → "p-6" (last wins)
```

**`clsx`** - Conditional class names:
```tsx
clsx("base", isActive && "bg-blue-500", isDisabled && "opacity-50")
```

## Recharts 3

Declarative React charting library used for:

**Yield Curve Chart:**
```tsx
<LineChart data={yieldData}>
    <XAxis dataKey="date" />
    <YAxis />
    <Line dataKey="DGS2" stroke="#8884d8" />
    <Line dataKey="DGS10" stroke="#82ca9d" />
    {/* ... 10 total lines */}
</LineChart>
```

**Spread Chart:**
```tsx
<AreaChart data={spreadData}>
    <defs>
        <linearGradient id="gradient">
            <stop offset="0%" stopColor="#8884d8" stopOpacity={0.8}/>
            <stop offset="100%" stopColor="#8884d8" stopOpacity={0}/>
        </linearGradient>
    </defs>
    <Area dataKey="10Y-2Y" fill="url(#gradient)" />
</AreaChart>
```

## Framer Motion 12

Animation library for React:
```tsx
import { motion } from "framer-motion";

<motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5 }}
>
    Content fades in and slides up
</motion.div>
```

Used for page transitions, card animations, and loading states.

## Supabase JS SDK

```typescript
// lib/supabase.ts
import { createClient } from "@supabase/supabase-js";

export const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);
```

**`NEXT_PUBLIC_` prefix** - Makes environment variables available in client-side code. Without this prefix, Next.js keeps them server-only.

## Date-fns 4

Lightweight date manipulation (alternative to Moment.js):
```typescript
import { format, parseISO } from "date-fns";
format(parseISO("2024-01-15"), "MMMM d, yyyy") // "January 15, 2024"
```

## Related Notes
- [[Frontend Architecture]] - How this fits in the system
- [[Server-Side Rendering]] - SSR concepts explained
- [[Supabase]] - Database client
