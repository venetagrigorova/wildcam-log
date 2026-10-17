FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# gunicorn is a proper production server (Flask's built-in one is for development only)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "app:app"]
