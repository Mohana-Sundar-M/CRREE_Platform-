FROM python:3.11-slim

# Install system dependencies for some python packages if needed
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the Hugging Face model to the image to avoid runtime latency
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-MiniLM-L3-v2')"

COPY . .

EXPOSE 7860

# Production settings: ensure SQLite DB can be written if persisted in volume
VOLUME /app/data

CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
