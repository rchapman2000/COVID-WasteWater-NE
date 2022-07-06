#!/usr/bin/env/ nextflow

nextflow.enable.dsl=2

def helpMessage() {
    log.info"""
    TO BE ADDED
    """
}

params.help = false
if (params.help){
    helpMessage()
    exit 0
}

params.input = ''
params.reference = ''
params.output = ''
params.barcodes = ''
params.demixDir = ''
params.mastersheet = ''
params.sublineageMap = ''
params.removeFromFile = ''
params.byWeek = false
params.combineAll = false

FREYJAPARSESCRIPT = file("${baseDir}/parse_freyja-v2.py")

// Parse the input directory parameter
INDIR = ''
if (params.input == ''){
    println "No input directory provided! Please provide an input directory containing bam files for analysis."
    exit(1)
}
else if (params.input[-1] != '/'){
    INDIR = params.input + '/'
}
else {
    INDIR = params.input
}

// Parse the output directory parameter
OUTDIR = ''
if (params.output == ''){
    println "No output directory provided! Please provide an output directory to place files."
    exit(1)
}
else if (params.output[-1] != '/'){
    OUTDIR = params.output + '/'
}
else {
    OUTDIR = params.output
}

// Parse the barcodes file parameter
if (params.barcodes == '') {
    println "No barcodes file provided! Please provide a barcodes file."
    exit(1)
}
else if (! file(params.barcodes).exists()){
    println "Barcodes file ${params.barcodes} found!. Please provide a barcodes file."
    exit(1)
}
BARCODES = file(params.barcodes)

// Parse the reference file parameter
if (params.reference == '') {
    println "No reference FASTA file provided! Please provide a reference FASTA file."
    exit(1)
}
else if (! file(params.reference).exists()) {
    println "Reference FASTA ${params.reference} not found! Please provide a reference fasta file."
    exit(1)
}
REF = file(params.reference)

// Parse the demixDir parameter
if (params.demixDir == '') {
    println "No directory containg existing demix files provided! Please provide a directory (--demixDir)."
    exit(1)
}

// Parse the mastersheet parameter
if (params.mastersheet == '') {
    println "No mastersheet file provided! Please provide a mastersheet."
    exit(1)
}
else if (! file(params.mastersheet).exists()) {
    println "Mastersheet ${params.mastersheet} not found! Plaese provide a mastersheet."
    exit(1)
}
MASTER = file(params.mastersheet)

// Parse the sublineage map parameter
if (params.sublineageMap == '') {
    println("Sublineage map file not provided! Please provide a sublineage map.")
    exit(1)
}
else if (!file(params.sublineageMap).exists()) {
    println "Sublineage map ${params.sublineageMap} not found! Please provide a sublineage map."
    exit(1)
}
SUBLIN = file(params.sublineageMap)

// Parses the remove from file option. If nothing is provided, an empty string
// is passed to the ParseFreyja module.
REMOVEFROMFILE = ''
if (params.removeFromFile != '') {
    REMOVEFROMFILE = "--removefromFile \'${params.removeFromFile}\'"
}
println(REMOVEFROMFILE)

// Parses the 'by week' option. If this option is not provided, an empty string
// is passed to the ParseFreyja module.
BYWEEK = ''
if (params.byWeek) {
    BYWEEK = '--byWeek'
}
println(BYWEEK)

// Parses the 'combine all' option. If this option is not provided, an empty string
// is passed to the ParseFreyja module.
COMBINEALL = ''
if (params.combineAll) {
    COMBINEALL = '--combineAll'
}
println(COMBINEALL)

include { RunFreyja } from './modules.nf'
include { ParseFreyja } from './modules.nf'

inputFiles_ch = Channel
    .fromPath("${INDIR}*.bam")
    .ifEmpty { error "No .bam files present in ${INDIR}. Please provide a directory containing .bam files for analysis."}
    .map {it -> [it.getSimpleName(), it]}

demixFiles_ch = Channel
    .fromPath("${params.demixDir}/*.demix")

workflow {
    RunFreyja(inputFiles_ch, REF, BARCODES, params.demixDir, OUTDIR)
    ParseFreyja(FREYJAPARSESCRIPT, "${baseDir}/${params.demixDir}", MASTER, OUTDIR, SUBLIN, REMOVEFROMFILE, BYWEEK, COMBINEALL)
}