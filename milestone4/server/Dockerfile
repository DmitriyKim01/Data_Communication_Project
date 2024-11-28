
FROM python:3.9-slim

WORKDIR /app

COPY ../requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ../proto ./proto
COPY ../server /app/server

EXPOSE 50052

CMD ["python", "server/grpc_server.py"]