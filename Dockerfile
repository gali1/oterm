# Use the official Python image from Docker Hub
FROM python:3.10.13

# Faster Resolver
RUN python3 -m pip install uv -U --user --force-reinstall --break-system-packages;

# Set environment variables
ENV PIP_CACHE_DIR="/root/.cache/pip"

# Install system dependencies
RUN apt-get update \
    && apt-get install -y \
    # Add any other system dependencies here if needed
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment and set it as the working directory
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy the project files into the Docker image
COPY . /oterm
WORKDIR /oterm

# Faster Resolver
RUN pip install uv -U

# Install Python dependencies
RUN uv pip install --system --upgrade pip \
    && uv pip install --system -r requirements.txt

# Copy metadata and package data
RUN cp -r ../oterm /usr/local/lib/python3.10/site-packages/
RUN cp -r .oterm-0.4.0.dist-info /usr/local/lib/python3.10/site-packages/oterm-0.4.0.dist-info

# Copy executable file:
RUN cp .usr/local/bin/oterm /usr/local/bin/

# Optional: OLLAMA
# RUN curl https://ollama.ai/install.sh | sh
# RUN export OLLAMA_HOST=0.0.0.0:11434
# RUN ollama serve > /dev/null 2>&1 >output.log 2>&1 &

# Optional: Run any post-installation tasks
RUN chmod +x /usr/local/bin/oterm  # Uncomment if needed

# Set the command to run when the container starts
# CMD ["python", "/usr/local/bin/oterm"]

# Optional: Specify environment variables or additional configuration
# ENV KEY=VALUE
# EXPOSE 8000
