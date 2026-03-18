import subprocess
import os
import logging


def extract_segments(ascat_rdata, sample_dir, env):

    output = os.path.join(sample_dir, "ascat_segments.tsv")

    cmd = f"""
    conda run -n {env} Rscript scripts/extract_segments.R \
        --input {ascat_rdata} \
        --output {output}
    """

    subprocess.run(cmd, shell=True, check=True)

    logging.info("Segments extracted")

    return output