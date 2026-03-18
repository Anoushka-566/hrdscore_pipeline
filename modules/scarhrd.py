import subprocess
import logging


def run_scarhrd(seg_file, ploidy, env):

    cmd = f"""
    conda run -n {env} Rscript scripts/run_scarhrd.R \
        --seg {seg_file} \
        --ploidy {ploidy}
    """

    subprocess.run(cmd, shell=True, check=True)

    logging.info("scarHRD completed")