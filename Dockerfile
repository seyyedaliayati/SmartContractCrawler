# Use official Python image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Install dependencies
COPY ./requirements.txt /app/
RUN apt-get update && apt-get install -y cron && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app/

# Add cron job
COPY crontab /etc/cron.d/my-cron-job
RUN chmod 0644 /etc/cron.d/my-cron-job && \
    crontab /etc/cron.d/my-cron-job && \
    touch /var/log/cron.log

# Expose port
EXPOSE 8000

# Run both cron and Gunicorn
CMD ["sh", "-c", "cron && gunicorn -w 4 -b 0.0.0.0:8000 web_server:app"]
