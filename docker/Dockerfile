FROM python:3.8
RUN mkdir /app && mkdir -p /srv/media && \
#gid/uid from salt
groupadd -g 75050 -r ressourcerenter && \
useradd -u 75050 --no-log-init -r -g ressourcerenter ressourcerenter && \
chown ressourcerenter:ressourcerenter /srv/media
COPY docker/pip-requirements.txt /app/pip-requirements.txt
COPY docker/sys-requirements.txt /app/sys-requirements.txt
RUN pip install --no-cache-dir -r /app/pip-requirements.txt
ENV PYTHONUNBUFFERED=1
# hadolint ignore=DL3008
RUN apt update && \
    grep -vE '^#' /app/sys-requirements.txt | xargs apt install -y --no-install-recommends && \
    apt clean && rm -rf /var/lib/apt/lists/*
USER ressourcerenter
COPY ./docker/entrypoint.sh /entrypoint.sh
COPY ./ressourcerenter /app
EXPOSE 8000
VOLUME  /srv/media
ENTRYPOINT ["/entrypoint.sh"]
WORKDIR /app
CMD ["gunicorn", "--bind=0.0.0.0:8000", "project.wsgi:application", "--workers=4", "--timeout 120", "--error-logfile -", "--capture-output"]
