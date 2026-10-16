# Dockerfile for Hugging Face Spaces (CPU Basic, 16 GB RAM)
FROM python:3.10-slim

# System dependencies for audio (libsndfile, ffmpeg) and OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    ffmpeg \
    libsndfile1 \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Hugging Face Spaces runs as user 1000 by default
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PORT=7860

WORKDIR /app

# Install Python dependencies with CPU-optimized PyTorch
COPY --chown=user requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY --chown=user . /app/

# Expose standard Hugging Face Spaces port
EXPOSE 7860

# Launch FastAPI app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]

