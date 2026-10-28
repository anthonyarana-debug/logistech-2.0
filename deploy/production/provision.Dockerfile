FROM postgres:17.11-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends openssl ca-certificates && rm -rf /var/lib/apt/lists/*
COPY deploy/production/provision-secrets.sh /usr/local/bin/provision-secrets
ENTRYPOINT ["bash", "/usr/local/bin/provision-secrets"]
