# Common Questions

## Architecture & Design

### "Walk me through the data flow."

> "Every weekday at 4:45 PM ET, GitHub Actions triggers a Docker container that runs the collection script. It pulls treasury yields and economic data from FRED, stock prices and indices from Yahoo Finance, and news headlines from NewsAPI. It computes yield spreads, formats everything, and sends it to Gemini 2.5-Flash which generates a ~1000-word market brief. That brief is then embedded into a 768-dimensional vector. All three artifacts - the text, the structured data as JSONB, and the embedding - are upserted into a Supabase PostgreSQL database. The Next.js frontend reads from that same database using server-side rendering."

### "Why did you choose Supabase over [Postgres/Firebase/DynamoDB]?"

> "Three reasons: First, it gives me PostgreSQL with the pgvector extension, so I can store both relational data and vector embeddings in one database - no need for a separate vector DB like Pinecone. Second, it auto-generates a REST API from my schema, so I didn't need to build a backend API layer. Third, it has official SDKs for both Python and JavaScript, which my two application layers need."

### "Why not use a dedicated vector database?"

> "For the scale of this project - hundreds of briefs, not millions - pgvector in PostgreSQL is more than sufficient. A dedicated vector DB would add infrastructure complexity, another service to manage, and the need to sync data between two databases. Keeping everything in one PostgreSQL instance gives me joins, transactions, and vector search in one place."

### "How would you scale this?"

> "Several dimensions:
> - **More data sources:** The collection is modular - I'd add new sources as independent try/except blocks
> - **Higher frequency:** Move from daily to intraday by switching the cron to hourly
> - **More users:** Supabase scales PostgreSQL connections via connection pooling. Add CDN caching for the Next.js frontend
> - **Larger dataset:** If millions of briefs, consider IVFFlat index (faster builds) or a dedicated vector DB
> - **Real-time:** Add Supabase Realtime subscriptions for live updates"

## AI & ML

### "How does the RAG system work?"

> "When a user asks a question, I embed their query using the same Gemini embedding model used for documents. Then I call a PostgreSQL function that finds the top 5 most similar briefs using cosine similarity on the HNSW index. Those briefs are concatenated into a prompt that instructs Gemini to answer the question using only the provided context. The similarity threshold of 0.5 filters out irrelevant results."

### "How do you handle hallucination?"

> "Four strategies: First, the generation prompt explicitly tells the model to reference specific numbers from the provided data. Second, the RAG prompt restricts the model to only use retrieved context. Third, the 0.5 similarity threshold prevents irrelevant documents from entering context. Fourth, I include source dates so users can verify the information."

### "Why Gemini Flash and not GPT-4 or Claude?"

> "For the generation task, I need cost-efficient structured summarization, not complex reasoning. Flash is significantly cheaper and faster than frontier models. It also means I get both text generation and embeddings from one provider with one SDK. For this specific use case - transforming structured data into a formatted summary - Flash's quality is excellent."

### "What would you improve about the RAG?"

> "Three things: First, hybrid search - combining vector similarity with keyword matching for better recall. Second, metadata filtering - letting users constrain by date range before vector search. Third, a reranking step using a cross-encoder to improve precision on the retrieved results. I'd also add evaluation metrics - relevance scoring and faithfulness checks."

## Technical Implementation

### "Why Docker for a Python script?"

> "Reproducibility in CI. Without Docker, I'd need to manage Python versions, system dependencies, and pip environments on the GitHub Actions runner. With Docker, the environment is identical every time. Docker layer caching also makes rebuilds fast - pip install is cached unless requirements.txt changes."

### "How do you handle API failures?"

> "Each data source is wrapped in its own try/except block. If FRED is down, I still get stock data and news. The AI prompt is designed to work with partial data - it will note missing sections and continue. The backfill workflow also tracks success/failure counts per date so I know exactly what needs re-running."

### "Why JSONB instead of normalized tables?"

> "The structured data is write-once-read-many. It's always consumed as a unit (one day's data) and never queried across days by individual fields. JSONB avoids the complexity of 5+ normalized tables and the joins needed to reconstruct a day's data. If I needed cross-day aggregation queries (e.g., 'average S&P 500 this month'), I'd normalize."

### "Explain the HNSW index."

> "HNSW builds a multi-layer navigable graph. Higher layers have fewer nodes and act as 'highways' for fast navigation. Search starts at the top layer, greedily moves toward the query vector, then drops to lower layers for finer-grained search. It provides O(log n) approximate nearest neighbor search with over 99% recall. For this project's scale, even brute force would work, but HNSW gives us the right semantics and will scale."

## Frontend

### "Why two frontends?"

> "Streamlit was the prototype - it's amazing for building data dashboards quickly in Python. The Next.js app is the production frontend with proper SSR, responsive design, and animations. They serve different purposes: Streamlit for data exploration and the RAG chat, Next.js for a polished public-facing experience."

### "How does SSR work in your Next.js app?"

> "App Router components are Server Components by default. When a user requests a page, Next.js runs the component on the server, including the Supabase query, generates HTML, and sends it to the browser. Interactive components like charts are Client Components marked with 'use client' - they're hydrated on the client after the initial HTML renders. This gives fast first paint and good SEO."

## Behavioral

### "What was the hardest part?"

> "Getting the data pipeline reliable. Each API has different failure modes, rate limits, and data formats. Yahoo Finance sometimes returns NaN values that break JSON serialization. FRED data has varying release schedules. News API has a 30-day limit. Building robust error handling for each source while keeping the pipeline flowing was the main engineering challenge."

### "What would you do differently?"

> "I'd add monitoring and alerting from day one. Right now I don't know if the daily run fails until I check manually. I'd set up a health check endpoint and Slack notifications. I'd also add automated evaluation for the RAG system - measuring retrieval relevance and answer faithfulness."

## Related Notes
- [[Project Walkthrough Script]] - How to present the project
- [[Key Design Decisions]] - Deeper reasoning
- [[Tradeoffs and Limitations]] - Honest assessment
