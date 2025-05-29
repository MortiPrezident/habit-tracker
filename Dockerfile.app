FROM python:3.10

RUN apt-get update && apt-get install -y supervisor \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root


COPY web/ /app/web
COPY .env /app/.env
COPY supervisord.app.conf /etc/supervisor/conf.d/supervisord.app.conf
COPY alembic/ /app/alembic
COPY alembic.ini /app/alembic.ini
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh


