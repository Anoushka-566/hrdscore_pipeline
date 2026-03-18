library(optparse)
library(ASCAT)

option_list <- list(
  make_option("--tumor", type="character"),
  make_option("--normal", type="character"),
  make_option("--out", type="character")
)

opt <- parse_args(OptionParser(option_list=option_list))

tumor <- opt$tumor
normal <- opt$normal
outfile <- opt$out

cat("Running ASCAT\n")

# placeholder ASCAT run
# replace with your full ASCAT pipeline

load("ascat_test_output.RData")

save(ascat.output, file=outfile)