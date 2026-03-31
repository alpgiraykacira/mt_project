FROM python:3.11-slim

WORKDIR /app

# Önce requirements — bu katman cache'lenir, her build'de tekrar kurulmaz
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodunu kopyala
COPY . .

# OpenShift güvenlik politikası: container root olarak çalışamaz
RUN useradd -r -u 1001 appuser && chown -R appuser:appuser /app
USER 1001

EXPOSE 8080

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "120", "--preload"]
