FROM python:3.12-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy the requirements file into the container
# We only have one dependency, Flask, so we can install it directly
# For a larger project, you would copy a requirements.txt file here

# 4. Install Flask (using a more recent version for compatibility)
RUN pip install Flask==2.3.3

# 5. Copy the application code into the container
COPY app/app.py .

# 6. Set the default version as an environment variable
# This can be overridden at runtime by the CI/CD pipeline
ENV APP_VERSION=1.3

# 7. Expose the port the app runs on
EXPOSE 8080

# 8. Define the command to run the application
CMD ["python", "app.py"]