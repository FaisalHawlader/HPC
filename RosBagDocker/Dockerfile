# Use the official ROS base image
FROM ros:noetic-perception

# Install additional packages
RUN apt-get update && \
    apt-get install -y python3-pip python3-dev && \
    apt-get install -y python3-rosbag && \
    pip install ipython && \
    pip install ipykernel && \
    pip install matplotlib && \
    pip install pandas && \
    pip install seaborn && \
    pip install Pillow

# Set up the entry point
CMD ["bash"]