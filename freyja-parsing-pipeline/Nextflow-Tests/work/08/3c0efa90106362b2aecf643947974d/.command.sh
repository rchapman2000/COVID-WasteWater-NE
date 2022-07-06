#!/bin/bash

mkdir results

python3 parse_freyja-v2.py -i /home/rchap/Working/freyja-ww-working/freyja-pipeline-nextflow/./demix/ -o results --sublineageMap Sublineage-Parent-Map-BROAD-Lineages-v2.csv --mastersheet 070522ParsedMaster.csv --removefromFile '.+?(?=q?\_S\d*_L\d*)' --byWeek --combineAll
