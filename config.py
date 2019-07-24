import os

# pylama:ignore=C0103
bind = '127.0.0.1:8000'

workers = int(os.environ.get('GUNICORN_PROCESSES', '1'))

forwarded_allow_ips = '*'
secure_scheme_headers = {'X-Forwarded-Proto': 'https'}
