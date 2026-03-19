import argparse
import yaml
import pandas as pd
import os
import logging
import time
import psutil
import subprocess
from datetime import datetime

from modules.envcheck import check_env, check_tool
from modules.slurm import submit_job


# -----------------------------
# Logger setup
# -----------------------------
def setup_logger():
    os.makedirs("logs", exist_ok=True)

    log_file = f"logs/pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    logging.info("=================================")
    logging.info(" HRD ANALYSIS PIPELINE STARTED")
    logging.info("=================================")


# -----------------------------
# Load config
# -----------------------------
def load_config():
    with open("config.yaml") as f:
        return yaml.safe_load(f)


# -----------------------------
# Tool version logging
# -----------------------------
def log_tool_versions():
    os.makedirs("logs", exist_ok=True)

    with open("logs/tool_versions.txt", "w") as f:
        f.write("Tool Versions:\n\n")

        tools = ["samtools", "bcftools", "minimap2", "R"]

        for tool in tools:
            try:
                output = subprocess.getoutput(f"{tool} --version")
                f.write(f"{tool}:\n{output}\n\n")
            except Exception as e:
                f.write(f"{tool}: NOT FOUND ({e})\n\n")

    logging.info("Tool versions logged")


# -----------------------------
# Resource monitor
# -----------------------------
def get_memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024**2)  # MB


# -----------------------------
# Submit step with logging
# -----------------------------
def run_step(step_name, job_script, args, dependency=None):
    logging.info(f"STARTING: {step_name}")

    start_time = time.time()
    mem_before = get_memory_usage()

    job_id = submit_job(job_script, args, dependency=dependency)

    end_time = time.time()
    mem_after = get_memory_usage()

    runtime = round(end_time - start_time, 2)

    logging.info(
        f"SUBMITTED: {step_name} | JobID: {job_id} | "
        f"Time: {runtime}s | Mem Before: {mem_before:.2f} MB | Mem After: {mem_after:.2f} MB"
    )

    return job_id


# -----------------------------
# Process one sample
# -----------------------------
def process_sample(sample_id, tumor_bam, normal_bam, config):
    logging.info(f"=================================")
    logging.info(f"PROCESSING SAMPLE: {sample_id}")
    logging.info(f"=================================")

    sample_dir = f"results/{sample_id}"
    os.makedirs(sample_dir, exist_ok=True)

    # -----------------------------
    # STEP 1 — QC
    # -----------------------------
    tumor_qc_job = run_step(
        "Tumor QC",
        "jobs/qc.sh",
        [tumor_bam, f"{sample_dir}/tumor_flagstat.txt"]
    )

    normal_qc_job = run_step(
        "Normal QC",
        "jobs/qc.sh",
        [normal_bam, f"{sample_dir}/normal_flagstat.txt"]
    )

    # -----------------------------
    # STEP 2 — Coverage
    # -----------------------------
    tumor_cov_job = run_step(
        "Tumor Coverage",
        "jobs/coverage.sh",
        [tumor_bam, f"{sample_dir}/tumor_coverage.txt"],
        dependency=tumor_qc_job
    )

    normal_cov_job = run_step(
        "Normal Coverage",
        "jobs/coverage.sh",
        [normal_bam, f"{sample_dir}/normal_coverage.txt"],
        dependency=normal_qc_job
    )

    # -----------------------------
    # STEP 3 — ASCAT
    # -----------------------------
    ascat_job = run_step(
        "ASCAT Analysis",
        "jobs/ascat.sh",
        [tumor_bam, normal_bam, sample_dir],
        dependency=f"{tumor_cov_job},{normal_cov_job}"
    )

    # -----------------------------
    # STEP 4 — scarHRD
    # -----------------------------
    seg_file = f"{sample_dir}/ascat_segments_for_scarHRD.txt"

    scarhrd_job = run_step(
        "scarHRD Scoring",
        "jobs/scarhrd.sh",
        [seg_file, sample_dir],
        dependency=ascat_job
    )

    logging.info(f"COMPLETED SAMPLE: {sample_id}")


# -----------------------------
# Main pipeline
# -----------------------------
def main(samples_file):
    setup_logger()

    config = load_config()

    # -----------------------------
    # Tool version logging
    # -----------------------------
    log_tool_versions()

    # -----------------------------
    # Environment check
    # -----------------------------
    logging.info("Checking environments")

    samtools_env = config["tools"]["samtools_env"]

    check_env(samtools_env)
    check_tool(samtools_env, "samtools")

    logging.info("Environment validation passed")

    # -----------------------------
    # Load samples
    # -----------------------------
    samples = pd.read_csv(samples_file, sep="\t")

    logging.info(f"Samples detected: {len(samples)}")

    start_pipeline = time.time()

    # -----------------------------
    # Process samples
    # -----------------------------
    for _, row in samples.iterrows():
        process_sample(
            row["sample_id"],
            row["tumor_bam"],
            row["normal_bam"],
            config
        )

    end_pipeline = time.time()
    total_time = round(end_pipeline - start_pipeline, 2)

    logging.info("=================================")
    logging.info(f"PIPELINE COMPLETED | Total Time: {total_time}s")
    logging.info("Jobs are running on SLURM compute nodes")
    logging.info("=================================")


# -----------------------------
# CLI arguments
# -----------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--samples",
        required=True,
        help="Sample sheet containing tumor-normal BAM pairs"
    )

    args = parser.parse_args()

    main(args.samples)