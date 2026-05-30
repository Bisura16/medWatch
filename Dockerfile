FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY api/requirements.txt /app/api/requirements.txt
RUN pip install --no-cache-dir -r /app/api/requirements.txt

RUN apt-get purge -y --auto-remove build-essential && rm -rf /var/lib/apt/lists/*

COPY . /app

ENV PYTHONUNBUFFERED=1
ENV USE_CLOUD_STORAGE=true
ENV PORT=8080
# Bake the multi-source SQLite catalog into the image so the web backend
# serves the full enriched drug database (openFDA + RxNorm + DailyMed)
# instead of falling back to the small JSON catalog.
ENV MEDWATCH_DB_PATH=/app/anggota1/Hasil-Scrap/drugs.db

EXPOSE 8080

WORKDIR /app
CMD ["gunicorn", "--bind", ":8080", "--workers", "2", "--threads", "4", "--timeout", "120", "api.app:app"]
