import sys
import os
import argparse
import data_manip_utils

def main():

    # Creates an argument parser and defines the possible arguments
    # that can be taken.
    parser = argparse.ArgumentParser(usage = "Grab Mutation Profile - can be used to identify mutation profiles for various lineages")

    parser.add_argument("-l", "--lineages", required = True, type=str, \
        help="[Required] - A list of lineages to identify mutation profiles for. Separate lineages by commas (Ex: BA.1,BA.2,BA.3)", \
        action = 'store', dest = 'lins')
    parser.add_argument('-s', '--sublineageMap', required = True, type = str, \
        help = '[Required] - File containing mappings to sublineages to parent lineages', \
        action = 'store', dest = 'sublin')
    parser.add_argument("-b", "--barcodes", required = True, type=str, \
        help="[Required] - Barcode file containing mutation profiles to be searched.", \
        action = 'store', dest = 'barcodes')
    parser.add_argument("-o", "--outpref", required = True, type=str, \
        help="[Required] - Prefix to append to output files", action = 'store', dest="outpref")

    # Parses the arguments provided by the user
    args = parser.parse_args()

    # Parses the lineage(s) that the user provided.
    lins = args.lins.split(",")
    if len(lins) == 0:
        sys.exit("ERROR: Please provide one or more lineages separated by commas")

    # Reads in the sublineage map into a dictionary.
    sublinMap = data_manip_utils.parseSublinMap(args.sublin)
    
    # Parses the provided barcodes into a pandas dataframe and sets the index
    # to the first column (containing the lineage/lineage group name)
    barcodes = data_manip_utils.parseCSVToDF(args.barcodes, ",", True)
    barcodes = barcodes.set_index('Unnamed: 0')

    # Creates a csv file to store mutation profiles
    outCSV = open("{0}-mutations.csv".format(args.outpref), "w+")

    # Additionally, because S gene barcodes may be specified, the lineages
    # provided by a user may be part of an S gene identical group. Thus,
    # we also create a summary file to store information about the lineage's
    # group and what other lineages fall within that group.
    outSummary = open("{0}-summary.txt".format(args.outpref), "w+")

    # Loops over the list of lineages provided by the user.
    for l in lins:
        
        # Creates empty variants to store the lineage's mutation
        # profile.
        mutations = []

        # Creates empty variables to store the lineage's S gene
        # identical group (if it is part of one) and any other lineages
        # that are part of that group.
        LinGroup = None
        LinsInGroup = None

        # Checks whether the lineage is present in the barcode file's index
        if l in barcodes.index:
            # If so, this means that the lineage is not part of any
            # s-gene identical group, and we can grab the mutation profile
            # directory.
            mutations = list(barcodes.columns[barcodes.loc[l,:].isin([1])].values)
            
            # Sets the lineage group and lineages in group variables to "None"
            LinGroup = "Unique From other Lineage in the S gene"
            LinsInGroup = "N/A"
        else:
            # If the lineage is not found in the barcode file's index,
            # it may be part of an S gene identical group (and thus the group may be
            # listed in the index). Thus, we can check for this by using the sublineage map.

            # Loops over the groups in the sublineage map
            for g in sublinMap.keys():
                # Checks whether the lineage is
                # found within the group.
                if l in sublinMap[g][1]:
                    # If so, update the lineage group and lineages in group
                    # variable and break from the loop to prevent unnecessary comparisons.
                    LinGroup = g
                    LinsInGroup = sublinMap[g][1]
                    break

            # Checks whether the lineage was found in any groups and whether this 
            # group exists in the barcode file supplied.
            if LinGroup != None and LinGroup in barcodes.index:
                # If so, grab the list of mutations for that group
                mutations = list(barcodes.columns[barcodes.loc[LinGroup,:].isin([1])].values)
            # If no group containing the lineage was found or the lineage group does not 
            # exist within the barcodes, then we cannot output any mutations. Thus, this 
            # variable is left as 'None'
            else:
                mutations = None
        
        # Finally, if the mutation profile has been set to None, then we can make a note in the summary file
        # that the lineage was not found in the barcodes or in an S-gene identical group
        if mutations == None:
            outSummary.write("Lineage {0} not found in barcodes or in an S-gene identical group.\n\n".format(l))
        else:
            # If the mutation profile has been set, we can output an entry into the summary file and
            # the mutation csv file.
            outSummary.write("{0}\nS-Gene Identical Group: {1}\nLineages in Group: {2}\nMutations: {3}\n\n".format(l, LinGroup, LinsInGroup, ", ".join(mutations)))
            outCSV.write(l + "," + ",".join(mutations) + "\n")

    # Close the output files.
    outCSV.close()
    outSummary.close()

if __name__ == "__main__":
    main()
