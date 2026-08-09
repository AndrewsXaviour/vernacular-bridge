FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY orchestrator.py .
COPY models/ models/
COPY utils/ utils/
COPY validators/ validators/
COPY schemas/ schemas/
COPY data/ data/

# Railway uses $PORT env var, default to 8000
EXPOSE 8000

CMD ["sh", "-c", "uvicorn orchestrator:app --host 0.0.0.0 --port ${PORT:-8000}"]
