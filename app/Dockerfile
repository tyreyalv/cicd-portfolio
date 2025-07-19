# Use Alpine-based Python image for better security and smaller size
FROM python:3.12-alpine

# Set the working directory inside the container
WORKDIR /app

# Install Flask (using a more recent version for compatibility)
# Alpine uses apk for package management, but pip still works for Python packages
RUN pip install --no-cache-dir Flask==2.3.3

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
# The Helm chart sets APP_VERSION via deployment.yaml env vars
ENV APP_VERSION=dev

# Expose the port the app runs on
EXPOSE 8080

# Define the command to run the application
CMD ["python", "app.py"]