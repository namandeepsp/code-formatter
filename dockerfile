# Use official Python image as base
FROM python:3.12-slim

# Install Go, Java, and other dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    golang-go \
    default-jdk \
    default-jre \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set Go environment variables
ENV PATH=$PATH:/usr/local/go/bin
ENV GOPATH=/go
ENV PATH=$PATH:$GOPATH/bin

# Create Go workspace
RUN mkdir -p /go/bin

# Set working directory
WORKDIR /app

# Set Python environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Download Google Java Format
RUN curl -L https://github.com/google/google-java-format/releases/download/v1.17.0/google-java-format-1.17.0-all-deps.jar -o /app/google-java-format.jar

# Copy project files
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]