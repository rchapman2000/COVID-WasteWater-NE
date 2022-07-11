#!/usr/bin/env bash

Help()
{
    echo "freyja-pipeline.sh - The purpose of this pipeline is to automate the analysis of wastewater data using freyja."
    echo "                     This pipeline takes a new set of data, analyzes it with freyja and aggregates/parses the data"
    echo "                     either by itself or with previously run data."
    echo
    echo "Usage: freyja-pipeline.sh -i INPUT_DIRECTORY -o OUTPUT_DIRECTORY -d DEMIX_FILE_DIRECTORY -r REFERENCE -m MASTER_FILE -b BARCODE_FILE -s SUBLINEAGE_MAP"
    echo "Optional arguments [-p FILE_PATTERN | --byWeek | --combineAll | -h]"
    echo
    echo "Option Descriptions:"
    echo "-i | --input INPUT_DIRECTORY - [Required] Directory containing input .bam files (Must be existing)."
    echo "-o | --output OUTPUT_DIRECTORY - [Required] Directory to place pipeline output (the pipeline will create this directory if it does not exist)."
    echo "-d | --demixDir DEMIX_FILE_DIRECTORY - [Required] Directory to place .demix files produced by freyja. The purpose of this option is to allow for aggregation of input files with previously run data. The demix directory may contain .demix files from previous runs, and these will be included in the file output files."
    echo "-r | --reference REFERENCE - [Required] A reference fasta file to be used (Must be the same reference used to generate the input bam files)."
    echo "-m | --masterfile MASTER_FILE - [Required] A .csv file that links sample names to wastewater sites and collection dates (Format provided on Github)."
    echo "-b | --barcode BARCODE_FILE - [Required] A .csv barcode file to be used by Freyja for processing (Format provided on Github)."
    echo "-s | --sublineageMap SUBLINEAGE_MAP - [Required] A .csv file which denotes how to collapse lineages produced by Freyja (Format provided on Github)."
    echo "-p | --removeFromFile FILE_PATTER - A regex pattern that can be used to remove extraneous text from a sample name (Example provided on Github)."
    echo "--byWeek - Produces data grouped by week rather than be individual sample collection date."
    echo "--combineAll - Produces a combined file where lineage abundances from all sites are averaged together for each day/week."
    echo
}

OPTIONS=$(getopt -o i:o:d:r:m:b:s:p:h -l input:,output:,demixDir:,reference:,masterfile:,barcode:,sublineageMap:,removeFromFile:,byWeek,combineAll,help -a -- "$@")

INDIR=
OUTDIR=
DEMIXDIR=
REF=
MASTER=
BARCODE=
SUBLIN=
PATTERN=
BYWEEK=
COMBINEALL=

SCRIPT_DIR="$(dirname ${BASH_SOURCE})/"
CURRENT_DIR="$(pwd)/"

eval set -- "$OPTIONS"
while true; do
  case "$1" in
    -i | --input ) 
        INDIR="$2"
        shift 2 
        ;;
    -o | --output )
        OUTDIR="$2"
        shift 2
        ;;
    -d | --demixDir ) 
        DEMIXDIR="$2"
        shift 2
        ;;
    -r | --reference )
        REF="$2"
        shift 2
        ;;
    -m | --masterfile )
        MASTER="$2"
        shift 2
        ;;
    -b | --barcode )
        BARCODE="$2"
        shift 2
        ;;
    -s | --sublineageMap )
        SUBLIN="$2"
        shift 2
        ;;
    -p | --removeFromFile )
        PATTERN="--removefromFile $2"
        shift 2
        ;;
    --byWeek )
        BYWEEK="--byWeek"
        shift
        ;;
    --combineAll ) 
        COMBINEALL="--combineAll"
        shift 
        ;;
    -h | --help )
        Help
        return 0
        ;;
    -- )
        shift
        break
        ;;
  esac
done

echo ''

if [ -z "$INDIR" ]
then
    echo "No input directory provided. Please include an input directory (-i/--input)!"
    echo ''
    return 0
else
    if [[ ! $INDIR == /* ]]
    then
        INDIR="${CURRENT_DIR}${INDIR}"
    fi

    if [[ ! $INDIR == */ ]]
    then
        INDIR="${INDIR}/"
    fi

    if [ ! -d "$INDIR" ]
        then
        echo "Directory $INDIR not found. Please include an existing directory (-i/--input)!"
        echo ''
        return 0
    fi
fi

if [ -z "$OUTDIR" ]
then
    echo "No output directory provided. Please include an input directory (-o/--output)!"
    echo ''
    return 0
else 
    if [[ ! $OUTDIR == /* ]]
    then 
        OUTDIR="${CURRENT_DIR}${OUTDIR}"
    fi

    if [[ ! $OUTDIR == */ ]]
    then
        OUTDIR="${OUTDIR}/"
    fi

    if [ ! -d "$OUTDIR" ]
    then
        echo "Directory $OUTDIR does not exist. Creating it in the current directory"
        echo ''
        mkdir $OUTDIR
    fi
fi

if [ -z "$DEMIXDIR" ]
then
    echo "No directory to place '.demix' files provided. Please include a directory (-d/--demixDir)!"
    echo ''
    return 0
else
    if [[ ! $DEMIXDIR == /* ]]
    then 
        DEMIXDIR="${CURRENT_DIR}${DEMIXDIR}"
    fi

    if [[ ! $DEMIXDIR == */ ]]
    then
        DEMIXDIR="${DEMIXDIR}/"
    fi

    if [ ! -d "$DEMIXDIR" ]
    then
        echo "Directory $DEMIXDIR not found. Please include a valid directory to place '.demix' files (-d/--demixDir)!"
        echo ''
        return 0
    fi
fi

if [ -z "$REF" ]
then
    echo "No reference provided. Please include a reference fasta file (-r/--reference)"
    echo ''
    return 0
elif [ ! -f "$REF" ]
then
    echo "File $REF does not exist. Please include an existing file and check the path provided (-r/--reference)!"
    echo ''
    return 0
fi

if [ -z "$MASTER" ]
then
    echo "No master file provided. Please include a master file (-m/--masterfile)!"
    echo ''
    return 0
elif [ ! -f "$MASTER" ]
then
    echo "File $MASTER does not exist. Please include an existing file and check the path provided (-m/--mastefile)!"
    echo ''
    return 0
fi

if [ -z "$BARCODE" ]
then
    echo "No barcode file provided. Please include a barcode file (-b/--barcode)"
    echo ''
    return 0
elif [ ! -f "$BARCODE" ]
then
    echo "File $BARCODE does not exist. Please include an existing file and check the path provided (-b/--barcode)!"
    echo ''
    return 0
fi

if [ -z "$SUBLIN" ]
then
    echo "No sublineage map file provided. Please include a sublineage map file (-s/--sublineageMap)"
    echo ''
    return 0
elif [ ! -f "$SUBLIN" ]
then
    echo "File $SUBLIN does not exist. Please include an existing file and check the path provided (-s/--sublineageMap)!"
    echo ''
    return 0
fi


FREYJA_DIR=$OUTDIR"freyja-results/"

mkdir $FREYJA_DIR


echo "Performing Variant Calling"
echo ''
for file in $INDIR*.bam
do
    base=$(basename $file .clipped.bam)
    echo $base
    freyja variants $file --variants "${FREYJA_DIR}${base}-variants.tsv" --depths "${FREYJA_DIR}${base}-depths.tsv" --ref $REF
done
echo ''

echo "Performing Demixing"
for file in $FREYJA_DIR*-variants.tsv
do
    base=$(basename $file -variants.tsv)
    echo $base
    freyja demix $file "${FREYJA_DIR}${base}-depths.tsv" --output "${FREYJA_DIR}${base}.demix" --barcodes $BARCODE
done
echo ''

cp $FREYJA_DIR*.demix $DEMIXDIR

python3 $SCRIPT_DIR"scripts/parse_freyja-v2.py" -i $DEMIXDIR -o $OUTDIR -s $SUBLIN -m $MASTER $PATTERN $BYWEEK $COMBINEALL
