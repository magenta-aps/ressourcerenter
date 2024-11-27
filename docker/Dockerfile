FROM python:3.10
ENV SUPERCRONIC_URL=https://github.com/aptible/supercronic/releases/download/v0.1.12/supercronic-linux-amd64 \
    SUPERCRONIC=supercronic-linux-amd64 \
    SUPERCRONIC_SHA1SUM=048b95b48b708983effb2e5c935a1ef8483d9e3e\
    PYTHONUNBUFFERED=1
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN mkdir /app &&  \
    mkdir -p /srv/media &&  \
    mkdir -p /var/cache/aalisakkat && \
    #gid/uid from salt
    groupadd -g 75090 -r ressourcerenter && \
    groupadd -g 75100 -r certificate_exporter && \
    useradd -u 75090 --no-log-init -r -g ressourcerenter -G certificate_exporter ressourcerenter && \
    chown ressourcerenter:ressourcerenter /srv/media && \
    chown ressourcerenter:ressourcerenter /var/cache/aalisakkat && chmod a+w /var/cache/aalisakkat

# hadolint ignore=DL3008
RUN sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt bookworm-pgdg main" > /etc/apt/sources.list.d/pgdg.list' && \
    curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        gettext libxmlsec1-dev xmlsec1 default-jre graphviz postgresql-client-common postgresql-client-16 && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# supercronic
RUN curl -fsSLO "$SUPERCRONIC_URL" && \
    echo "${SUPERCRONIC_SHA1SUM}  ${SUPERCRONIC}" | sha1sum -c - && \
    chmod +x "$SUPERCRONIC" && \
    mv "$SUPERCRONIC" "/usr/local/bin/${SUPERCRONIC}" && \
    ln -s "/usr/local/bin/${SUPERCRONIC}" /usr/local/bin/supercronic

# schemaspy
RUN curl -fsSL --output /usr/local/share/schemaspy.jar https://github.com/schemaspy/schemaspy/releases/download/v6.1.0/schemaspy-6.1.0.jar && \
    curl -fsSL --output /usr/local/share/postgresql.jar https://jdbc.postgresql.org/download/postgresql-42.2.8.jar

ARG COMMIT_TAG
ENV COMMIT_TAG=${COMMIT_TAG:-HEAD}

COPY ressourcerenter/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY docker/crontab /crontab
COPY ./docker/entrypoint.sh /entrypoint.sh
COPY ./ressourcerenter /app
# COPY ./manual.md /manual.md
WORKDIR /app
RUN django-admin compilemessages
USER ressourcerenter
VOLUME /srv/media
VOLUME /var/cache/aalisakkat
EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "--bind=0.0.0.0:8000", "project.wsgi:application", "--workers=4", "--timeout=120","--error-logfile=-", "--access-logfile=-", "--capture-output"]
