FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 120 --retries 5 -r requirements.txt

COPY app.py library.db ./
COPY templates ./templates

EXPOSE 12345

CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:12345", "app:app"]