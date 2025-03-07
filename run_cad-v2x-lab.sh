#!/bin/bash

# Check if Docker daemon is running
if ! sudo systemctl is-active docker &> /dev/null; then
    echo "Docker daemon is not running. Starting Docker..."
fi

# Wait for Docker daemon to be fully started
WAIT_TIME=60  # Max wait time in seconds
WAIT_INTERVAL=1  # Interval for checking in seconds
elapsed_time=0

while ! sudo docker info &> /dev/null; do
    if [ "$elapsed_time" -ge "$WAIT_TIME" ]; then
        echo "Docker daemon did not start within $WAIT_TIME seconds. Exiting..."
        exit 1
    fi

    echo "Waiting for Docker daemon to start..."
    sleep "$WAIT_INTERVAL"
    elapsed_time=$((elapsed_time + WAIT_INTERVAL))
done

# Run the Docker command
docker run --rm -it \
    -v "$HOME/.ssh:/root/.ssh" \
    -v "$(pwd)":/host \
    --workdir /host \
    python:3.10.9 python iris_singularity_tools.py attach-vscode \
    --job-name cad-v2x-lab\
    --cpus 7 \
    --gpus 0 \
    --singularity-arg "--bind /home/users/fahawlader" \
    --singularity-image "/home/users/fahawlader/cad-v2x-lab.sif" \
    --time 10:00:00 \
    --mem 16GB

