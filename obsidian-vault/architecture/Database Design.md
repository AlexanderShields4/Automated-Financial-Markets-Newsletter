# Database Design

## Platform: Supabase

[[Supabase]] is used as the database platform. Under the hood, it's **PostgreSQL** with the **pgvector** extension for vector operations.

## Schema

### `daily_briefs` Table

```sql
CREATE TABLE daily_briefs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date        DATE UNIQUE NOT NULL,
    full_text   TEXT NOT NULL,
    structured_data JSONB,
    embedding   VECTOR(768),
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Column Breakdown

| Column | Type | Purpose |
|--------|------|---------|
| `id` | UUID | Auto-generated primary key. UUIDs prevent enumeration attacks and work across distributed systems |
| `date` | DATE (UNIQUE) | The market date this brief covers. Unique constraint ensures one brief per day |
| `full_text` | TEXT | The AI-generated newsletter in plain text. Used for display and as RAG context |
| `structured_data` | JSONB | Raw market data (yields, prices, spreads, news). Enables frontend charts without re-fetching |
| `embedding` | VECTOR(768) | 768-dimensional vector from Gemini's embedding model. Powers semantic search |
| `created_at` | TIMESTAMPTZ | Auto-set creation timestamp for auditing |

### Why JSONB for structured_data?

**JSONB** (Binary JSON) is PostgreSQL's structured document storage:
- **Flexible schema** - Market data structure can evolve without migrations
- **Indexable** - Can create GIN indexes on specific JSON paths if needed
- **Queryable** - Supports operators like `->`, `->>`, `@>` for JSON querying
- **Compact** - Binary format is more efficient than TEXT-stored JSON

The alternative would be normalizing into separate tables (yields, spreads, stocks, news), but JSONB is simpler for a write-once-read-many pattern where the data is always consumed as a unit.

## Vector Index

```sql
CREATE INDEX daily_briefs_embedding_idx
ON daily_briefs
USING hnsw (embedding vector_cosine_ops);
```

This creates an **HNSW (Hierarchical Navigable Small World)** index for fast approximate nearest neighbor search.

> See [[HNSW Index]] for how this algorithm works.

**Key parameters:**
- `vector_cosine_ops` - Uses [[Cosine Similarity]] as the distance metric
- Default HNSW params: `m=16, ef_construction=64` (good defaults for datasets < 1M rows)

### Why HNSW over IVFFlat?

| | HNSW | IVFFlat |
|---|---|---|
| Build time | Slower | Faster |
| Query time | Faster | Slower |
| Recall | Higher | Lower |
| Memory | More | Less |
| Need to retrain? | No | Yes (after significant inserts) |

For this project, HNSW is ideal because:
- Dataset is small (hundreds of rows, not millions)
- Query speed matters for user-facing RAG
- No retraining needed as new briefs are added daily

## RPC Function: `match_daily_briefs`

```sql
CREATE OR REPLACE FUNCTION match_daily_briefs(
    query_embedding vector(768),
    match_threshold float,
    match_count int
)
RETURNS TABLE (
    id uuid,
    date date,
    full_text text,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        daily_briefs.id,
        daily_briefs.date,
        daily_briefs.full_text,
        1 - (daily_briefs.embedding <=> query_embedding) as similarity
    FROM daily_briefs
    WHERE 1 - (daily_briefs.embedding <=> query_embedding) > match_threshold
    ORDER BY daily_briefs.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
```

### How It Works

1. Takes a query embedding (768-d vector), a similarity threshold, and max results
2. `<=>` is pgvector's cosine distance operator
3. `1 - distance = similarity` (converts distance to similarity score)
4. Filters results below the threshold
5. Returns top matches ordered by relevance

### Why an RPC Function?

- **Encapsulation** - Complex vector math is hidden behind a clean interface
- **Supabase client compatibility** - Supabase's Python/JS clients can call RPC functions directly: `supabase.rpc("match_daily_briefs", params)`
- **Performance** - Runs server-side, avoiding transferring all embeddings to the client
- **Security** - Row Level Security (RLS) can be applied at the function level

## Database Initialization

The `db_setup.py` script handles schema creation:
1. Connects via `psycopg2` (direct PostgreSQL connection)
2. Enables `vector` extension
3. Creates the table
4. Creates the HNSW index
5. Creates the RPC function

This is idempotent (`CREATE TABLE IF NOT EXISTS`, `CREATE OR REPLACE FUNCTION`).

## Related Notes
- [[Supabase]] - The platform powering this
- [[Vector Embeddings]] - What goes in the embedding column
- [[HNSW Index]] - The indexing algorithm
- [[Cosine Similarity]] - The distance metric used
- [[RAG System]] - How the database powers Q&A
