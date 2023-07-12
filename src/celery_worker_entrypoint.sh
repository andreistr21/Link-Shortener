#!/bin/sh

until cd /app/shorty
do
    echo "Waiting for server volume..."
done

celery -A shorty worker --loglevel=info --concurrency 1 -E
