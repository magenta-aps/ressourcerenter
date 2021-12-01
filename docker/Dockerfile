FROM python:3.8
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN mkdir /app
#gid/uid from salt
#groupadd -g 75050 -r ressourcerenter && \
#useradd -u 75050 --no-log-init -r -g ressourcerenter ressourcerenter
COPY ressourcerenter/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
ENV PYTHONUNBUFFERED=1
# hadolint ignore=DL3008
RUN apt-get update && \
    apt-get install -y --no-install-recommends gettext && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
#USER ressourcerenter
COPY ./docker/entrypoint.sh /entrypoint.sh
COPY ./ressourcerenter /app
WORKDIR /app
RUN django-admin compilemessages
VOLUME  /srv/media
EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "--bind=0.0.0.0:8000", "project.wsgi:application", "--workers=4", "--timeout 120", "--error-logfile -", "--capture-output"]
