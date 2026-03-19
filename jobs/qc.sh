#!/bin/bash
#SBATCH --job-name=hrd_qc
#SBATCH --output=logs/qc_%j.out
#SBATCH --error=logs/qc_%j.err
#SBATCH --time=02:00:00
#SBATCH --mem=8G
#SBATCH --cpus-per-task=2

echo "================================================="
echo "HRD PIPELINE : QC STEP"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURMD_NODENAME"
echo "Partition: $SLURM_JOB_PARTITION"
echo "CPUs allocated: $SLURM_CPUS_PER_TASK"
echo "Memory allocated: $SLURM_MEM_PER_NODE MB"
echo "Submit directory: $SLURM_SUBMIT_DIR"
echo "User: $SLURM_JOB_USER"
echo "Start time: $(date)"
echo "================================================="

source ~/miniconda3/etc/profile.d/conda.sh
conda activate ascat_new

echo "Conda environment:"
conda info --envs

echo "Samtools version:"
samtools --version | head -n 1

bam=$1
outfile=$2

echo "Input BAM: $bam"
echo "Output file: $outfile"

start=$(date +%s)

samtools flagstat $bam > $outfile

end=$(date +%s)
runtime=$((end-start))

echo "-------------------------------------------------"
echo "Runtime (seconds): $runtime"
echo "End time: $(date)"
echo "================================================="