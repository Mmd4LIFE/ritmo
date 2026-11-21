FROM python:3.12-slim

WORKDIR /app

COPY apps/api/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY apps/api /app/api
COPY apps/worker /app/worker

ENV PYTHONPATH=/app/api
CMD ["python", "/app/worker/main.py"]
