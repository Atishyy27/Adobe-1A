# syntax=docker/dockerfile:1
FROM --platform=linux/amd64 python:3.10-slim

# Set base working directory
WORKDIR /app

# Copy dependencies and install them
COPY Requirements.txt .
RUN pip install --no-cache-dir -r Requirements.txt

# Copy entire project into container
COPY . .

# Move to the directory where main.py exists
WORKDIR /app/Backend

# Run main.py
CMD ["python", "main.py"]
