import sys
import os
import argparse
import pandas as pd
import subprocess as sp
from utilities import parseCSVToDF, parseDirectory

def getMutPos(m):
    """ Calculate and returns the position of the mutation
    
    Parameters:
        m: a mutation in the format "A#####T"

    Output:
        The integer position of the mutation.
    """
    return int(m[1:len(m) - 1])

def runFreyjaUpdate(o):
    """ Runs the Freyja update module to download the most
    up-to-date set of barcodes.

    Parameters:
        o: a path to output the files from the module

    Output: 
        None
    """
    cmd = "freyja update --outdir {0}".format(o)
    sp.run(cmd, check=True, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
    

def main():
    parser = argparse.ArgumentParser(usage = "TO BE ADDED")

    parser.add_argument("-i", "--input", required = False, type=str, \
        help="File containing USHER Barcodes to be filtered. If not provided, 'freyja update' will automatically be run and the output barcodes will be used.", \
        action = 'store', dest = 'infile')
    parser.add_argument("-o", "--outdir", required = True, type=str, \
        help='[Required] - directory to place output files', \
        action = 'store', dest = 'outdir')
    parser.add_argument("--noFilter", required= False, \
        help = "This script automatically removes proposed, misc, and hybrid lineages (X#). Supply this option if you wish for these to be included", \
        action = 'store_true', dest = 'noFilt')

    args = parser.parse_args()

    # Parses the output directory inputted by the user
    outdir = parseDirectory(args.outdir)


    df = ''
    if args.infile:

        # If the user supplied the input file to use, parse that file into 
        # a pandas dataframe and notify the user.
        df = parseCSVToDF(args.infile, ',', header=True)
        print("Input file, {0}, provided. Freyja update will not be run and this file will be used insteadd.".format(args.infile))
    else:
        # If the user did not supply an input file, run 'freyja update' and read the barcode in
        # as a pandas dataframe. 
        print("Fetching latest barcodes using 'freyja update'")
        runFreyjaUpdate(outdir)
        barcodes = outdir + "usher_barcodes.csv"
        df = parseCSVToDF(barcodes, ',', header=True)
    
    # If the user supplied the --noFilter option, skip filtering.
    if not args.noFilt:
        # Filter the barcodes to removed any proposed lineages,
        # misc lineages, and hybrid lineages (X#)
        filterProposed = df.iloc[:,0].str.contains("proposed\d+")
        df = df[~filterProposed]
        filterMisc = df.iloc[:,0].str.contains("misc.*")
        df = df[~filterMisc]
        filterRecombinant = df.iloc[:,0].str.contains("X.*")
        df = df[~filterRecombinant]
        df.iloc[:,0] = df.iloc[:,0].str.replace(" ", '')
    
    # Sets the index to the first column which contains
    # lineages names
    df = df.set_index('Unnamed: 0')

    # Saves the start and end positions of the SARS-CoV-2 S gene
    s_gene_start = 21563
    s_gene_end = 25384

    # Loops over each column in the barcode file, which represents a
    # mutation. Removes the mutations outside of the s gene.
    for column in df:
        
        # Skips the first column which contains the variant names
        if column != "Unnamed: 0":
            
            # Grabs the mutation position from the column.
            pos = getMutPos(column)
            
            # Drops the column if the mutation position is outside
            # of the s gene.
            if pos < s_gene_start or pos > s_gene_end:
                df = df.drop(column, axis=1) 
    

    # Writes a csv that contains the barcodes before identical rows are combined. 
    df.to_csv("{0}S_Gene_Unfiltered.csv".format(outdir))

    # Places all of the columns in the dataframe into a list
    cols = df.columns.values.tolist()

    # Uses pandas' groupby function to great groups of rows based on having matching columns.
    # Essentially, this creates groups of variants with the same mutation profiles.
    dup_grouped = df.groupby(cols)
    dup_groups = dup_grouped.groups

    # Creates a human-readable file that contains the lineage groupings
    # and their common mutation profile.
    groupFile = open("{0}LineageGroups.txt".format(outdir), "w+")
    
    # Creates a new dataframe to store the combined lineages and their mutation profiles
    newCols = cols
    newCols.insert(0, '')
    newdf = pd.DataFrame(columns=newCols)

    # Loops over all of the groups produced by the groupby
    # function to combine them into 1 entry in the new dataframe
    for grp in dup_groups.keys():

        # Grabs the individual variants from the group
        rows = dup_groups[grp].values

        # Grabs the columns where the variants have a 1. This indicates 
        # that the variant has a given mutation 
        muts = df.columns[df.loc[rows[0],:].isin([1])].values

        # Writes the variants and mutations for into the text file
        groupFile.write("Variants: {0}\n".format(", ".join(rows)))
        groupFile.write("Mutations: {0}\n\n".format(", ".join(muts)))
        
        # If there is more than 1 variant in the group, the entry in
        # the new dataframe for this group is a concatenation of the
        # variants in the group separated by pipe characters.
        if len(rows) > 1:
            clade = "|".join(rows)
        else:
            clade = rows[0]    

        # Grabs the entire row for one of the variants in the group from the original dataframe
        # (since they are all the same within the group, we can just grab the first one).
        barcodes = df.loc[rows[0],:].values.tolist()

        # Adds the row into the new dataframe.
        barcodes.insert(0, clade)
        newdf.loc[len(newdf.index)] = barcodes

    # Writes the dataframe to a csv and closes the text filestream.
    newdf.to_csv("{0}S_Gene_barcodes.csv".format(outdir), index=False)
    groupFile.close()

if __name__ == "__main__":
    main()
