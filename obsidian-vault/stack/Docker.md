# Docker

## What is Docker?

Docker packages applications into **containers** - lightweight, standalone, executable units that include everything needed to run: code, runtime, libraries, and system tools.

## How Docker is Used in This Project

### Dockerfile

```dockerfile
FROM python:3.9-slim     # Base image: minimal Debian + Python 3.9

WORKDIR /app             # Set working directory inside container
COPY requirements.txt .  # Copy deps manifest first (layer caching)
RUN pip install --no-cache-dir -r requirements.txt  # Install deps

COPY . .                 # Copy all project files

EXPOSE 8501              # Document that Streamlit uses port 8501
CMD ["streamlit", "run", "newsletter_dashboard.py"]  # Default command
```

### Layer Caching Strategy

Docker builds images in **layers**. Each instruction creates a layer, and layers are cached:

```
Layer 1: python:3.9-slim          (cached unless base image updates)
Layer 2: COPY requirements.txt    (cached unless requirements.txt changes)
Layer 3: pip install              (cached unless Layer 2 changes)
Layer 4: COPY . .                 (rebuilds when ANY file changes)
```

**Key optimization:** `requirements.txt` is copied and installed *before* the rest of the code. This means code changes don't invalidate the pip install cache (~2-3 minutes saved per build).

### `--no-cache-dir` Flag

```
pip install --no-cache-dir -r requirements.txt
```

Prevents pip from storing downloaded packages in cache. In a container, there's no benefit to caching (the container is ephemeral), so this reduces image size.

## Two Execution Modes

### Mode 1: Local Dashboard (Default CMD)
```bash
docker build -t newsletter .
docker run -p 8501:8501 --env-file .env newsletter
# Opens Streamlit dashboard at http://localhost:8501
```

### Mode 2: CI Pipeline (Override CMD)
```bash
docker run --rm \
  -e SUPABASE_URL=... \
  -e GOOGLE_KEY=... \
  newsletter:latest \
  python3 newsletter_collector.py
# Runs pipeline, exits when done
```

The `--rm` flag removes the container after it exits (no leftover containers).

## Key Docker Concepts for Interviews

### Image vs Container

| Image | Container |
|-------|-----------|
| Blueprint/template | Running instance |
| Read-only layers | Read-write layer on top |
| Shareable (Docker Hub) | Ephemeral (created/destroyed) |
| `docker build` creates | `docker run` creates |

### Why `python:3.9-slim`?

| Variant | Size | Use Case |
|---------|------|----------|
| `python:3.9` | ~900MB | Full Debian, all build tools |
| `python:3.9-slim` | ~150MB | Minimal Debian, most packages work |
| `python:3.9-alpine` | ~50MB | Alpine Linux, some packages break |

`slim` is the sweet spot: small enough for fast builds, compatible enough that `psycopg2-binary` and other C-extension packages work without extra build tools.

### Environment Variables in Docker

```bash
# Single variable
docker run -e GOOGLE_KEY=abc123 ...

# From file
docker run --env-file .env ...

# In GitHub Actions
docker run -e GOOGLE_KEY=${{ secrets.GOOGLE_KEY }} ...
```

Environment variables are the standard way to pass secrets to containers. They exist only in the container's process space, not in the image.

## Docker in GitHub Actions

The CI pipeline uses **Docker BuildX** with GitHub Actions cache:

```yaml
- uses: docker/setup-buildx-action@v3    # Enable BuildX
- uses: docker/build-push-action@v5
  with:
    context: .
    load: true                            # Load into local Docker
    tags: newsletter:latest
    cache-from: type=gha                  # Pull cache from GHA
    cache-to: type=gha,mode=max           # Push ALL layers to cache
```

**BuildX** is Docker's extended build system with features like:
- Multi-platform builds (ARM, x86)
- Advanced caching backends (GitHub Actions, S3, registry)
- Parallel stage building

## `.dockerignore`

```
venv/
__pycache__/
.env
*.pyc
.git/
```

Prevents large/sensitive directories from being copied into the build context. Without this, `COPY . .` would include the entire `venv/` directory.

## Related Notes
- [[CI-CD Pipeline]] - How Docker is used in automation
- [[GitHub Actions]] - The CI platform
