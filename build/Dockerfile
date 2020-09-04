FROM python:3.6-slim
LABEL maintainer = "Webank CTB Team"
RUN pip install ../dist/*.whl
# Install logrotate
RUN apt-get update && apt-get -y install logrotate
# Copy logrotate configuration
COPY build/logrotate.d/itsdangerous /etc/logrotate.d/
RUN service cron start
RUN addgroup -S app && adduser -S -G app app
# Use app:app to run gunicorn
USER app
RUN mkdir -p /etc/itsdangerous
ADD ../etc/gunicorn /etc/itsdangerous/
ADD ../etc/locale /etc/itsdangerous/
CMD gunicorn --config /etc/cms/gunicorn.py wecube_plugins_itsdangerous.server.wsgi_server:application
