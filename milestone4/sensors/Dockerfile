
FROM python:3.9-slim

WORKDIR /app

COPY ../requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ../proto ./proto
COPY ../sensors /app/sensors

EXPOSE 60321

CMD ["python", "sensors/runner.py"]