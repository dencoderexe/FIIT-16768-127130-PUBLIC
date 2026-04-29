#!/bin/bash

IMAGE_NAME="msi-pipeline-dashboard"
CONTAINER_NAME="msi-pipeline-dashboard"

# Enter your directories here
DATA_DIR="$(pwd)/data"
JOBS_DIR="$(pwd)/jobs"
LOGS_DIR="$(pwd)/logs"

echo "Building Docker image..."
docker build -t "$IMAGE_NAME" .

echo "Stopping old container (if exists)..."
docker stop "$CONTAINER_NAME" 2>/dev/null
docker rm "$CONTAINER_NAME" 2>/dev/null

echo "Preparing directories..."
mkdir -p "$DATA_DIR" "$JOBS_DIR" "$LOGS_DIR"
chown "$USER:$USER" "$DATA_DIR" "$JOBS_DIR" "$LOGS_DIR"

echo "Starting container..."
docker run -d \
  --name "$CONTAINER_NAME" \
  --user "$(id -u):$(id -g)" \
  -p 8050:8050 \
  -v "$(pwd):/app" \
  -v "$DATA_DIR:/data" \
  -v "$JOBS_DIR:/jobs" \
  -v "$LOGS_DIR:/logs" \
  "$IMAGE_NAME"

echo "App started at http://localhost:8050"

echo "Exporting image..."
docker save -o "$IMAGE_NAME".tar "$IMAGE_NAME"