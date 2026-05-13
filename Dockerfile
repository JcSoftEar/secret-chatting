FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir eventlet

COPY . .

RUN mkdir -p /app/instance && chmod 777 /app/instance

EXPOSE 5000

CMD ["python", "app.py"]
