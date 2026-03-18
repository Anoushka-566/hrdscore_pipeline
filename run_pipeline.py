import argparse
import yaml
import pandas as pd
import os
import logging
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

    logging.info("Pipeline logging initialized")


# -----------------------------
# Load config
# -----------------------------
def load_config():

    with open("config.yaml") as f:
        config = yaml.safe_load(f)

    return config


# -----------------------------
# Process one sample
# -----------------------------
def process_sample(sample_id, tumor_bam, normal_bam, config):
    logging.info(f"Processing sample {sample_id}")

    print("\n=================================")
    print(f"Processing sample: {sample_id}")
    print("=================================")

    samtools_env = config["tools"]["samtools_env"]

    sample_dir = f"results/{sample_id}"
    os.makedirs(sample_dir, exist_ok=True)

   
    # STEP 1 — QC
    
    logging.info("Submitting QC jobs")

    tumor_qc_job = submit_job(
        "jobs/qc.sh",
        [tumor_bam, f"{sample_dir}/tumor_flagstat.txt"]
    )

    normal_qc_job = submit_job(
        "jobs/qc.sh",
        [normal_bam, f"{sample_dir}/normal_flagstat.txt"]
    )

    logging.info(f"Tumor QC job ID: {tumor_qc_job}")
    logging.info(f"Normal QC job ID: {normal_qc_job}")

    # -----------------------------
    # STEP 2 — Coverage
    # -----------------------------
    logging.info("Submitting coverage jobs")

    tumor_cov_job = submit_job(
        "jobs/coverage.sh",
        [tumor_bam, f"{sample_dir}/tumor_coverage.txt"],
        dependency=tumor_qc_job
    )

    normal_cov_job = submit_job(
        "jobs/coverage.sh",
        [normal_bam, f"{sample_dir}/normal_coverage.txt"],
        dependency=normal_qc_job
    )

    logging.info(f"Tumor coverage job ID: {tumor_cov_job}")
    logging.info(f"Normal coverage job ID: {normal_cov_job}")

    print("QC and Coverage jobs submitted to SLURM")
    print("Results will appear in results directory")
    
    # -----------------------------
    # STEP 3 — ASCAT
    # -----------------------------
    
    logging.info("Submitting ASCAT job")

    ascat_job = submit_job(
    "jobs/ascat.sh",
    [tumor_bam, normal_bam, sample_dir],
    dependency=f"{tumor_cov_job},{normal_cov_job}"
    )

    logging.info(f"ASCAT job ID: {ascat_job}")
    
    # -----------------------------
    # STEP 4 — scarHRD
    # -----------------------------
    
    logging.info("Submitting scarHRD job")
    
    seg_file = f"{sample_dir}/ascat_segments_for_scarHRD.txt"
    
    scarhrd_job = submit_job(
        "jobs/scarhrd.sh",
        [seg_file, sample_dir],
        dependency=ascat_job
    )
    
    logging.info(f"scarHRD job ID: {scarhrd_job}")


# -----------------------------
# Main pipeline
# -----------------------------
def main(samples_file):

    setup_logger()

    logging.info("=================================")
    logging.info(" HRD ANALYSIS PIPELINE STARTED")
    logging.info("=================================")

    # Load configuration
    config = load_config()

    samtools_env = config["tools"]["samtools_env"]

    # -----------------------------
    # Environment check
    # -----------------------------
    logging.info("Checking environments")

    check_env(samtools_env)
    check_tool(samtools_env, "samtools")

    print("Environment validation passed")

    # -----------------------------
    # Load samples
    # -----------------------------
    samples = pd.read_csv(samples_file, sep="\t")

    print(f"\nSamples detected: {len(samples)}")

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

    print("\nPipeline controller finished.")
    print("Jobs are running on SLURM compute nodes.")


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