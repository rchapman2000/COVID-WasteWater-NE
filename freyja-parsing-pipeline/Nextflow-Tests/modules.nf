process RunFreyja {
    input:
        tuple val(sampleName), file(sampleBam)
        file ref
        file barcodes
        val demixDir
        val outDir

    output:
        tuple val(sampleName), file("${sampleName}.demix")
        file "${sampleName}.demix" into demixFiles_ch
        file "${sampleName}-variants.tsv"
        file "${sampleName}-depths.tsv"

    publishDir "${outDir}/intermediateFiles/", mode: 'copy'
    publishDir "${demixDir}/", pattern:"*.demix", mode: 'copy'

    script:
    """
    #!/bin/bash

    echo ${sampleBam}

    freyja variants ${sampleBam} --variants ${sampleName}-variants.tsv --depths ${sampleName}-depths.tsv --ref ${ref}

    echo "Completed Variants"

    freyja demix ${sampleName}-variants.tsv ${sampleName}-depths.tsv --output ${sampleName}.demix --barcodes ${barcodes}

    """
}

process ParseFreyja {
    input:
        file script
        val demixDir
        file masterSheet
        val outDir
        file sublineageMap
        val removeFromFile
        val byWeek
        val combineAll
    output:
        file "results/"

    publishDir "${outDir}/results", mode: "copy"
    script:
    """
    #!/bin/bash

    mkdir results

    python3 ${script} -i ${demixDir} -o results --sublineageMap ${sublineageMap} --mastersheet ${masterSheet} ${removeFromFile} ${byWeek} ${combineAll}
    """
}