# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create a directory for the database (for volume mounting)
RUN mkdir -p /app/data

# Expose port 8000
EXPOSE 8000

# Define environment variable for the database URL (default to volume path)
# Users can override this, but this sets a sensible default to use the /app/data volume
ENV DATABASE_URL="sqlite:////app/data/alerting.db"

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
