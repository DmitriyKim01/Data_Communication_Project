
FROM python:3.9-slim

WORKDIR /app

COPY ../requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ../proto ./proto
COPY ../operating_pc /app/operating_pc

EXPOSE 50899

CMD ["python", "operating_pc/runner.py"]