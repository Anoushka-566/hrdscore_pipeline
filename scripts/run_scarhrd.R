library(optparse)
library(scarHRD)

option_list <- list(
  make_option("--seg", type="character"),
  make_option("--outdir", type="character")
)

opt <- parse_args(OptionParser(option_list=option_list))

seg_file <- opt$seg
outdir <- opt$outdir

cat("====================================\n")
cat("Running scarHRD\n")
cat("Segments file:", seg_file, "\n")
cat("Output directory:", outdir, "\n")
cat("====================================\n")

hrd <- scar_score(
  seg = seg_file,
  reference = "grch38",
  chr.in.names = FALSE,
  seqz = FALSE,
  ploidy = NULL
)

outfile <- paste0(outdir, "/HRD_results.txt")

write.table(
  hrd,
  file = outfile,
  sep = "\t",
  quote = FALSE,
  row.names = FALSE
)

cat("HRD scoring completed\n")