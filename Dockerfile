FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend dependencies first (caching layer)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Set environment variables
ENV FLASK_APP=backend/app.py
ENV PYTHONUNBUFFERED=1
# Override these at runtime:
# SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_KEY
# TURSO_URL, TURSO_TOKEN
# SENDER_EMAIL, SENDER_PASSWORD
# SECRET_KEY

EXPOSE 5001

CMD ["gunicorn", "backend.app:app", "-w", "4", "-b", "0.0.0.0:5001"]
