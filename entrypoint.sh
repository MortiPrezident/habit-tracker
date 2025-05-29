#!/usr/bin/env bash
set -e  # выходим при любой ошибке

echo "⏳ Прогоняем Alembic миграции..."
poetry run alembic upgrade head

echo "🚀 Запускаем supervisord..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.app.conf
