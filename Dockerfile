# Use the official Python image from Docker Hub
FROM python:3.10.13

# Set environment variables
ENV PIP_CACHE_DIR="/root/.cache/pip"

# Install system dependencies
RUN apt-get update \
    && apt-get install -y \
        uv \
        # Add any other system dependencies here if needed
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment and set it as the working directory
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy the project files into the Docker image
COPY . /app
WORKDIR /app

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install --editable .

# Optional: Run any post-installation tasks
# RUN chmod +x /usr/local/bin/oterm  # Uncomment if needed

# Set the command to run when the container starts
CMD ["python", "/usr/local/bin/oterm"]

# Optional: Specify environment variables or additional configuration
# ENV KEY=VALUE
# EXPOSE 8000
