FROM python:3.8-slim-buster
LABEL maintainer = "Webank CTB Team"
# Install logrotate
RUN sed -i 's/deb.debian.org/mirrors.tencentyun.com/g' /etc/apt/sources.list
RUN sed -i 's/security.debian.org/mirrors.tencentyun.com/g' /etc/apt/sources.list
# RUN apt update && apt -y install --no-install-recommends logrotate
# Copy logrotate configuration
# COPY build/logrotate.d/itsdangerous /etc/logrotate.d/
# RUN service cron start
COPY requirements.txt /tmp/requirements.txt
COPY dist/* /tmp/
# Install && Clean up
RUN apt update && apt-get -y install gcc python3-dev swig libssl-dev && \
    pip3 install -i http://mirrors.tencentyun.com/pypi/simple/ --trusted-host mirrors.tencentyun.com -r /tmp/requirements.txt && \
    pip3 install /tmp/*.whl && \
    rm -rf /root/.cache && apt autoclean && \
    rm -rf /tmp/* /var/lib/apt/* /var/cache/* && \
    apt purge -y `cat /var/log/apt/history.log|grep 'Install: '|tail -1| sed 's/Install://'| sed 's/\ /\n/g' | sed '/(/d' | sed '/)/d' | sed ':l;N;s/\n/ /;b l'`
# Use app:app to run gunicorn
RUN mkdir -p /etc/itsdangerous/
RUN mkdir -p /var/log/itsdangerous/
RUN mkdir -p /tmp/artifacts/
COPY etc /etc/itsdangerous
# RUN adduser --disabled-password app
# RUN chown -R app:app /etc/itsdangerous/
# RUN chown -R app:app /var/log/itsdangerous/
# USER app
COPY build/start_all.sh /scripts/start_all.sh
RUN chmod +x /scripts/start_all.sh
CMD ["/bin/sh","-c","/scripts/start_all.sh"]