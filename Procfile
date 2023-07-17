web: gunicorn --chdir ./src shorty.wsgi
worker: celery -A shorty worker -l info