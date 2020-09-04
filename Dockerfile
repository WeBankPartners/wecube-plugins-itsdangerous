FROM python:3.6-slim
LABEL maintainer = "Webank CTB Team"
# Install logrotate
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list
RUN sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list
RUN apt-get update && apt-get -y install logrotate
RUN apt-get -y install gcc python3-dev
# Copy logrotate configuration
COPY build/logrotate.d/itsdangerous /etc/logrotate.d/
RUN service cron start
RUN adduser --disabled-password app
ADD requirements.txt /tmp/requirements.txt
RUN pip3 install -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com -r /tmp/requirements.txt
ADD dist/* /tmp/
RUN cd /tmp && pip3 install *.whl
# Use app:app to run gunicorn
RUN mkdir -p /etc/itsdangerous/
RUN mkdir -p /var/log/itsdangerous/
ADD etc/* /etc/itsdangerous/
RUN chown -R app:app /etc/itsdangerous/
RUN chown -R app:app /var/log/itsdangerous/
USER app
CMD ["/usr/local/bin/gunicorn", "--config", "/etc/itsdangerous/gunicorn.py", "wecube_plugins_itsdangerous.server.wsgi_server:application"]