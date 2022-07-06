#!/bin/bash

echo WWS-00647q_S40_L001.clipped.bam

freyja variants WWS-00647q_S40_L001.clipped.bam --variants WWS-00647q_S40_L001-variants.tsv --depths WWS-00647q_S40_L001-depths.tsv --ref NC_045512.2.fasta

echo "Completed Variants"

freyja demix WWS-00647q_S40_L001-variants.tsv WWS-00647q_S40_L001-depths.tsv --output WWS-00647q_S40_L001.demix --barcodes Modified_usher_barcodes_Final.csv
