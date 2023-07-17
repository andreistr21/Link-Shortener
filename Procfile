web: gunicorn --chdir ./src shorty.wsgi
worker: sh -c 'cd ./src/ && exec celery -A shorty worker -l info'