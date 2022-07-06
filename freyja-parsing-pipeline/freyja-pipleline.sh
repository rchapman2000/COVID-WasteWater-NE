#!/usr/bin/env bash

TEMP=$(getopt -o i:o:d:r:m:b:s:p:h --long input:,output:,demixDir:,reference:,masterfile:,barcode:,sublineageMap:,removeFromFile:,byWeek,combineAll,help -- "$@")

eval set --"$TEMP"

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


while true; do
  case "$1" in
    -i | --input ) 
        INDIR='$2'
        shift 2 
        ;;
    -o | --output )
        OUTDIR='$2'
        shift 2
        ;;
    -d | --demixDir ) 
        DEMIXDIR='$2'
        shift 2
        ;;
    -r | --reference )
        REF='$2'
        shift 2
    -m | --masterfile )
        MASTER='$2'
        shift 2
        ;;
    -b | --barcode )
        BARCODE='$2'
        shift 2
        ;;
    -s | --sublineageMap )
        SUBLIN='$2'
        shift 2
        ;;
    -p | --removeFromFile )
        PATTERN='--removeFromFile $2'
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
        echo "Add Help Message"
        exit 0
        ;;
    --)
        shift
        break
        ;;
  esac
  shift
done

if [-z "$INPUT"]
then
    echo "No input directory provided. Please include an input directory (-i/--input)!"
    exit 0
elif [-d "$INPUT"]
    echo "Directory $INPUT not found. Please include an existing directory (-i/--input)!"
    exit 0
elif [[ $INPUT == /*]]

fi

if [-z "$OUTPUT"]
then
    echo "No output directory provided. Please include an input directory (-o/--output)!"
    exit 0
elif [-d "$OUTPUT"]
    mkdir $OUPUT
fi

if [-z "$DEMIXDIR"]
then
    echo "No directory to place '.demix' files provided. Please include a directory (-d/--demixDir)!"
    exit 0
elif [-d "$DEMIXDIR"]
    echo "Directory $DEMIXDIR not found. Please include a valid directory to place '.demix' files (-d/--demixDir)!"
    exit 0
fi

if [-z "$REF"]
then
    echo "No reference provided. Please include a reference fasta file (-r/--reference)"
fi reference fasta
if [-r "$reference"]
then
    echo "No master file provided. Please include a master file (-m/--masterfile)!"
    exit 0
fi

if [-z "$BARCODE"]
then
    echo "No barcode file provided. Please include a barcode file (-b/--barcode)"
fi

if [-z "$SUBLIN"]
then
    echo "No sublineage map file provided. Please include a sublineage map file (-s/--sublineageMap)"
fi

for file in $INDIR
do
    base=$(basename $file .*.bam)
    echo $base;
    freyja variants $file --variants $base"-variants.tsv" --depths $base"-depths.tsv" -ref $REF
done

for file in 