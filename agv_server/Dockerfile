FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y curl

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY requirements.txt .

RUN uv pip install -r requirements.txt --system

COPY . .

EXPOSE 8000

# Make entry file executable
RUN chmod +x  ./entrypoint.sh

CMD ["./entrypoint.sh"]

