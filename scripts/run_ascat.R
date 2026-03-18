library(optparse)
library(ASCAT)

option_list <- list(
  make_option("--tumor", type="character"),
  make_option("--normal", type="character"),
  make_option("--outdir", type="character")
)

opt <- parse_args(OptionParser(option_list=option_list))

tumor <- opt$tumor
normal <- opt$normal
outdir <- opt$outdir

dir.create(outdir, showWarnings = FALSE, recursive = TRUE)

cat("====================================\n")
cat("Running ASCAT pipeline\n")
cat("Tumor BAM:", tumor, "\n")
cat("Normal BAM:", normal, "\n")
cat("Output directory:", outdir, "\n")
cat("====================================\n")

# Paths
allelecounter_path <- "/home/anoushka/miniconda3/envs/ascatenv/bin/alleleCounter"

loci.prefix <- "/scratch/mallya/anoushka/hrd/software/ascatNgs/ascat_resources/G1000_loci_hg38_chr"
alleles.prefix <- "/scratch/mallya/anoushka/hrd/software/ascatNgs/ascat_resources/G1000_alleles_hg38_chr"

tumor_LogR <- paste0(outdir,"/tumor_LogR.txt")
tumor_BAF <- paste0(outdir,"/tumor_BAF.txt")
normal_LogR <- paste0(outdir,"/normal_LogR.txt")
normal_BAF <- paste0(outdir,"/normal_BAF.txt")

cat("Step 1: Preparing HTS data\n")

ascat.prepareHTS(
  tumourseqfile = tumor,
  normalseqfile = normal,
  tumourname = basename(tumor),
  normalname = basename(normal),
  allelecounter_exe = allelecounter_path,
  loci.prefix = loci.prefix,
  alleles.prefix = alleles.prefix,
  genomeVersion = "hg38",
  nthreads = 8,
  tumourLogR_file = tumor_LogR,
  tumourBAF_file = tumor_BAF,
  normalLogR_file = normal_LogR,
  normalBAF_file = normal_BAF,
  loci_binsize = 500,
  min_base_qual = 10,
  additional_allelecounter_flags = "-f 0",
  gender = "XY",
  chrom_names = c(as.character(1:22), "X", "Y")
)

cat("LogR and BAF generated\n")

cat("Step 2: Loading ASCAT data\n")

ascat.bc <- ascat.loadData(
  Tumor_LogR_file = tumor_LogR,
  Tumor_BAF_file = tumor_BAF,
  Germline_LogR_file = normal_LogR,
  Germline_BAF_file = normal_BAF
)

cat("Step 3: Segmentation\n")

ascat.bc <- ascat.aspcf(ascat.bc)

cat("Step 4: Running ASCAT\n")

ascat.output <- ascat.runAscat(ascat.bc)

save(ascat.output, file=paste0(outdir,"/ascat_output.RData"))

cat("ASCAT analysis completed\n")

ascat_seg <- ascat.output$segments
ascat_seg$total_cn <- ascat_seg$nMajor + ascat_seg$nMinor
ascat_seg$A_cn <- ascat_seg$nMajor
ascat_seg$B_cn <- ascat_seg$nMinor
ascat_seg$ploidy <- as.numeric(ascat.output$ploidy)

scar_input <- data.frame(
  SampleID = ascat_seg$sample,
  Chromosome = ascat_seg$chr,
  Start_position = ascat_seg$startpos,
  End_position = ascat_seg$endpos,
  total_cn = ascat_seg$total_cn,
  A_cn = ascat_seg$A_cn,
  B_cn = ascat_seg$B_cn,
  ploidy = ascat_seg$ploidy
)

outfile <- paste0(outdir,"/ascat_segments_for_scarHRD.txt")

write.table(
  scar_input,
  file = outfile,
  sep = "\t",
  quote = FALSE,
  row.names = FALSE
)

cat("scarHRD input file generated\n")
cat("ASCAT pipeline finished successfully\n")