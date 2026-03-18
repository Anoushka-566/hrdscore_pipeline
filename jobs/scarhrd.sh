#!/bin/bash
#SBATCH --job-name=scarhrd
#SBATCH --output=logs/scarhrd_%j.out
#SBATCH --error=logs/scarhrd_%j.err
#SBATCH --time=02:00:00
#SBATCH --mem=8G
#SBATCH --cpus-per-task=2

echo "===================================="
echo "HRD PIPELINE : scarHRD"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURMD_NODENAME"
echo "Start time: $(date)"
echo "===================================="

source ~/miniconda3/etc/profile.d/conda.sh
conda activate scarhrd

seg=$1
outdir=$2

Rscript scripts/run_scarhrd.R \
  --seg $seg \
  --outdir $outdir

echo "scarHRD completed"
echo "End time: $(date)"

# resource logging
sacct -j $SLURM_JOB_ID \
--format=JobID,JobName,Elapsed,CPUTime,MaxRSS,State \
>> logs/resource_usage.log