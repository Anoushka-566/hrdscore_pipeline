#!/bin/bash
#SBATCH --job-name=scarhrd_install
#SBATCH --output=scarhrd_install.out
#SBATCH --error=scarhrd_install.err
#SBATCH --time=02:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G

set -e  # ?? stop on error

echo "Starting scarHRD installation..."

# Load conda
source ~/miniconda3/etc/profile.d/conda.sh
conda activate scarhrd_new

echo "Environment activated"

export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH

# Install deps
conda install -y -c conda-forge unzip wget zlib libzlib r-data.table

# Clean old
rm -rf scarHRD-master master.zip

echo "Downloading scarHRD..."
wget -q https://github.com/sztup/scarHRD/archive/refs/heads/master.zip

echo "Extracting..."
unzip -o master.zip

# ?? Enter correct directory safely
cd scarHRD-master

echo "Current directory:"
pwd
ls

echo "Patching..."

# ? Now this will work
sed -i 's/sequenza (>= 2.1.2),//' DESCRIPTION
sed -i '/import(sequenza)/d' NAMESPACE

echo "Installing..."
R CMD INSTALL .

echo "Testing..."

Rscript - <<EOF
library(scarHRD)
cat("scarHRD installed successfully\n")
EOF

echo "Done!"