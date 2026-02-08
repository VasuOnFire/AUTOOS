# Multi-stage Dockerfile for AUTOOS services

FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Create logs directory
RUN mkdir -p /app/logs

# API Service
FROM base as api
EXPOSE 8000
CMD ["uvicorn", "autoos.intent.api:app", "--host", "0.0.0.0", "--port", "8000"]

# Orchestrator Service
FROM base as orchestrator
CMD ["python", "-m", "autoos.orchestration.orchestrator_service"]

# Agent Worker Service
FROM base as agent-worker
# Install Docker CLI for tool execution
RUN apt-get update && apt-get install -y docker.io && rm -rf /var/lib/apt/lists/*
CMD ["python", "-m", "autoos.execution.agent_worker_service"]
