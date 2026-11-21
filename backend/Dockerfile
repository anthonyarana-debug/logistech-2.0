FROM python:3.13.17-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && groupadd --gid 10001 app \
    && useradd --uid 10001 --gid app --no-create-home app
COPY --chown=app:app . .
USER app
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000", "--noreload"]

FROM runtime AS development
USER root
COPY requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt
USER app

FROM runtime AS production
USER root
RUN sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list.d/debian.sources \
    && apt-get -o Acquire::Retries=0 update \
    && apt-get -o Acquire::Retries=0 upgrade -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*
COPY requirements-production.txt ./
RUN pip install --no-cache-dir -r requirements-production.txt
RUN mkdir -p /app/staticfiles && chown 10001:10001 /app/staticfiles
# Runtime images are immutable: package installation tools and their vendored
# dependencies belong in build/test stages, not the Internet-facing process.
RUN python -m pip uninstall -y pip setuptools wheel
USER app
CMD ["gunicorn", "--config", "python:config.gunicorn", "config.wsgi:application"]
