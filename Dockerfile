FROM node:20-slim

RUN apt-get update && apt-get install -y python3 python3-pip python3.11-venv python3-dev build-essential libssl-dev libffi-dev libxml2-dev libxslt1-dev zlib1g-dev

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
COPY start.sh /app/start.sh
COPY package.json /app/package.json
COPY package-lock.json /app/package-lock.json
COPY tsconfig.json /app/tsconfig.json
COPY tsconfig.app.json /app/tsconfig.app.json
COPY tsconfig.node.json /app/tsconfig.node.json
COPY vite.config.ts /app/vite.config.ts
COPY src /app/src
COPY tailwind.config.js /app/tailwind.config.js

COPY search /app/search
RUN python3 -m venv ~/.virtualenvs/search
COPY search /app/search
RUN python3 -m venv /root/.virtualenvs/search \
 && /root/.virtualenvs/search/bin/pip install --upgrade pip \
 && /root/.virtualenvs/search/bin/pip install -r search/requirements.txt \
 && /root/.virtualenvs/search/bin/python -m nltk.downloader \
      punkt averaged_perceptron_tagger stopwords
RUN npm install -g serve
RUN /bin/bash ./start.sh &