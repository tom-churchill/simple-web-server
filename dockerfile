# Use Python 3.6 to match the original development environment
FROM python:3.6-slim

# Set working directory
WORKDIR /app

# Install build dependencies and git
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev git && \
    rm -rf /var/lib/apt/lists/*

# Install requests-async from GitHub FIRST (before other deps that need it)
# Version 0.5.0 was never released to PyPI but Sanic 19.6.3 requires it
RUN pip install --no-cache-dir git+https://github.com/encode/requests-async.git@0.5.0 2>/dev/null || \
    pip install --no-cache-dir git+https://github.com/encode/requests-async.git

# Copy requirements first for better caching
COPY requirements.txt .

# Install all other dependencies (requests-async is already installed)
RUN grep -v "requests-async" requirements.txt > requirements_temp.txt && \
    pip install --no-cache-dir -r requirements_temp.txt && \
    rm requirements_temp.txt

# Copy the entire application
COPY . .

# Install the package
RUN pip install --no-cache-dir -e .

# Expose default port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Create a volume for serving files
VOLUME ["/data"]

# Change working directory to /data for serving files
WORKDIR /data

# Default command - can be overridden
CMD ["python", "-m", "simplewebserver", "--bind", "0.0.0.0", "--port", "8000"]