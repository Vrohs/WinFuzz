FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install required packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY wzf.py .

# Create volume mount point for user files
VOLUME /data

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set entrypoint
ENTRYPOINT ["python", "wzf.py"]

# Default command (can be overridden)
CMD []
