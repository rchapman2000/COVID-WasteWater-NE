#!/bin/bash -ue
!#/bin/bash

python3 parse_freyja-v2.py -i ./demix/ -o results --sublineageMap Sublineage-Parent-Map-BROAD-Lineages-v2.csv --mastersheet 070522ParsedMaster.csv --removefromFile '.+?(?=q?\_S\d*_L\d*)' --byWeek --combineAll
