#!/bin/bash

IMAGE_NAME="msi-pipeline-dashboard"
CONTAINER_NAME="msi-pipeline-dashboard"

echo "Building Docker image..."
docker build -t $IMAGE_NAME .

echo "Stopping old container (if exists)..."
docker stop $CONTAINER_NAME 2>/dev/null
docker rm $CONTAINER_NAME 2>/dev/null

echo "Preparing directories..."
mkdir -p jobs logs
chown $USER:$USER jobs logs

echo "Starting container..."
docker run -d \
  --name $CONTAINER_NAME \
  --user $(id -u):$(id -g) \
  -p 8050:8050 \
  -v $(pwd):/app \
  -v $(pwd)/data:/data \
  -v $(pwd)/jobs:/jobs \
  -v $(pwd)/logs:/logs \
  $IMAGE_NAME

echo "App started"
