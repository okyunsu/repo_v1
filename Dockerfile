# Backend-only monolithic application
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    supervisor \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy and install Python dependencies for all services
COPY financeservice/requirements.txt /app/financeservice/requirements.txt
COPY ratioservice/requirements.txt /app/ratioservice/requirements.txt
COPY esgservice/requirements.txt /app/esgservice/requirements.txt
COPY stockservice/requirements.txt /app/stockservice/requirements.txt
COPY gateway/requirements.txt /app/gateway/requirements.txt
COPY news-service/requirements.txt /app/news-service/requirements.txt
COPY pdfservice/requirements.txt /app/pdfservice/requirements.txt

# Install all Python dependencies
RUN pip install --no-cache-dir -r financeservice/requirements.txt \
    && pip install --no-cache-dir -r ratioservice/requirements.txt \
    && pip install --no-cache-dir -r esgservice/requirements.txt \
    && pip install --no-cache-dir -r stockservice/requirements.txt \
    && pip install --no-cache-dir -r gateway/requirements.txt \
    && pip install --no-cache-dir -r news-service/requirements.txt \
    && pip install --no-cache-dir -r pdfservice/requirements.txt

# Copy all service code
COPY financeservice/ /app/financeservice/
COPY ratioservice/ /app/ratioservice/
COPY esgservice/ /app/esgservice/
COPY stockservice/ /app/stockservice/
COPY gateway/ /app/gateway/
COPY news-service/ /app/news-service/
COPY pdfservice/ /app/pdfservice/

# Copy supervisor configuration
COPY k8s/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create startup script
COPY k8s/start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Expose backend service ports
EXPOSE 8000 8001 8002 8003 8004 8005 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Start all services
CMD ["/app/start.sh"] 