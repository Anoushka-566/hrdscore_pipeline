#!/bin/bash
#SBATCH --job-name=hrd_cov
#SBATCH --output=logs/coverage_%j.out
#SBATCH --error=logs/coverage_%j.err
#SBATCH --time=08:00:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=4

echo "================================================="
echo "HRD PIPELINE : COVERAGE STEP"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURMD_NODENAME"
echo "Partition: $SLURM_JOB_PARTITION"
echo "CPUs allocated: $SLURM_CPUS_PER_TASK"
echo "Memory allocated: $SLURM_MEM_PER_NODE MB"
echo "Start time: $(date)"
echo "================================================="

source ~/miniconda3/etc/profile.d/conda.sh
conda activate ascat_new

echo "Samtools version:"
samtools --version | head -n 1

bam=$1
outfile=$2

echo "Input BAM: $bam"

start=$(date +%s)

samtools depth -a $bam | awk '{sum+=$3} END {print sum/NR}' > $outfile

end=$(date +%s)
runtime=$((end-start))

echo "Coverage result:"
cat $outfile

echo "-------------------------------------------------"
echo "Runtime (seconds): $runtime"
echo "End time: $(date)"
echo "================================================="