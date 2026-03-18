import subprocess
import logging

def submit_job(script, args, dependency=None):

    cmd = ["sbatch"]

    if dependency:
        cmd.append(f"--dependency=afterok:{dependency}")

    cmd.append(script)
    cmd.extend(args)

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(result.stderr)

    job_id = result.stdout.strip().split()[-1]

    logging.info(f"Submitted {script} as job {job_id}")

    return job_id