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
    echo "-c | --collapse COLLAPSE_FILE - [Required] A .tsv file which consists of group labels and parent lineages to collapse under them (Format provided on Github)."
    echo "-b | --barcode BARCODE_FILE - A .csv barcode file to be used by Freyja for processing (Format provided on Github)."
    echo "-p | --removeFromFile FILE_PATTERN - A regex pattern that can be used to remove extraneous text from a sample name (Example provided on Github)."
    echo "--s_gene - Tells the pipeline to adapt for S-gene sequencing only (will modify barcodes to remove non-s-gene mutations and combine lineages identical within the s gene)"
    echo "--byDate - Produces data grouped by date rather than by individual samples"
    echo "--byWeek - Produces data grouped by week rather than by individual samples. Weeks start on Monday."
    echo "--combineAll - Produces a combined file where lineage abundances from all sites are averaged together for each day/week."
    echo
}

OPTIONS=$(getopt -o i:o:d:r:m:b:c:p:h -l input:,output:,demixDir:,reference:,masterfile:,barcode:,collapse:,removeFromFile:,s_gene,byDate,byWeek,combineAll,help -a -- "$@")
if [ $? -ne 0 ]
then
    echo ""
    Help
    exit 1
fi

INDIR=
OUTDIR=
DEMIXDIR=
REF=
MASTER=
BARCODE=
COLLAPSE=
PATTERN=
BYOPTION=
SGENE=
BYWEEK=
BYDATE=
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
    -c | --collapse )
        COLLAPSE="$2"
        shift 2
        ;;
    -p | --removeFromFile )
        PATTERN="--pattern $2"
        shift 2
        ;;
    --s_gene )
        SGENE="--s_gene"
        shift
        ;;
    --byDate )
        BYDATE="--byDate"
        shift
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
        exit 1
        ;;
    -- )
        shift
        break
        ;;
    * )
        Help
        exit 1
        ;;
  esac
done

echo ''

if [ -z "$INDIR" ]
then
    echo "No input directory provided. Please include an input directory (-i/--input)!"
    echo ''
    exit 1
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
        exit 1 
    fi
fi

if [ -z "$OUTDIR" ]
then
    echo "No output directory provided. Please include an input directory (-o/--output)!"
    echo ''
    exit 1
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
    exit 1
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
        exit 1
    fi
fi

if [ -z "$REF" ]
then
    echo "No reference provided. Please include a reference fasta file (-r/--reference)"
    echo ''
    exit 1
elif [ ! -f "$REF" ]
then
    echo "File $CURRENTDIR$REF does not exist. Please include an existing file and check the path provided (-r/--reference)!"
    echo ''
    exit 1
fi

if [ -z "$MASTER" ]
then
    echo "No master file provided. Please include a master file (-m/--masterfile)!"
    echo ''
    exit 1
elif [ ! -f "$MASTER" ]
then
    echo "File $MASTER does not exist. Please include an existing file and check the path provided (-m/--mastefile)!"
    echo ''
    exit 1
fi

if [ -z "$COLLAPSE" ]
then
    echo "No collapse file provided. Please include a sublineage map file (-c/--collapse)"
    echo ''
    exit 1
elif [ ! -f "$COLLAPSE" ]
then
    echo "File $COLLAPSE does not exist. Please include an existing file and check the path provided (-c/--collapse)!"
    echo ''
    exit 1
fi

if [ -n "$BYDATE" ] && [ -n "$BYWEEK" ]
then
    echo "Both the --byDate and --byWeek options have been provided. Only one can be supplied."
    echo ''
    exit 1
else
    if [ -n "$BYDATE" ] 
    then 
        BYOPTION=$BYDATE
    elif [ -n "$BYWEEK" ]
    then
        BYOPTION=$BYWEEK
    fi
fi



FREYJA_DIR=$OUTDIR"freyja-results/"
if [ ! -d "${OUTDIR}freyja-results/" ]
then
    mkdir $FREYJA_DIR
fi

if [ -n "$SGENE" ]
then
    echo "The S-Gene option was supplied."
    echo "Barcodes used to classify lineages will be modified to remove any mutations outside of the s gene"
    echo "Lineages with identical S gene mutation profiles will be grouped together"
    echo ''
fi

BARCODEOPT=''
BARCODE_DIR=$OUTDIR"barcodes-and-collapse/"
if [ -z "$BARCODE" ]
then
    echo "No barcode file provided. Updated barcodes will be created using Freyja"
    BARCODEOPT='--confirmedonly'
    echo ''

    if [ ! -d "$BARCODE_DIR" ]
    then
        mkdir $BARCODE_DIR
    fi
    
    python3 $SCRIPT_DIR"scripts/update_barcodes_and_collapse.py" -o $BARCODE_DIR -c $COLLAPSE $SGENE

    if [ -n "$SGENE" ]
    then 
        BARCODEOPT=$BARCODE_DIR"S_Gene_barcodes.csv"
    else
        BARCODEOPT=$BARCODE_DIR"filtered_barcodes.csv"
    fi

elif [ ! -f "$BARCODE" ]
then
    echo "File $BARCODE does not exist. Please include an existing file and check the path provided (-b/--barcode)!"
    echo ''
    exit 1
else 
    echo "Barcode file $BARCODE supplied."

    if [ ! -d "$BARCODE_DIR" ]
    then
        mkdir $BARCODE_DIR
    fi
    python3 $SCRIPT_DIR"scripts/update_barcodes_and_collapse.py" -i $BARCODE -o $BARCODE_DIR -c $COLLAPSE $SGENE

    if [ -n "$SGENE" ]
    then 
        BARCODEOPT=$BARCODE_DIR"S_Gene_barcodes.csv"
    else
        BARCODEOPT=$BARCODE_DIR"filtered_barcodes.csv"
    fi
fi

SUBLINEAGE_MAP=$BARCODE_DIR"sublineage-map.tsv"

echo "Performing Variant Calling"
echo ''
for file in $INDIR*.bam
do
    base=$(basename $file .bam)
    echo $base
    freyja variants $file --variants "${FREYJA_DIR}${base}-variants.tsv" --depths "${FREYJA_DIR}${base}-depths.tsv" --ref $REF
done
echo ''

echo "Performing Demixing"
for file in $FREYJA_DIR*-variants.tsv
do
    base=$(basename $file -variants.tsv)
    echo $base
    freyja demix $file "${FREYJA_DIR}${base}-depths.tsv" --output "${FREYJA_DIR}${base}.demix" --barcodes $BARCODEOPT
done
echo ''

cp $FREYJA_DIR*.demix $DEMIXDIR
echo "python3 ${SCRIPT_DIR}scripts/parse_freyja.py -i $DEMIXDIR -o $OUTDIR -s $SUBLINEAGE_MAP -m $MASTER $PATTERN $BYOPTION $COMBINEALL"
python3 $SCRIPT_DIR"scripts/parse_freyja.py" -i $DEMIXDIR -o $OUTDIR -s $SUBLINEAGE_MAP -m $MASTER $PATTERN $BYOPTION $COMBINEALL
