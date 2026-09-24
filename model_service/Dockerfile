FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

WORKDIR /app

# Install system dependencies required by OpenCV, PyTorch, and YOLO
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    libsm6 \
    libxext6 \
    libxcb1 \
    libx11-6 \
    && rm -rf /var/lib/apt/lists/*

# Pre-install CPU-only PyTorch and headless OpenCV to optimize build size
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir opencv-python-headless>=4.10.0

# Install remaining Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy models, source code, and configuration
COPY models/ ./models/
COPY src/ ./src/
COPY config.yaml .
COPY main.py .

EXPOSE 8080

# Run uvicorn on Cloud Run's dynamic $PORT
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
