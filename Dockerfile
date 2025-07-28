# Use a specific, stable Python version on the required architecture
FROM --platform=linux/amd64 python:3.10-slim-bullseye

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies using pre-compiled wheels for speed and reliability
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code (including the trained model)
COPY src/ ./src/
COPY models/ ./models/
COPY main.py .

# Command to run when the container starts
# The script reads from /app/input and writes to /app/output,
# which will be mounted by the judging system.
CMD ["python", "main.py"]