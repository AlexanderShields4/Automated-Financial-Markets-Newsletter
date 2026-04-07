# Supabase

## What is Supabase?

Supabase is an **open-source Firebase alternative** built on top of PostgreSQL. It provides:

- **PostgreSQL database** - Full relational database with extensions
- **PostgREST API** - Auto-generated REST API from your schema
- **Authentication** - User management and JWT-based auth
- **Storage** - File storage (S3-compatible)
- **Realtime** - WebSocket subscriptions for live data
- **Edge Functions** - Serverless functions (Deno runtime)

## Why Supabase for This Project?

1. **PostgreSQL + pgvector** - Native vector support for embeddings, no separate vector DB needed
2. **Managed service** - No database administration, automatic backups
3. **Free tier** - Generous free tier for small projects (500MB database, 50K monthly active users)
4. **Client libraries** - Official SDKs for Python and JavaScript (both used in this project)
5. **RPC functions** - Can define PostgreSQL functions and call them via the API

## How It's Used

### Python Client (Backend)

```python
from supabase import create_client

supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_SERVICE_KEY"]  # Service key = full access
)

# Insert/update a brief
supabase.table("daily_briefs").upsert({
    "date": "2024-01-15",
    "full_text": "...",
    "structured_data": {...},
    "embedding": [0.123, -0.456, ...]
}).execute()

# Call RPC function for vector search
supabase.rpc("match_daily_briefs", {
    "query_embedding": [...],
    "match_threshold": 0.5,
    "match_count": 5
}).execute()
```

### JavaScript Client (Frontend)

```typescript
import { createClient } from "@supabase/supabase-js";

const supabase = createClient(url, anonKey);

// Fetch latest brief
const { data } = await supabase
    .from("daily_briefs")
    .select("*")
    .order("date", { ascending: false })
    .limit(1)
    .single();

// Fetch all briefs for archive
const { data: briefs } = await supabase
    .from("daily_briefs")
    .select("id, date, created_at")
    .order("date", { ascending: false });
```

## Key Concepts

### Service Key vs Anon Key

| | Service Key | Anon Key |
|---|---|---|
| **Access level** | Full admin access | Restricted by RLS |
| **Used in** | Backend (Python) | Frontend (Next.js) |
| **Exposure** | Server-side only, never in client | Safe to expose in browser |
| **RLS** | Bypasses Row Level Security | Subject to RLS policies |

### PostgREST

Supabase automatically generates a REST API from your PostgreSQL schema:
- `GET /rest/v1/daily_briefs` → `SELECT * FROM daily_briefs`
- `POST /rest/v1/daily_briefs` → `INSERT INTO daily_briefs`
- Query params map to SQL: `?date=eq.2024-01-15` → `WHERE date = '2024-01-15'`

The client libraries are wrappers around these REST endpoints.

### pgvector Extension

PostgreSQL extension that adds:
- `VECTOR(n)` data type for storing n-dimensional vectors
- Distance operators: `<=>` (cosine), `<->` (L2/Euclidean), `<#>` (inner product)
- Index types: HNSW, IVFFlat

This means you don't need a separate vector database (like Pinecone, Weaviate, or Qdrant). Everything lives in one PostgreSQL instance.

### Why Not a Dedicated Vector DB?

| PostgreSQL + pgvector | Dedicated Vector DB (Pinecone, etc.) |
|---|---|
| One database for everything | Separate service to manage |
| SQL joins across vector and relational data | Need to sync data between systems |
| Free with Supabase | Usually paid at scale |
| Good enough for < 1M vectors | Optimized for billions of vectors |
| Familiar PostgreSQL tooling | New query language/API to learn |

For this project (hundreds of briefs), pgvector is more than sufficient.

## Related Notes
- [[Database Design]] - Schema and index details
- [[Vector Embeddings]] - What's stored in the embedding column
- [[HNSW Index]] - The vector index algorithm
