from pathlib import Path
import time
import psutil
import argparse
from subprocess import Popen, PIPE, CalledProcessError
import json
import socket

from multiprocessing import Process, Value

def parse_cam_line(cam_line: str):
    cam = json.loads(cam_line)["cam"]
    generationDeltaTime = cam["generationDeltaTime"]
    pos = cam["camParameters"]["basicContainer"]["referencePosition"]
    lat, lon = pos["latitude"], pos["longitude"]
    return {"generationDeltaTime": generationDeltaTime, "latitude": lat, "longitude": lon}


class UDPSocket:
    def __init__(self, remote: str, remote_port: int, timeout_seconds: float):
        self.remote = remote
        self.remote_port = remote_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP Socket
        self.socket.settimeout(timeout_seconds)
        self.socket.connect((self.remote, self.remote_port))

    def send(self, data: bytes):
        return self.socket.send(data)

    def close(self):
        self.socket.close()


def continuously_update_gnss(shared_gnss_lat: Value, shared_gnss_long: Value, shared_gnss_generation_time: Value):
    # this runs in a parallel process to launch mwpubsub and update gnss coordinates
    # the main process will do networking measurements while reporting the latest gnss coordinates
    # This runs mwpubsub and parses its output to get lat/long, and update the shared memory variables so they hold the latest values
    process = "mwpubsub -m 32 -a 12345 -s"
    # process = "head -n1 measurements/cam_measurements_example.txt" # TODO for testing only, remove this and use mwpubsub
    # i = 0
    with Popen(process, stdout=PIPE, universal_newlines=True, shell=True) as p:
        for cam_line in p.stdout:
            # read cam message and fix timestamp overflow
            # cam = {"latitude": i, "longitude": i, "generationDeltaTime": i}; i+=1 # TODO remove this
            cam = parse_cam_line(cam_line)
            shared_gnss_lat.value = cam["latitude"]
            shared_gnss_long.value = cam["longitude"]
            shared_gnss_generation_time.value = cam["generationDeltaTime"]
            # print(f"set values to {shared_gnss_lat.value}, {shared_gnss_long.value}, {shared_gnss_generation_time.value}")
    if p.returncode != 0:
        raise CalledProcessError(p.returncode, p.args)
    return p

def measure_throughput(output_csv: Path, remote: str, remote_port: str, message_bytes: int):
    with output_csv.open("w") as output_file:
        output_file.write("gnss_generation_time,latitude,longitude,goodput\n") # Write output header
        shared_gnss_lat = Value("d", 0.0, lock=False)
        shared_gnss_long = Value("d", 0.0, lock=False)
        shared_gnss_generation_time = Value("i", 0, lock=False)
        continuously_update_gnss(shared_gnss_lat, shared_gnss_long, shared_gnss_generation_time)
        process = Process(target=continuously_update_gnss, args=(shared_gnss_lat, shared_gnss_long, shared_gnss_generation_time)) # Run the process that will update the gnss coordinates to the latest values

        # Continuously send data over socket, and measure throughput in sync with gnss coordinates
        # We make the assumption that the gnss coordinates are constant while sending a single chunk of data
        byte_array = bytearray(message_bytes)
        while True:
            try:
                sock = UDPSocket(remote, remote_port, timeout_seconds=2.0)
                while True:
                    t0 = time.time()
                    sock.send(byte_array)
                    t1 = time.time()
                    print(f"Sent {message_bytes} bytes in {t1 - t0} seconds")
                    goodput = message_bytes / (t1 - t0)
                    # gnss_generation_time,latitude,longitude,goodput
                    output_file.write(f"{shared_gnss_generation_time.value},{shared_gnss_lat.value},{shared_gnss_long.value},{goodput}\n")
                    print(f"{shared_gnss_generation_time.value},{shared_gnss_lat.value},{shared_gnss_long.value},{goodput}\n")
                    t2 = time.time()
                    if t2 - t0 < 1.0:
                        # Limit loop to 1Hz
                        time.sleep(1.0 - (t2 - t0))
            except socket.timeout:
                # Socket timedout, so we assume there is 0 throughput
                # We try to reinit the socket and continue
                print(f"Socket timedout, assuming 0 throughput and attempting to reconnect.")
                sock.close()
                output_file.write(f"{shared_gnss_generation_time.value},{shared_gnss_lat.value},{shared_gnss_long.value},{0.0}\n")
            except ConnectionError:
                print(f"Connection error, assuming 0 throughput and attempting to reconnect. Make sure server is running.")
                sock.close()
                output_file.write(f"{shared_gnss_generation_time.value},{shared_gnss_lat.value},{shared_gnss_long.value},{0.0}\n")
            output_file.flush()

    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Measure network throughput')
    parser.add_argument("--output_csv", type=Path, required=True, help="Output file")
    parser.add_argument("--remote", type=str, required=True, help="Remote host to send data to")
    parser.add_argument("--remote_port", type=int, required=True, help="Remote port to send data to")
    parser.add_argument("--message_bytes", type=int, required=True, help="Number of bytes to send in each message to measure the throughput. We assume that the gnss coordinates are constant while sending a single message.")
    args = parser.parse_args()
    measure_throughput(args.output_csv, args.remote, args.remote_port, args.message_bytes)

