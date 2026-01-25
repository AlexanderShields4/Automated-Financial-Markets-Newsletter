import os
import time
from dotenv import load_dotenv
from supabase import create_client, Client
# import postgres # Removed unused import
# Note: creating tables directly via supabase-py client is not standard for DDL. 
# We usually use the SQL editor or a direct postgres connection.
# Since the user asked for a script, we will use a direct Postgres connection if available 
# or standard requests if needed. 
# However, usually for "db_setup.py" in python with Supabase, one uses `psycopg2` or `sqlalchemy` pointing to the connection string.

# I will use `psycopg2` (assuming it is installed or accessible via langchain prerequisites) for DDL operations.
# If not available, we could assume the user runs this SQL in the supabase dashboard, but the user asked for a script.

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def setup_database():
    load_dotenv()
    
    # We need the DIRECT postgres connection string (port 5432)
    # e.g. postgresql://postgres:password@db.projectref.supabase.co:5432/postgres
    db_url = os.getenv("SUPABASE_DB_URL") 
    
    if not db_url:
        print("Error: SUPABASE_DB_URL is not set in .env")
        print("Please add your connection string: postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres")
        return

    try:
        print("Connecting to database...")
        conn = psycopg2.connect(db_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # 1. Enable Vector Extension (needs superuser or extension privileges, usually enabled in Supabase by default or allowed)
        print("Enabling vector extension...")
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        
        # 2. Create Table
        print("Creating daily_briefs table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS daily_briefs (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                date DATE UNIQUE NOT NULL,
                full_text TEXT NOT NULL,
                structured_data JSONB,
                embedding VECTOR(768),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        
        # 3. Create Index (Optional but recommended for performance)
        # Using ivfflat as a starting point.
        # Note: Index creation requires data typically, or can be done empty. 
        # hnsw is often better but more expensive to build.
        print("Creating vector index (hnsw)...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS daily_briefs_embedding_idx 
            ON daily_briefs USING hnsw (embedding vector_cosine_ops);
        """)

        # 4. Create RPC function for similarity search
        print("Creating match_daily_briefs RPC function...")
        cur.execute("""
            create or replace function match_daily_briefs (
              query_embedding vector(768),
              match_threshold float,
              match_count int
            )
            returns table (
              id uuid,
              date date,
              full_text text,
              similarity float
            )
            language plpgsql
            as $$
            begin
              return query
              select
                daily_briefs.id,
                daily_briefs.date,
                daily_briefs.full_text,
                1 - (daily_briefs.embedding <=> query_embedding) as similarity
              from daily_briefs
              where 1 - (daily_briefs.embedding <=> query_embedding) > match_threshold
              order by daily_briefs.embedding <=> query_embedding
              limit match_count;
            end;
            $$;
        """)

        print("Database setup completed successfully.")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    setup_database()
