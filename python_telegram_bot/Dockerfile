FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# uv is used by the project (see Makefile). We install it via pip for Docker builds.
RUN pip install --no-cache-dir uv

# Install dependencies from lockfile first (better layer caching)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# App sources
COPY src ./src

# Optional: keep default data files in the image; at runtime /app/data is usually mounted as a volume.
COPY data ./data

CMD ["uv", "run", "python", "src/main.py"]


