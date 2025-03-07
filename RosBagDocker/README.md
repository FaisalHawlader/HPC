# Build the docker image
docker build -t processingrosbag .

# Run the docker image
docker run -it --name rosbagprocessing processingrosbag

# List all the docker containers
docker ps -a

# remove a stopped container
docker rm rosbagprocessing

# send the container to HPC as a singularity image (using iris_singularity_tools.py)
python3 iris_singularity_tools.py docker-convert --tag processingrosbag  --sif-path /work/projects/360lab/cv2x_vnc2024/docker/rosbagprocessing.sif

# Attach VSCode and  and run the container (using the script run_iris_singularity_data_preparation.sh)
./run_iris_singularity_data_preparation.sh


