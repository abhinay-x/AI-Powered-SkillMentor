FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt')"

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PORT=8080

# Initialize data directory
RUN mkdir -p data/processed

# Expose the application port
EXPOSE 8080

# Run the application with Gunicorn
CMD gunicorn --bind 0.0.0.0:8080 --workers 3 app:app 