# Use a base image with Python pre-installed
FROM python:3.10-slim

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Install any needed packages
RUN apt-get update && \
    rm -rf /var/lib/apt/lists/*

# Copy the project files into the Docker image
COPY . /oterm
WORKDIR /oterm

# Install 'uv' package globally
RUN pip install uv

# Copy metadata and package data
RUN cp -r ../oterm /usr/local/lib/python3.10/site-packages/
RUN cp -r .oterm-0.4.0.dist-info /usr/local/lib/python3.10/site-packages/oterm-0.4.0.dist-info

# Copy executable file:
RUN cp .usr/local/bin/oterm /usr/local/bin/

# Use 'uv' to install packages from requirements.txt globally
RUN uv pip install --system -r requirements.txt

# Make the oterm executable and run it
RUN chmod +x /usr/local/bin/oterm

ENTRYPOINT ["/usr/local/bin/oterm"]
