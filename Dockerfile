# === Stage 1: build dependencies into wheels (keeps final image slim & fast to install)
FROM python:3.12-slim AS builder
WORKDIR /app
# Don’t write .pyc files; unbuffer Python output (clearer logs)
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
# Minimal build tools for any packages that need compiling (none right now, but safe)
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*
# Pin app deps
COPY requirements.txt .
# Upgrade pip and build .whl files for everything to speed up install in the runtime layer
RUN python -m pip install --upgrade pip && pip wheel --no-cache-dir --no-deps -r requirements.txt -w /wheels

# === Stage 2: runtime image (no compilers, just Python + my app)
FROM python:3.12-slim
WORKDIR /app
# Runtime env:
# - no .pyc files
# - unbuffered logs
# - point Flask to my app module
# - bind on all interfaces inside the container
# - set container port (can still remap with -p host:container at run)
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    FLASK_APP=src/web_app.py \
    FLASK_RUN_HOST=0.0.0.0 \
    FLASK_RUN_PORT=7774

# Install wheels built in the builder stage (fast, no extra build deps here)
COPY --from=builder /wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy my application code
COPY src/ ./src/

# Document the container port (purely informational for Docker)
EXPOSE 7774

# Healthcheck without adding curl: use Python stdlib to hit /data and expect 200
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD ["python","-c","import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:7774/data').status==200 else 1)"]

# Start Flask via the CLI so FLASK_* env vars are respected
CMD ["python", "-m", "flask", "run"]
