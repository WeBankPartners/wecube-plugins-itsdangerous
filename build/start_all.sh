#!/bin/sh
nohup wecube_plugins_itsdangerous_scheduler > /dev/null 2>&1 &
/usr/local/bin/gunicorn --config /etc/itsdangerous/gunicorn.py wecube_plugins_itsdangerous.server.wsgi_server:application
