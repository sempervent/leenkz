# Multi-stage build for Leenkz
# Stage 1: Build React frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (use npm install if package-lock.json doesn't exist)
RUN if [ -f package-lock.json ]; then \
        npm ci --only=production; \
    else \
        npm install --only=production; \
    fi

# Copy source code
COPY . .

# Build the React app
RUN npm run build

# Stage 2: Python backend
FROM python:3.12-slim AS backend

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Install uv
RUN pip install uv

# Copy pyproject.toml and README.md
COPY pyproject.toml README.md ./

# Install Python dependencies (use --system to avoid venv issues in Docker)
RUN uv pip install --system .

# Copy source code
COPY leenkz/ ./leenkz/

# Copy built frontend from stage 1
COPY --from=frontend-builder /app/dist ./static

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health')" || exit 1

# Run the application
CMD ["uv", "run", "leenkz", "start", "--host", "0.0.0.0", "--port", "8000"] 