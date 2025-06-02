FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    gcc \
    g++ \
    git \
    vim \
    python3-dev \
    build-essential \
    procps \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY search /app/search
RUN pip install -r search/requirements.txt
RUN python -m nltk.downloader punkt averaged_perceptron_tagger stopwords