FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y tesseract-ocr gcc g++ git vim python3-dev build-essential

WORKDIR /app
COPY search /app/search
COPY docker-compose.yml /app

RUN pip install -r search/requirements.txt
RUN cd search && bash start_server.sh
RUN docker compose up --build
EXPOSE 8080