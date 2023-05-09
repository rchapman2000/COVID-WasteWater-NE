import sys
import os
import argparse
import data_manip_utils

def sortByCoordinate(l):
    """ A version of merge sort coded to sort a list of mutations by
    their coordinates.

    Parameters:
        l - a list of mutations to be sorted
    """

    # First, check whether the length of the list is
    # greater than 1. If the list is of length 1, then it
    # is already sorted.
    if len(l) > 1:
        # If yes, find the midpoint of the
        # list and create two separate lists
        # containing the items that come
        # before of after the midpoint (to the left
        # or to the right, visually)
        midpoint = len(l)//2
        left = l[:midpoint]
        right = l[midpoint:]

        # Next, recursively call the function to sort
        # the left and right sides of the current list
        left = sortByCoordinate(left)
        right = sortByCoordinate(right)

        # Once the left and right lists have been
        # sorted, we now need to combine the
        # two while sorting.

        # Create integer varables to keep
        # track of our position in the left,
        # right, and master lists.
        leftPos = rightPos = mainPos = 0

        # Next we will loop over both the left and right
        # list, adding items to the main list based on which should
        # come first. (This works since both the left and right lists
        # are already sorted).
        while leftPos < len(left) and rightPos < len(right):
            
            # Check if the mutation at the current position in the left list should come
            # before the mutation at the current position in the right list (i.e. the coordinate
            # of the mutation from the left list is less than the coordinate of
            # the mutation in the right list) 
            if data_manip_utils.getMutationCoords(left[leftPos]) < data_manip_utils.getMutationCoords(right[rightPos]):
                # If so, then mutation from the left list should come first. Add it to the master list
                # and increment the position in the left list.
                l[mainPos] = left[leftPos]
                leftPos += 1
            else:
                # If not, then the mutation in the right list should come first. Add 
                # it to the master list and increment position in the right list.
                l[mainPos] = right[rightPos]
                rightPos +=1
            
            # Increment the position in the master list.
            mainPos += 1
        
        # At this point, all of the mutations from either the left
        # or the right list have been added, so we simply need to add the 
        # remaining mutations in their current order (because the left and 
        # right lists were already sorted).

        # If the current position in the left list is less than the length
        # of that list, then it must have elements remaining.
        while leftPos < len(left):
            # Add the mutation at the current left position to the main list
            # and increment both current positions
            l[mainPos] = left[leftPos]
            mainPos += 1
            leftPos +=1

        # If the current position in the right list is less than the length
        # of that list, then it must have elements remaining.
        while rightPos < len(right):
            # Add the mutation at the current right position to the main list
            # and increment both current positions
            l[mainPos] = right[rightPos]
            mainPos += 1
            rightPos += 1
    
    # Return the list
    return l

def getUniqueMutations(l, mutProfs):
    """ For a provided organism, identifies unique mutations 
    for this organism compared to others in set of mutation profiles.

    In this case, we define unique mutations as those that are only
    found in the mutation profile of the given lineage when compared to a
    set of other lineages. 

    Parameters:
        l - the lineage for which to identify unique
        otherLists - A dictionary linking lineages to their corresponding mutation
                     profiles.
    """
    # Store the lineage's mutation profile
    # in a new list.
    uniqueMuts = mutProfs[l]

    # Loop over the lineages in the mutation profile 
    # dictionary
    for k in mutProfs.keys():

        # Check that the current lineage in the loop
        # is not the desired lineage. 
        if k != l:
            # If not, subtract the mutations from the other
            # lineages profile from the desired lineages mutations
            # using set datatypes.
            uniqueMuts = set(uniqueMuts) - set(mutProfs[k])

    # Return the remaining list, which should now
    # contain only unique items.
    return list(uniqueMuts)
    

def getDefiningMutations(l, mutProfs):
    """ For a provided organism, identifies defining mutations 
    for this organism compared to others in set of mutation profiles.

    In this case, we define "defining mutations" as all mutations that can be used 
    to distinguish the desired lineage from a set of other lineages. 
    We can find this list by identifying the list of mutations found only in the
    desired lineage for each other lineage in the set. By adding these mutations together and 
    taking the list of unique mutations, we end up with the combination of mutations 
    that distinguishes the lineage from the others. 

    Parameters:
        l - the lineage for which to identify unique
        otherLists - A dictionary linking lineages to their corresponding mutation
                     profiles.
    """
    # Create an empty list to store the defining mutations
    definingMuts = []

    # Loop over the lineages in the mutation profiles 
    # dictionary
    for k in mutProfs.keys():
        # Check that the current lineage in the loop
        # is not the desired lineage. 
        if k != l:
            # If not, to the list of defining mutations, add all the mutations found
            # in the desired lineage but not the current lineage
            definingMuts.extend(list(set(mutProfs[l]) - set(mutProfs[k])))

    # After adding all of the mutations, there are likely duplicate
    # mutations in the list. Thus, we remove duplicate values in the list by
    # converting to a set, and then converting back to a list.
    return list(set(definingMuts))


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

    # Creates a text file to store complete mutation profiles and
    # unique mutations for each lineage (if multiple were supplied)
    outMuts = open("{0}-mutations.txt".format(args.outpref), "w+")
    outMuts.write("Complete Mutation Profiles:\n\n")

    # Additionally, because S gene barcodes may be specified, the lineages
    # provided by a user may be part of an S gene identical group. Thus,
    # we also create a summary file to store information about the lineage's
    # group and what other lineages fall within that group.
    outSummary = open("{0}-summary.txt".format(args.outpref), "w+")

    mutProfs = {}

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
            sortedMuts = sortByCoordinate(mutations)
            # If the mutation profile has been set, we can output an entry into the summary file and
            # the mutation csv file.
            outSummary.write("{0}\nS-Gene Identical Group: {1}\nLineages in Group: {2}\nMutations: {3}\n\n".format(l, LinGroup, LinsInGroup, ", ".join(sortedMuts)))
            outMuts.write(l + ": " + ",".join(sortedMuts) + "\n")

            # Add the mutations to the mutation profile 
            # dictionary
            mutProfs[l] = sortedMuts

    # If the user supplied for than 1 lineage that was found within
    # the barcodes, then the we can also collect the unique and defining
    # mutations of each to make the output more useful.
    if len(mutProfs.keys()) > 1:
        
        # Write a header for the unique mutations ot the output file
        outMuts.write("\n\nUnique Mutations Between Lineages:\n\n")

        # Loop over each lineage in the mutation profile dictionary
        for l in mutProfs.keys():
            # Find the unique mutations for that lineage and then
            # sort them my coordinate position
            uniqueMuts = sortByCoordinate(getUniqueMutations(l, mutProfs))

            # Write the sorted, unique mutations to the output file.
            outMuts.write("{0}: {1}\n".format(l, ",".join(uniqueMuts)))

        # Write a header for the defining mutations to the output file
        outMuts.write("\n\nDefining Mutations of Each Lineage:\n\n")

        # Loop over each lineage in the mutation profile dictionary
        for l in mutProfs.keys():
            # Find the defining mutations for that lineage and then
            # sort them by coordinate position
            definingMuts = sortByCoordinate(getDefiningMutations(l, mutProfs))

            # Write the sorted, defining mutations to the output file
            outMuts.write("{0}: {1}\n".format(l, ",".join(definingMuts)))
        

    # Close the output files.
    outMuts.close()
    outSummary.close()

if __name__ == "__main__":
    main()
