FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc g++ build-essential cmake git wget unzip && \
    apt-get clean

# Preinstall Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Optional: re-copy source if you want to bundle agent code directly
# COPY . /app

# Start in interactive mode (or override in compose)
CMD ["/bin/bash"]