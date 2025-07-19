# Use Alpine-based Python image for better security and smaller size
FROM python:3.12-alpine

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies for building Python packages
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev

# Remove any system-installed urllib3 packages that might conflict
RUN apk del py3-urllib3 2>/dev/null || true

# Install Python dependencies with security patch
# Pin urllib3 to ensure we get the secure version
RUN pip install --no-cache-dir \
    Flask==2.3.3 \
    kubernetes==28.1.0 \
    urllib3==2.5.0

# Copy the application code into the container
COPY app/app.py .

# Create a non-root user for better security
RUN addgroup -g 1001 -S appgroup && \
    adduser -S appuser -u 1001 -G appgroup

# Change ownership of the app directory to the app user
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Set a default version that will be overridden by the CI/CD pipeline
ENV APP_VERSION=dev

# Expose the port the app runs on
EXPOSE 8080

# Define the command to run the application
CMD ["python", "app.py"]