#!/bin/bash

freyja variants WWS-00650q_S42_L001.clipped.bam --variants WWS-00650q_S42_L001-variants.tsv --depths WWS-00650q_S42_L001-depths.tsv --ref qbams

freyja demix WWS-00650q_S42_L001-variants.tsv --output WWS-00650q_S42_L001.demix --barcodes input.3

cp *.demix ./demix/
