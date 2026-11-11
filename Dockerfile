FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application code
COPY orchestrator.py .
COPY api/ api/
COPY core/ core/
COPY data/ data/
COPY models/ models/
COPY parsers/ parsers/
COPY schemas/ schemas/
COPY services/ services/
COPY utils/ utils/
COPY validators/ validators/

# Uses $PORT env var (Render, Railway, Cloud Run), default to 8000
EXPOSE 8000

CMD ["sh", "-c", "uvicorn orchestrator:app --host 0.0.0.0 --port ${PORT:-8000}"]
