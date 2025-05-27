#!/bin/bash

NAME="search-server"
NUM_WORKERS=${GUNICORN_WORKERS:-5}
NUM_THREADS=${GUNICRON_THREADS:-10}
HOST="127.0.0.1"
PORT="8080"

MAX_REQUESTS=${GUNICORN_MAX_REQUESTS:-1000}
MAX_REQUESTS_JITTER=${GUNICORN_MAX_REQUESTS_JITTER:-30}
FASTAPI_APP="server:app"

init_fastapi_server() {
    PYTHONPATH=. gunicorn $FASTAPI_APP \
        --bind ${HOST}:${PORT} \
        --name $NAME \
        --workers $NUM_WORKERS \
        --threads $NUM_THREADS \
        --timeout 600 \
        --max-requests $MAX_REQUESTS \
        --max-requests-jitter $MAX_REQUESTS_JITTER \
        --worker-class uvicorn.workers.UvicornWorker 2>&1
}


init_backend() {
    pkill -9 -f 'celery'
    pkill -9 -f 'gunicorn'
    echo "Bringing up celery workers...."
    celery -A celery_app worker --loglevel=INFO >/dev/null 2>&1 &
    echo "Starting configured FastAPI server..."
    init_fastapi_server
}   

init_backend