# GitHub Actions

## What is GitHub Actions?

GitHub's built-in CI/CD platform. It runs **workflows** (YAML files) in response to **events** (push, schedule, manual trigger).

## Core Concepts

### Workflow
A YAML file in `.github/workflows/` that defines an automated process.

### Event/Trigger
What starts the workflow:
```yaml
on:
  push:                          # Code pushed
  pull_request:                  # PR opened/updated
  schedule:                      # Cron schedule
    - cron: '45 20 * * 1-5'
  workflow_dispatch:             # Manual trigger
    inputs:                      # With form inputs
      start_date:
        required: true
```

### Job
A set of steps that run on a single runner (VM):
```yaml
jobs:
  collect-newsletter:
    runs-on: ubuntu-latest       # Runner OS
    steps: [...]
```

### Step
Individual commands or actions within a job:
```yaml
steps:
  - uses: actions/checkout@v4    # Pre-built action
  - run: echo "Hello"            # Shell command
```

### Action
Reusable units (like npm packages for CI):
- `actions/checkout@v4` - Clone the repo
- `docker/setup-buildx-action@v3` - Setup Docker BuildX
- `docker/build-push-action@v5` - Build Docker images

## Cron Syntax

```
┌───────────── minute (0-59)
│ ┌───────────── hour (0-23)
│ │ ┌───────────── day of month (1-31)
│ │ │ ┌───────────── month (1-12)
│ │ │ │ ┌───────────── day of week (0-6, Sun=0)
│ │ │ │ │
45 20 * * 1-5
```

`45 20 * * 1-5` = minute 45, hour 20 (UTC), any day of month, any month, Monday-Friday

**Important:** GitHub Actions cron uses UTC. 20:45 UTC = 4:45 PM Eastern (during EDT).

**Caveat:** GitHub Actions cron is not perfectly punctual. Jobs may be delayed by a few minutes during peak load.

## Secrets Management

```yaml
# Stored in: Settings → Secrets and variables → Actions
# Referenced as:
${{ secrets.SUPABASE_URL }}
${{ secrets.GOOGLE_KEY }}
```

- Encrypted at rest
- Masked in logs (if printed, shows `***`)
- Only available to workflows in the same repository
- Can be scoped to environments (production, staging)

## Workflow Dispatch Inputs

```yaml
on:
  workflow_dispatch:
    inputs:
      start_date:
        description: 'Start date (YYYY-MM-DD)'
        required: true
        type: string
      force:
        description: 'Re-run existing dates'
        type: boolean
        default: false
```

Creates a form in the GitHub UI. Referenced in steps as:
```yaml
- run: python backfill.py --start ${{ github.event.inputs.start_date }}
```

## GitHub Actions Cache

```yaml
cache-from: type=gha
cache-to: type=gha,mode=max
```

- **`type=gha`** - Uses GitHub Actions' built-in cache (10GB per repo)
- **`mode=max`** - Caches ALL intermediate layers, not just final
- Cache is shared across workflow runs on the same branch
- Automatically evicted when size limit is reached (LRU)

## Cost

- **Public repos:** Unlimited free minutes
- **Private repos:** 2,000 free minutes/month (Linux runners)
- **Docker builds with caching:** ~30 seconds after initial build
- **Full pipeline run:** ~2-3 minutes including data collection

## Related Notes
- [[CI-CD Pipeline]] - How these workflows are configured
- [[Docker]] - The containers these workflows build and run
