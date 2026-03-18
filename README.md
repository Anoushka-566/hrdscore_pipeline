HRD Analysis Pipeline

A reproducible pipeline for calculating **Homologous Recombination Deficiency (HRD) scores** using **ASCAT** and **scarHRD**.

---

Installation

1. Clone the repository


git clone https://github.com/username/hrd_pipeline
cd hrd_pipeline

---

2. Create environments

ASCAT environment

conda env create -f ascat.yml
conda activate ascatenv
```

scarHRD environment


conda env create -f scarhrd.yml
conda activate scarhrd


---

3. Install scarHRD


sbatch install_scarhrd.slurm


> Note:
> The original scarHRD package depends on the `sequenza` R package.
> Since this pipeline uses **ASCAT-derived segmentation data only**, the dependency is removed during installation using a scripted patch.

---

4. Configure pipeline

Edit parameters in:


config.yaml


---

5. Run pipeline

python run_pipeline.py --tumor tumor.bam --normal normal.bam


---

Output

* HRD score
* LOH (Loss of Heterozygosity)
* TAI (Telomeric Allelic Imbalance)
* LST (Large-scale State Transitions)

---

Methodology

* Copy number segmentation: **ASCAT**
* HRD scoring: **scarHRD (ASCAT-compatible)**

---

Notes

* This pipeline does **not require Sequenza**
* Designed for **HPC environments (SLURM)**
* Tested with **R 4.2 and Python 3.10**

---

Author

Anoushka
MSc Bioinformatics, Manipal School of Life Sciences
