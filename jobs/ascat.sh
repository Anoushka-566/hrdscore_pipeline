#!/bin/bash
#SBATCH --job-name=ascat
#SBATCH --output=logs/ascat_%j.out
#SBATCH --error=logs/ascat_%j.err
#SBATCH --time=24:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=8

echo "===================================="
echo "HRD PIPELINE : ASCAT SEGMENTATION"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURMD_NODENAME"
echo "CPUs: $SLURM_CPUS_PER_TASK"
echo "Memory: $SLURM_MEM_PER_NODE"
echo "Start time: $(date)"
echo "===================================="

source ~/miniconda3/etc/profile.d/conda.sh
conda activate ascat_new

tumor=$1
normal=$2
outdir=$3

mkdir -p $outdir

Rscript scripts/run_ascat.R \
  --tumor $tumor \
  --normal $normal \
  --outdir $outdir

echo "ASCAT completed"
echo "End time: $(date)"

# resource logging
sacct -j $SLURM_JOB_ID \
--format=JobID,JobName,Elapsed,CPUTime,MaxRSS,State \
>> logs/resource_usage.log