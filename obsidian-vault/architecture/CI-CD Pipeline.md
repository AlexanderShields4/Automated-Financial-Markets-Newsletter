# CI/CD Pipeline

## Overview

The project uses **GitHub Actions** for two automated workflows:
1. **Daily Newsletter** - Scheduled cron job that runs the full pipeline
2. **Backfill** - Manual workflow for filling historical gaps

## Daily Newsletter Workflow

**File:** `.github/workflows/daily_newsletter.yml`

### Trigger

```yaml
on:
  schedule:
    - cron: '45 20 * * 1-5'  # 8:45 PM UTC = 4:45 PM ET
  workflow_dispatch:           # Manual trigger button
```

- **Cron expression:** `minute hour day-of-month month day-of-week`
- `45 20 * * 1-5` = 20:45 UTC, Monday through Friday
- **4:45 PM ET** is chosen because US markets close at 4:00 PM ET, giving 45 minutes for closing data to propagate to APIs
- `workflow_dispatch` allows manual runs for testing

### Job Steps

```yaml
jobs:
  collect-newsletter:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4          # 1. Get code

      - uses: docker/setup-buildx-action@v3 # 2. Setup Docker BuildX

      - uses: docker/build-push-action@v5   # 3. Build image with caching
        with:
          context: .
          load: true
          tags: newsletter:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - run: |                              # 4. Run collector in container
          docker run --rm \
            -e SUPABASE_URL=${{ secrets.SUPABASE_URL }} \
            -e SUPABASE_SERVICE_KEY=${{ secrets.SUPABASE_SERVICE_KEY }} \
            -e GOOGLE_KEY=${{ secrets.GOOGLE_KEY }} \
            -e fred_api_key=${{ secrets.FRED_API_KEY }} \
            -e NewsApikey=${{ secrets.NEWS_API_KEY }} \
            newsletter:latest \
            python3 newsletter_collector.py
```

### Docker Build Caching

The `cache-from: type=gha` / `cache-to: type=gha,mode=max` uses **GitHub Actions cache** for Docker layer caching:
- First run: builds all layers (~2-3 min for pip install)
- Subsequent runs: reuses cached layers (~10-20 seconds)
- Only rebuilds when `requirements.txt` or `Dockerfile` changes
- `mode=max` caches all layers, not just the final image

### Secrets Management

API keys are stored as **GitHub Repository Secrets**:
- Never committed to code
- Injected as environment variables at runtime
- Accessible only to repository admins
- Passed to Docker via `-e` flags

## Backfill Workflow

**File:** `.github/workflows/backfill.yml`

### Trigger

```yaml
on:
  workflow_dispatch:
    inputs:
      start_date:
        description: 'Start date (YYYY-MM-DD, inclusive)'
        required: true
      end_date:
        description: 'End date (YYYY-MM-DD, defaults to yesterday)'
        required: false
      force:
        description: 'Re-run dates already in database'
        required: false
        default: 'false'
```

This is a **manual-only workflow** with typed inputs that appear as a form in the GitHub UI.

### Backfill Logic

The `backfill.py` script:

1. **Queries existing dates** from Supabase to avoid duplicates
2. **Generates business days** in the requested range (skips weekends)
3. **Filters out** dates already in the database (unless `force=true`)
4. **Warns** about dates > 30 days old (NewsAPI limitation)
5. **Loops** through each missing date, running `newsletter_collector.py`
6. **Reports** success/failure counts

```
Example:
  Input: start_date=2024-01-01, end_date=2024-01-31
  Existing: [2024-01-02, 2024-01-03, 2024-01-15]
  Process: Runs for 19 remaining business days
  Output: "Backfill complete: 18 success, 1 failed"
```

## Why Docker?

The pipeline runs in Docker containers for:

1. **Reproducibility** - Same Python version, same dependencies, every run
2. **Isolation** - No conflicts with GitHub Actions runner environment
3. **Portability** - Same container works locally, in CI, and in any cloud
4. **Caching** - Docker layers cache pip installs, making rebuilds fast

### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "newsletter_dashboard.py"]
```

**Note:** The default CMD runs Streamlit (for local development), but CI overrides it with `python3 newsletter_collector.py`.

## Related Notes
- [[Docker]] - Containerization details
- [[GitHub Actions]] - Platform deep dive
- [[Data Collection Pipeline]] - What the pipeline collects
