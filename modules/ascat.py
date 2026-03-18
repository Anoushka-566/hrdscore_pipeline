import subprocess
import logging
import os


def run_ascat(tumor_bam, normal_bam, sample_dir, env):

    logging.info("Running ASCAT")

    ascat_output = os.path.join(sample_dir, "ascat_output.RData")

    cmd = f"""
    conda run -n {env} Rscript scripts/run_ascat.R \
        --tumor {tumor_bam} \
        --normal {normal_bam} \
        --out {ascat_output}
    """

    subprocess.run(cmd, shell=True, check=True)

    logging.info("ASCAT completed")

    return ascat_output