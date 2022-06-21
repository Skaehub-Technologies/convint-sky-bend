release: python manage.py migrate

web: gunicorn core.wsgi.py --log-file -
