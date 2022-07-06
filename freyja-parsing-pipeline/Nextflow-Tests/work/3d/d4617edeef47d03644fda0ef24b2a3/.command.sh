#!/bin/bash

echo WWS-00643q_S36_L001.clipped.bam

freyja variants WWS-00643q_S36_L001.clipped.bam --variants WWS-00643q_S36_L001-variants.tsv --depths WWS-00643q_S36_L001-depths.tsv --ref input.2

echo "Completed Variants"

freyja demix WWS-00643q_S36_L001-variants.tsv WWS-00643q_S36_L001-depths.tsv --output WWS-00643q_S36_L001.demix --barcodes Modified_usher_barcodes_Final.csv
