FROM python:3.8
ENV SUPERCRONIC_URL=https://github.com/aptible/supercronic/releases/download/v0.1.12/supercronic-linux-amd64 \
    SUPERCRONIC=supercronic-linux-amd64 \
    SUPERCRONIC_SHA1SUM=048b95b48b708983effb2e5c935a1ef8483d9e3e\
    PYTHONUNBUFFERED=1
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN mkdir /app && mkdir -p /srv/media && mkdir -p /var/cache/aalisakkat && \
#gid/uid from salt
groupadd -g 75090 -r ressourcerenter && \
groupadd -g 75100 -r certificate_exporter && \
useradd -u 75090 --no-log-init -r -g ressourcerenter -G certificate_exporter ressourcerenter && \
chown ressourcerenter:ressourcerenter /srv/media && \
chown ressourcerenter:ressourcerenter /var/cache/aalisakkat && chmod a+w /var/cache/aalisakkat
# hadolint ignore=DL3008
RUN apt-get update && \
    apt-get install -y --no-install-recommends gettext pandoc libxmlsec1-dev xmlsec1 default-jre graphviz && \
    apt-get clean && rm -rf /var/lib/apt/lists/* \
    && wget --progress=dot:giga "$SUPERCRONIC_URL" \
    && echo "${SUPERCRONIC_SHA1SUM}  ${SUPERCRONIC}" | sha1sum -c - \
    && chmod +x "$SUPERCRONIC" \
    && mv "$SUPERCRONIC" "/usr/local/bin/${SUPERCRONIC}" \
    && ln -s "/usr/local/bin/${SUPERCRONIC}" /usr/local/bin/supercronic \
    && wget --progress=dot:giga https://github.com/schemaspy/schemaspy/releases/download/v6.1.0/schemaspy-6.1.0.jar -O /usr/local/share/schemaspy.jar \
    && wget --progress=dot:giga https://jdbc.postgresql.org/download/postgresql-42.2.8.jar -O /usr/local/share/postgresql.jar

COPY ressourcerenter/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY docker/crontab /crontab
COPY ./docker/entrypoint.sh /entrypoint.sh
COPY ./ressourcerenter /app
# COPY ./manual.md /manual.md
WORKDIR /app
USER ressourcerenter
VOLUME  /srv/media
VOLUME  /var/cache/aalisakkat
EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn","-b","0.0.0.0:8000","project.wsgi:application","-w 4","-t 120","--error-logfile","-","--capture-output"]
