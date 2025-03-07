from pathlib import Path
import subprocess
from typing import List
def join_str(l: List, x: str = " "):
    return x.join([str(x) for x in l])
def exec(command: List[str], exec_on_iris: bool, echo_command: bool = True, check=True, force_tty=False, **kwargs):
    command = [str(x) for x in command]
    if exec_on_iris:
        tty = ["-t"] if force_tty else []
        command = ["ssh"] + tty + ["iris-cluster"] + command
    if echo_command:
        print(join_str(command))
    return subprocess.run(command, check=check, **kwargs)
def run_hpc_batch(model, imgsz, zlib_compression, cmax, split_layer, qlevel):
    # TODO Use --batch
    root = Path("/work/projects/360lab/yolo-v2x")
    path_to_singularity_tools = "/Users/faisalhawlader/iris_singularity_tools/iris_singularity_tools.py"
    singularity_image = "/work/projects/360lab/360lab-traffic-light-detection.sif"
    singularity_env = f"PYTHONPATH={root}:{root}/yolov5:{root}/src"
    jobname = f"v2x-l{split_layer:02d}_cmin{float(cmin)}_cmax{float(cmax)}_qlevels{qlevel:02d}_zlib{zlib_compression:02d}"
    data = root / "data/uncompressed-bmp/uncompressed-bmp.yaml"
    command = ["python3", "/work/projects/360lab/yolo-v2x/src/eval_compression.py", f"--data={data}", f"--model_path={model}", f"--imgsz={imgsz}", f"--split_layer={split_layer}", f"--cmin={cmin}", f"--cmax={cmax}", f"--quantization_levels={qlevel}", f"--zlib_compression_level={zlib_compression}"]
    batch = False
    batch_command = ["--batch"] if batch else []
    exec([path_to_singularity_tools, "run"] + batch_command + [f"--job-name={jobname}", "--cpus=7", "--gpus=1", "--mem=32G", "--time=00:30:00", f"--singularity-image={singularity_image}", f"--singularity-env", singularity_env, "--singularity-arg=--bind /work/projects/360lab"] + command, exec_on_iris=False, echo_command=True, check=True)
# TODO Support restarting
if __name__ == "__main__":
    models = [
        Path("/work/projects/360lab/yolo-v2x/experiments/yolo-v2x-yolov5l-640-uncompressed/weights/best.pt"),
        # Path("/work/projects/360lab/yolo-v2x/experiments/yolo-v2x-yolov5l6-1280-uncompressed/weights/best.pt")
    ]
    model_imgszs = [640] #, 1280]
    cmin = 0.0
    for model, imgsz in zip(models, model_imgszs):
        for zlib_compression in [1, 2, 3, 4]:
            for cmax in [1, 2, 3, 4, 5, 7, 10]:
                for split_layer in [1, 2, 3, 4, 5, 6]:
                    for qlevel in [2, 4, 8, 16]:
                        # Check if output file already exists on iris
                        output_path = model.parent / f"{model.stem}_quantized_layer{split_layer:02d}_cmin{float(cmin)}_cmax{float(cmax)}_qlevels{qlevel:02d}_zlib{zlib_compression:02d}-evaluation.json"
                        ls_output_path = exec(["ls", output_path], exec_on_iris=True, check=False, echo_command=True)
                        if ls_output_path.returncode == 0:
                            print(f"Output {output_path} already exists, skipping experiment")
                        else:
                            print(f"Starting experiment {output_path}")
                            run_hpc_batch(model, imgsz, zlib_compression, cmax, split_layer, qlevel)
                    break