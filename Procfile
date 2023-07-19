web: bin/start-nginx gunicorn -c config/gunicorn.conf.py --chdir ./src shorty.wsgi
worker: sh -c 'cd ./src/ && exec celery -A shorty worker -l info'