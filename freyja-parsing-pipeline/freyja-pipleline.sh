#!/usr/bin/env bash

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
        echo "Add Help Message"
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

mv $FREYJA_DIR*.demix $DEMIXDIR

python3 $SCRIPT_DIR"scripts/parse_freyja-v2.py" -i $DEMIXDIR -o $OUTDIR -s $SUBLIN -m $MASTER $PATTERN $BYWEEK $COMBINEALL
