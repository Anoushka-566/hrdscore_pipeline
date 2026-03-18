## scarHRD Installation (HPC)

### Option 1 (Online)
sbatch install_scarhrd.slurm

### Option 2 (Offline)
wget https://github.com/sztup/scarHRD/archive/refs/heads/master.zip
unzip master.zip
cd scarHRD-master
R CMD INSTALL .