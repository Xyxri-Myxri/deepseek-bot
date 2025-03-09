FROM python:3.12-slim

ENV PYTHONPATH=/app

RUN pip install uv

WORKDIR /app
COPY pyproject.toml ./
RUN uv pip install --requirements pyproject.toml --system
COPY . ./

CMD ["sh", "-c", "alembic upgrade head && python bot/main.py"]