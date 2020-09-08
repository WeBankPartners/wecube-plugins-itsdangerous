FROM python:3.6-slim
LABEL maintainer = "Webank CTB Team"
# Install logrotate
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list
RUN sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list
RUN apt update && apt -y install --no-install-recommends logrotate
# Copy logrotate configuration
COPY build/logrotate.d/itsdangerous /etc/logrotate.d/
RUN service cron start
ADD requirements.txt /tmp/requirements.txt
ADD dist/* /tmp/
# Install && Clean up
RUN apt-get -y install gcc python3-dev && \
    pip3 install -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com -r /tmp/requirements.txt && \
    pip3 install /tmp/*.whl && \
    find /usr/local/lib/python3.6 -name '*.pyc' -delete && \
    rm -rf /root/.cache && apt autoclean && \
    rm -rf /tmp/* /var/lib/apt/* /var/cache/* && \
    apt purge -y `cat /var/log/apt/history.log|grep 'Install: '|tail -1| sed 's/Install://'| sed 's/\ /\n/g' | sed '/(/d' | sed '/)/d' | sed ':l;N;s/\n/ /;b l'`
# Use app:app to run gunicorn
RUN mkdir -p /etc/itsdangerous/
RUN mkdir -p /var/log/itsdangerous/
ADD etc/* /etc/itsdangerous/
# RUN adduser --disabled-password app
# RUN chown -R app:app /etc/itsdangerous/
# RUN chown -R app:app /var/log/itsdangerous/
# USER app
CMD ["/usr/local/bin/gunicorn", "--config", "/etc/itsdangerous/gunicorn.py", "wecube_plugins_itsdangerous.server.wsgi_server:application"]