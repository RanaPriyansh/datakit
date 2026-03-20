# Multi-stage build for datakit
FROM python:3.12-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY pyproject.toml requirements.txt ./
RUN pip install --user --upgrade pip && \
    pip install --user ".[dev]"

# Final stage
FROM python:3.12-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy source code
COPY src/ ./src/
COPY pyproject.toml README.md ./
COPY tests/ ./tests/

# Create non-root user
RUN useradd -m -u 1000 datakit && chown -R datakit:datakit /app
USER datakit

# Expose for potential API usage (if we add server later)
EXPOSE 8000

# Default command (interactive)
ENTRYPOINT ["datakit"]
CMD ["--help"]
