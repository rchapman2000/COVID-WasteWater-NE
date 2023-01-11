setup() {
    load 'test_helper/bats-support/load'
    load 'test_helper/bats-assert/load'

    TESTDIR="$( cd "$( dirname "$BATS_TEST_FILENAME" )" >/dev/null 2>&1 && pwd )"

    PATH="$TESTDIR/../bin:$PATH"

    VALIDINDIR=$TESTDIR/pipeline-test-files/inDir/
    VALIDOUTDIR=$TESTDIR/pipeline-test-files/outDir
    VALIDDEMIXDIR=$TESTDIR/pipeline-test-files/demixDir
    VALIDREF=$TESTDIR/pipeline-test-files/reference-test.fasta
    VALIDMASTER=$TESTDIR/pipeline-test-files/master-test.csv
    VALIDBARCODE=$TESTDIR/pipeline-test-files/barcodes-test.csv
    VALIDCOLLAPSE=$TESTDIR/pipeline-test-files/collapse-test.tsv

    INVALIDDIR=$TESTDIR/invalidDir
    INVALIDFILE=$TESTDIR/invalidfile

    COMPAREDIR=$TESTDIR/pipeline-test-files/Compare-Output
}

@test "Show help message to -h/--help" {
    run freyja-pipeline.sh -h
    assert_output --partial "freyja-pipeline.sh - The purpose of this pipeline is to automate the analysis of wastewater data using freyja."

    run freyja-pipeline.sh --help
    assert_output --partial "freyja-pipeline.sh - The purpose of this pipeline is to automate the analysis of wastewater data using freyja."
}

@test "Show error when no options provided" {
    run freyja-pipeline.sh
    assert_output --partial 'No input directory provided. Please include an input directory (-i/--input)!'
}
@test "Show error when invalid option is provided" {
    # Option 'intput' supplied intead of input
    run freyja-pipeline.sh --intput $VALIDINDIR --output $VALIDOUTDIR --demixDir $VALIDINDIR --reference $VALIDREF --master $VALIDMASTER --barcode $VALIDBARCODE --sublineageMap $VALIDSUBLIN
    assert_output --partial "getopt: unrecognized option '--intput'"
    assert_output --partial "freyja-pipeline.sh - The purpose of this pipeline is to automate the analysis of wastewater data using freyja."

    run freyja-pipeline.sh -q --intput $VALIDINDIR --output $VALIDOUTDIR --demixDir $VALIDINDIR --reference $VALIDREF --master $VALIDMASTER --barcode $VALIDBARCODE --sublineageMap $VALIDSUBLIN
    assert_output --partial "getopt: unrecognized option '-q'"
    assert_output --partial "freyja-pipeline.sh - The purpose of this pipeline is to automate the analysis of wastewater data using freyja."
}

@test "Show error when no input directory provided" {
    run freyja-pipeline.sh --output $VALIDOUTDIR
    assert_output --partial 'No input directory provided. Please include an input directory (-i/--input)!'
}

@test "Show error if non-existent input directory provided" {
    run freyja-pipeline.sh --input $INVALIDDIR
    assert_output --partial "not found. Please include an existing directory (-i/--input)"

    run freyja-pipeline.sh -i $INVALIDDIR
    assert_output --partial "not found. Please include an existing directory (-i/--input)"
}

@test "Show error if no output directory is provided" {
    run freyja-pipeline.sh --input $VALIDINDIR
    assert_output --partial "No output directory provided. Please include an input directory (-o/--output)!"
    
    run freyja-pipeline.sh -i $VALIDINDIR
    assert_output --partial "No output directory provided. Please include an input directory (-o/--output)!"
}

@test "Show error if no demix directory is provided" {
    run freyja-pipeline.sh --input $VALIDINDIR --output $VALIDOUTDIR
    assert_output --partial "No directory to place '.demix' files provided. Please include a directory (-d/--demixDir)!" 

    run freyja-pipeline.sh -i $VALIDINDIR -o $VALIDOUTDIR
    assert_output --partial "No directory to place '.demix' files provided. Please include a directory (-d/--demixDir)!" 
}

@test "Show error if non-existent demix directory is provided" {
    run freyja-pipeline.sh --input $VALIDINDIR --output $VALIDOUTDIR --demixDir $INVALIDDIR
    assert_output --partial "not found. Please include a valid directory to place '.demix' files (-d/--demixDir)!"

    run freyja-pipeline.sh -i $VALIDINDIR -o $VALIDOUTDIR -d $INVALIDDIR
    assert_output --partial "not found. Please include a valid directory to place '.demix' files (-d/--demixDir)!"
}

@test "Show error if no reference file is provided" {
    run freyja-pipeline.sh --input $VALIDINDIR --output $VALIDOUTDIR --demixDir $VALIDINDIR
    assert_output --partial "No reference provided. Please include a reference fasta file (-r/--reference)"

    run freyja-pipeline.sh -i $VALIDINDIR -o $VALIDOUTDIR -d $VALIDINDIR
    assert_output --partial "No reference provided. Please include a reference fasta file (-r/--reference)"
}

@test "Show error if non-existent reference file is provided" {
    run freyja-pipeline.sh --input $VALIDINDIR --output $VALIDOUTDIR --demixDir $VALIDINDIR --reference $INVALIDFILE
    assert_output --partial "does not exist. Please include an existing file and check the path provided (-r/--reference)!"

    run freyja-pipeline.sh -i $VALIDINDIR -o $VALIDOUTDIR -d $VALIDINDIR -r $INVALIDFILE
    assert_output --partial "does not exist. Please include an existing file and check the path provided (-r/--reference)!"
}

@test "Show error if no master file is provided" {
    run freyja-pipeline.sh --input $VALIDINDIR --output $VALIDOUTDIR --demixDir $VALIDINDIR --reference $VALIDREF
    assert_output --partial "No master file provided. Please include a master file (-m/--masterfile)!"

    run freyja-pipeline.sh -i $VALIDINDIR -o $VALIDOUTDIR -d $VALIDINDIR -r $VALIDREF
    assert_output --partial "No master file provided. Please include a master file (-m/--masterfile)!"
}

@test "Show error if non-existent master file is provided" {
    run freyja-pipeline.sh --input $VALIDINDIR --output $VALIDOUTDIR --demixDir $VALIDINDIR --reference $VALIDREF --master $INVALIDFILE
    assert_output --partial "does not exist. Please include an existing file and check the path provided (-m/--mastefile)!"

    run freyja-pipeline.sh -i $VALIDINDIR -o $VALIDOUTDIR -d $VALIDINDIR -r $VALIDREF -m $INVALIDFILE
    assert_output --partial "does not exist. Please include an existing file and check the path provided (-m/--mastefile)!"
}

@test "Show error if no collapse map file is provided" {
    run freyja-pipeline.sh --input $VALIDINDIR --output $VALIDOUTDIR --demixDir $VALIDINDIR --reference $VALIDREF --master $VALIDMASTER --barcode $VALIDBARCODE
    assert_output --partial "No collapse file provided. Please include a sublineage map file (-c/--collapse)"

    run freyja-pipeline.sh -i $VALIDINDIR -o $VALIDOUTDIR -d $VALIDINDIR -r $VALIDREF -m $VALIDMASTER -b $VALIDBARCODE
    assert_output --partial "No collapse file provided. Please include a sublineage map file (-c/--collapse)"
}

@test "Show error if non-existent collapse map file is provided" {
    run freyja-pipeline.sh --input $VALIDINDIR --output $VALIDOUTDIR --demixDir $VALIDINDIR --reference $VALIDREF --master $VALIDMASTER --collapse $INVALIDFILE
    assert_output --partial "does not exist. Please include an existing file and check the path provided (-c/--collapse)!"

    run freyja-pipeline.sh -i $VALIDINDIR -o $VALIDOUTDIR -d $VALIDINDIR -r $VALIDREF -m $VALIDMASTER -c $INVALIDFILE
    assert_output --partial "does not exist. Please include an existing file and check the path provided (-c/--collapse)!"
}

@test "Show error if invalid barcode file is provided" {
    run freyja-pipeline.sh --input $VALIDINDIR --output $VALIDOUTDIR --demixDir $VALIDINDIR --reference $VALIDREF --master $VALIDMASTER --collapse $VALIDCOLLAPSE --barcode $INVALIDFILE
    assert_output --partial "does not exist. Please include an existing file and check the path provided (-b/--barcode)!"

    run freyja-pipeline.sh -i $VALIDINDIR -o $VALIDOUTDIR -d $VALIDINDIR -r $VALIDREF -m $VALIDMASTER -c $VALIDCOLLAPSE -b $INVALIDFILE
    assert_output --partial "does not exist. Please include an existing file and check the path provided (-b/--barcode)!"
}

@test "Show error if both --byDate and --byWeek provided" {
    run freyja-pipeline.sh --input $VALIDINDIR --output $VALIDOUTDIR --demixDir $VALIDINDIR --reference $VALIDREF --master $VALIDMASTER --barcode $VALIDBARCODE --collapse $VALIDCOLLAPSE --byDate --byWeek
    assert_output --partial "Both the --byDate and --byWeek options have been provided. Only one can be supplied."
}

@test "Complete Run: whole-genome, by sample, existing barcodes, with recombinants" {
    run freyja-pipeline.sh --input $VALIDINDIR --output $VALIDOUTDIR --demixDir $VALIDDEMIXDIR --reference $VALIDREF --master $VALIDMASTER --barcode $VALIDBARCODE --collapse $VALIDCOLLAPSE
    [ "$status" -eq 0 ]
    result="$(diff $VALIDOUTDIR/Filtered-dataframe.csv $COMPAREDIR/whole-genome-by-sample-with-recombinants/Filtered-dataframe.csv)"
    result2="$(diff $VALIDOUTDIR/Unfiltered-dataframe.csv $COMPAREDIR/whole-genome-by-sample-with-recombinants/Unfiltered-dataframe.csv)"
    results3="$(diff $VALIDOUTDIR/Site-X-lineageMatrix.csv $COMPAREDIR/whole-genome-by-sample-with-recombinants/Site-X-lineageMatrix.csv)"
    ["$result" -eq ''] 
    ["$result2" -eq '']
    ["$result3" -eq '']
    
    rm -r $VALIDOUTDIR/freyja-results/
    rm -r $VALIDOUTDIR/barcodes-and-collapse/
    rm $VALIDOUTDIR/Filtered-dataframe.csv
    rm $VALIDOUTDIR/Unfiltered-dataframe.csv
    rm $VALIDOUTDIR/Site-X-lineageMatrix.csv
    rm $VALIDDEMIXDIR/Test-Sample.demix
}

@test "Complete Run: whole-genome, by sample, existing barcodes, no recombinants" {
    run freyja-pipeline.sh --input $VALIDINDIR --output $VALIDOUTDIR --demixDir $VALIDDEMIXDIR --reference $VALIDREF --master $VALIDMASTER --barcode $VALIDBARCODE --collapse $VALIDCOLLAPSE --filterRecombinants
    [ "$status" -eq 0 ]
    result="$(diff $VALIDOUTDIR/Filtered-dataframe.csv $COMPAREDIR/whole-genome-by-sample-no-recombinants/Filtered-dataframe.csv)"
    result2="$(diff $VALIDOUTDIR/Unfiltered-dataframe.csv $COMPAREDIR/whole-genome-by-sample-no-recombinants/Unfiltered-dataframe.csv)"
    results3="$(diff $VALIDOUTDIR/Site-X-lineageMatrix.csv $COMPAREDIR/whole-genome-by-sample-no-recombinants/Site-X-lineageMatrix.csv)"
    ["$result" -eq ''] 
    ["$result2" -eq '']
    ["$result3" -eq '']
    
    rm -r $VALIDOUTDIR/freyja-results/
    rm -r $VALIDOUTDIR/barcodes-and-collapse/
    rm $VALIDOUTDIR/Filtered-dataframe.csv
    rm $VALIDOUTDIR/Unfiltered-dataframe.csv
    rm $VALIDOUTDIR/Site-X-lineageMatrix.csv
    rm $VALIDDEMIXDIR/Test-Sample.demix
}

@test "Complete Run: whole-genome, by date, existing barcodes, with recombinants" {
    run freyja-pipeline.sh --input $VALIDINDIR --output $VALIDOUTDIR --demixDir $VALIDDEMIXDIR --reference $VALIDREF --master $VALIDMASTER --barcode $VALIDBARCODE --collapse $VALIDCOLLAPSE --byDate
    [ "$status" -eq 0 ]
    result="$(diff $VALIDOUTDIR/Filtered-dataframe.csv $COMPAREDIR/whole-genome-by-date-with-recombinants/Filtered-dataframe.csv)"
    result2="$(diff $VALIDOUTDIR/Unfiltered-dataframe.csv $COMPAREDIR/whole-genome-by-date-with-recombinants/Unfiltered-dataframe.csv)"
    results3="$(diff $VALIDOUTDIR/Site-X-lineageMatrix.csv $COMPAREDIR/whole-genome-by-date-with-recombinants/Site-X-lineageMatrix.csv)"
    ["$result" -eq '']
    ["$result2" -eq '']
    ["$result3" -eq '']
    
    rm -r $VALIDOUTDIR/freyja-results/
    rm -r $VALIDOUTDIR/barcodes-and-collapse/
    rm $VALIDOUTDIR/Filtered-dataframe.csv
    rm $VALIDOUTDIR/Unfiltered-dataframe.csv
    rm $VALIDOUTDIR/Site-X-lineageMatrix.csv
    rm $VALIDDEMIXDIR/Test-Sample.demix
}

@test "Complete Run: whole-genome, by date, existing barcodes, no recombinants" {
    run freyja-pipeline.sh --input $VALIDINDIR --output $VALIDOUTDIR --demixDir $VALIDDEMIXDIR --reference $VALIDREF --master $VALIDMASTER --barcode $VALIDBARCODE --collapse $VALIDCOLLAPSE --byDate --filterRecombinants 
    [ "$status" -eq 0 ]
    result="$(diff $VALIDOUTDIR/Filtered-dataframe.csv $COMPAREDIR/whole-genome-by-date-no-recombinants/Filtered-dataframe.csv)"
    result2="$(diff $VALIDOUTDIR/Unfiltered-dataframe.csv $COMPAREDIR/whole-genome-by-date-no-recombinants/Unfiltered-dataframe.csv)"
    results3="$(diff $VALIDOUTDIR/Site-X-lineageMatrix.csv $COMPAREDIR/whole-genome-by-date-no-recombinants/Site-X-lineageMatrix.csv)"
    ["$result" -eq '']
    ["$result2" -eq '']
    ["$result3" -eq '']
    
    rm -r $VALIDOUTDIR/freyja-results/
    rm -r $VALIDOUTDIR/barcodes-and-collapse/
    rm $VALIDOUTDIR/Filtered-dataframe.csv
    rm $VALIDOUTDIR/Unfiltered-dataframe.csv
    rm $VALIDOUTDIR/Site-X-lineageMatrix.csv
    rm $VALIDDEMIXDIR/Test-Sample.demix
}

@test "Complete Run: whole-genome, by week, existing barcodes, with recombinants" {
    run freyja-pipeline.sh --input $VALIDINDIR --output $VALIDOUTDIR --demixDir $VALIDDEMIXDIR --reference $VALIDREF --master $VALIDMASTER --barcode $VALIDBARCODE --collapse $VALIDCOLLAPSE --byWeek
    [ "$status" -eq 0 ]
    result="$(diff $VALIDOUTDIR/Filtered-dataframe.csv $COMPAREDIR/whole-genome-by-week-with-recombinants/Filtered-dataframe.csv)"
    result2="$(diff $VALIDOUTDIR/Unfiltered-dataframe.csv $COMPAREDIR/whole-genome-by-week-with-recombinants/Unfiltered-dataframe.csv)"
    results3="$(diff $VALIDOUTDIR/Site-X-lineageMatrix.csv $COMPAREDIR/whole-genome-by-week-with-recombinants/Site-X-lineageMatrix.csv)"
    ["$result" -eq '']
    ["$result2" -eq '']
    ["$result3" -eq '']
    
    rm -r $VALIDOUTDIR/freyja-results/
    rm -r $VALIDOUTDIR/barcodes-and-collapse/
    rm $VALIDOUTDIR/Filtered-dataframe.csv
    rm $VALIDOUTDIR/Unfiltered-dataframe.csv
    rm $VALIDOUTDIR/Site-X-lineageMatrix.csv
    rm $VALIDDEMIXDIR/Test-Sample.demix
}

@test "Complete Run: whole-genome, by week, existing barcodes, no recombinants" {
    run freyja-pipeline.sh --input $VALIDINDIR --output $VALIDOUTDIR --demixDir $VALIDDEMIXDIR --reference $VALIDREF --master $VALIDMASTER --barcode $VALIDBARCODE --collapse $VALIDCOLLAPSE --byWeek --filterRecombinants
    [ "$status" -eq 0 ]
    result="$(diff $VALIDOUTDIR/Filtered-dataframe.csv $COMPAREDIR/whole-genome-by-week-no-recombinants/Filtered-dataframe.csv)"
    result2="$(diff $VALIDOUTDIR/Unfiltered-dataframe.csv $COMPAREDIR/whole-genome-by-week-no-recombinants/Unfiltered-dataframe.csv)"
    results3="$(diff $VALIDOUTDIR/Site-X-lineageMatrix.csv $COMPAREDIR/whole-genome-by-week-no-recombinants/Site-X-lineageMatrix.csv)"
    ["$result" -eq '']
    ["$result2" -eq '']
    ["$result3" -eq '']
    
    rm -r $VALIDOUTDIR/freyja-results/
    rm -r $VALIDOUTDIR/barcodes-and-collapse/
    rm $VALIDOUTDIR/Filtered-dataframe.csv
    rm $VALIDOUTDIR/Unfiltered-dataframe.csv
    rm $VALIDOUTDIR/Site-X-lineageMatrix.csv
    rm $VALIDDEMIXDIR/Test-Sample.demix
}

@test "Complete Run: s-gene, by sample, existing barcodes, with recombinants" {
    run freyja-pipeline.sh --input $VALIDINDIR --output $VALIDOUTDIR --demixDir $VALIDDEMIXDIR --reference $VALIDREF --master $VALIDMASTER --barcode $VALIDBARCODE --collapse $VALIDCOLLAPSE --s_gene
    [ "$status" -eq 0 ]
    result="$(diff $VALIDOUTDIR/Filtered-dataframe.csv $COMPAREDIR/s-gene-by-sample-with-recombinants/Filtered-dataframe.csv)"
    result2="$(diff $VALIDOUTDIR/Unfiltered-dataframe.csv $COMPAREDIR/s-gene-by-sample-with-recombinants/Unfiltered-dataframe.csv)"
    results3="$(diff $VALIDOUTDIR/Site-X-lineageMatrix.csv $COMPAREDIR/s-gene-by-sample-with-recombinants/Site-X-lineageMatrix.csv)"
    ["$result" -eq ''] 
    ["$result2" -eq '']
    ["$result3" -eq '']
    
    rm -r $VALIDOUTDIR/freyja-results/
    rm -r $VALIDOUTDIR/barcodes-and-collapse/
    rm $VALIDOUTDIR/Filtered-dataframe.csv
    rm $VALIDOUTDIR/Unfiltered-dataframe.csv
    rm $VALIDOUTDIR/Site-X-lineageMatrix.csv
    rm $VALIDDEMIXDIR/Test-Sample.demix
}

@test "Complete Run: s-gene, by sample, existing barcodes, no recombinants" {
    run freyja-pipeline.sh --input $VALIDINDIR --output $VALIDOUTDIR --demixDir $VALIDDEMIXDIR --reference $VALIDREF --master $VALIDMASTER --barcode $VALIDBARCODE --collapse $VALIDCOLLAPSE --s_gene --filterRecombinants
    [ "$status" -eq 0 ]
    result="$(diff $VALIDOUTDIR/Filtered-dataframe.csv $COMPAREDIR/s-gene-by-sample-no-recombinants/Filtered-dataframe.csv)"
    result2="$(diff $VALIDOUTDIR/Unfiltered-dataframe.csv $COMPAREDIR/s-gene-by-sample-no-recombinants/Unfiltered-dataframe.csv)"
    results3="$(diff $VALIDOUTDIR/Site-X-lineageMatrix.csv $COMPAREDIR/s-gene-by-sample-no-recombinants/Site-X-lineageMatrix.csv)"
    ["$result" -eq ''] 
    ["$result2" -eq '']
    ["$result3" -eq '']
    
    rm -r $VALIDOUTDIR/freyja-results/
    rm -r $VALIDOUTDIR/barcodes-and-collapse/
    rm $VALIDOUTDIR/Filtered-dataframe.csv
    rm $VALIDOUTDIR/Unfiltered-dataframe.csv
    rm $VALIDOUTDIR/Site-X-lineageMatrix.csv
    rm $VALIDDEMIXDIR/Test-Sample.demix
}

@test "Complete Run: s-gene, by date, existing barcodes, with recombinants" {
    run freyja-pipeline.sh --input $VALIDINDIR --output $VALIDOUTDIR --demixDir $VALIDDEMIXDIR --reference $VALIDREF --master $VALIDMASTER --barcode $VALIDBARCODE --collapse $VALIDCOLLAPSE --s_gene --byDate 
    [ "$status" -eq 0 ]
    result="$(diff $VALIDOUTDIR/Filtered-dataframe.csv $COMPAREDIR/s-gene-by-date-with-recombinants/Filtered-dataframe.csv)"
    result2="$(diff $VALIDOUTDIR/Unfiltered-dataframe.csv $COMPAREDIR/s-gene-by-date-with-recombinants/Unfiltered-dataframe.csv)"
    results3="$(diff $VALIDOUTDIR/Site-X-lineageMatrix.csv $COMPAREDIR/s-gene-by-date-with-recombinants/Site-X-lineageMatrix.csv)"
    ["$result" -eq '']
    ["$result2" -eq '']
    ["$result3" -eq '']
    
    rm -r $VALIDOUTDIR/freyja-results/
    rm -r $VALIDOUTDIR/barcodes-and-collapse/
    rm $VALIDOUTDIR/Filtered-dataframe.csv
    rm $VALIDOUTDIR/Unfiltered-dataframe.csv
    rm $VALIDOUTDIR/Site-X-lineageMatrix.csv
    rm $VALIDDEMIXDIR/Test-Sample.demix
}

@test "Complete Run: s-gene, by date, existing barcodes, no recombinants" {
    run freyja-pipeline.sh --input $VALIDINDIR --output $VALIDOUTDIR --demixDir $VALIDDEMIXDIR --reference $VALIDREF --master $VALIDMASTER --barcode $VALIDBARCODE --collapse $VALIDCOLLAPSE --s_gene --byDate --filterRecombinants
    [ "$status" -eq 0 ]
    result="$(diff $VALIDOUTDIR/Filtered-dataframe.csv $COMPAREDIR/s-gene-by-date-no-recombinants/Filtered-dataframe.csv)"
    result2="$(diff $VALIDOUTDIR/Unfiltered-dataframe.csv $COMPAREDIR/s-gene-by-date-no-recombinants/Unfiltered-dataframe.csv)"
    results3="$(diff $VALIDOUTDIR/Site-X-lineageMatrix.csv $COMPAREDIR/s-gene-by-date-no-recombinants/Site-X-lineageMatrix.csv)"
    ["$result" -eq '']
    ["$result2" -eq '']
    ["$result3" -eq '']
    
    rm -r $VALIDOUTDIR/freyja-results/
    rm -r $VALIDOUTDIR/barcodes-and-collapse/
    rm $VALIDOUTDIR/Filtered-dataframe.csv
    rm $VALIDOUTDIR/Unfiltered-dataframe.csv
    rm $VALIDOUTDIR/Site-X-lineageMatrix.csv
    rm $VALIDDEMIXDIR/Test-Sample.demix
}

@test "Complete Run: s-gene, by week, existing barcodes, with recombinants" {
    run freyja-pipeline.sh --input $VALIDINDIR --output $VALIDOUTDIR --demixDir $VALIDDEMIXDIR --reference $VALIDREF --master $VALIDMASTER --barcode $VALIDBARCODE --collapse $VALIDCOLLAPSE --s_gene --byWeek 
    [ "$status" -eq 0 ]
    result="$(diff $VALIDOUTDIR/Filtered-dataframe.csv $COMPAREDIR/s-gene-by-week-with-recombinants/Filtered-dataframe.csv)"
    result2="$(diff $VALIDOUTDIR/Unfiltered-dataframe.csv $COMPAREDIR/s-gene-by-week-with-recombinants/Unfiltered-dataframe.csv)"
    results3="$(diff $VALIDOUTDIR/Site-X-lineageMatrix.csv $COMPAREDIR/s-gene-by-week-with-recombinants/Site-X-lineageMatrix.csv)"
    ["$result" -eq '']
    ["$result2" -eq '']
    ["$result3" -eq '']
    
    rm -r $VALIDOUTDIR/freyja-results/
    rm -r $VALIDOUTDIR/barcodes-and-collapse/
    rm $VALIDOUTDIR/Filtered-dataframe.csv
    rm $VALIDOUTDIR/Unfiltered-dataframe.csv
    rm $VALIDOUTDIR/Site-X-lineageMatrix.csv
    rm $VALIDDEMIXDIR/Test-Sample.demix
}

@test "Complete Run: s-gene, by week, existing barcodes, no recombinants" {
    run freyja-pipeline.sh --input $VALIDINDIR --output $VALIDOUTDIR --demixDir $VALIDDEMIXDIR --reference $VALIDREF --master $VALIDMASTER --barcode $VALIDBARCODE --collapse $VALIDCOLLAPSE --s_gene --byWeek --filterRecombinants
    [ "$status" -eq 0 ]
    result="$(diff $VALIDOUTDIR/Filtered-dataframe.csv $COMPAREDIR/s-gene-by-week-no-recombinants/Filtered-dataframe.csv)"
    result2="$(diff $VALIDOUTDIR/Unfiltered-dataframe.csv $COMPAREDIR/s-gene-by-week-no-recombinants/Unfiltered-dataframe.csv)"
    results3="$(diff $VALIDOUTDIR/Site-X-lineageMatrix.csv $COMPAREDIR/s-gene-by-week-no-recombinants/Site-X-lineageMatrix.csv)"
    ["$result" -eq '']
    ["$result2" -eq '']
    ["$result3" -eq '']
    
    rm -r $VALIDOUTDIR/freyja-results/
    rm -r $VALIDOUTDIR/barcodes-and-collapse/
    rm $VALIDOUTDIR/Filtered-dataframe.csv
    rm $VALIDOUTDIR/Unfiltered-dataframe.csv
    rm $VALIDOUTDIR/Site-X-lineageMatrix.csv
    rm $VALIDDEMIXDIR/Test-Sample.demix
}


