# Use the official Yolov base image
FROM ultralytics/ultralytics

# Install additional packages
RUN apt-get update && \
    pip install tqdm && \
    pip install ipython && \
    pip install ipykernel && \
    pip install matplotlib && \
    pip install pandas && \
    pip install seaborn && \
    pip install Pillow

# Create working directory
WORKDIR /usr/src/ultralytics

# Set up the entry point
CMD ["bash"]