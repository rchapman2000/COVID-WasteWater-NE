from distutils.command import build
import sys
import os
import argparse
import pandas as pd
import subprocess as sp
from treelib import Node, Tree
import urllib.request as ur
import json
import re
from data_manip_utils import parseCSVToDF, parseDirectory
from tree_utils import addLineagesToTree, addWithdrawnLineagesToTree, checkLineageExists, getCommonLineageParent, getSubLineages, parseParentFromLineage

def parseCladeName(tree, clade):
    """ The nextstrain clades pulled from the USHER phylogenetic
    tree (and subsequently used in the barcodes) are in the format:

        ##[A-Z](INFO)

    The clade names pulled from the nextstrain data are in a slightly different
    format:

        ##[A-Z] (INFO,equivalentLineage)

    Thus, we must parse these names to retrieve the equivalent lineage as well as
    to match the barcode clade name.

    This function takes the clade name, separates the clade number from the information,
    parses the information to obtain the equivalent lineage, and reassembles the clade name
    with the other information.

    There are also several cases that we must consider when processing:
        1. When there is no info given for a clade (Ex: 20C), we will
        set the equivalent lineage to 'None', and this clade will be associated with its
        parent based on the nextstrain clade file.

        2. When there is no lineage given, but information given (Ex: 21J (Delta)), we will
        set the equivalent lienage to 'None', concatenate the information with the clade name,
        and associate the clade with its parent based on the nextstrain clade file.


    Parameters:
        tree: a tree containing pango lineages
        clade: the clade name pulled from the nextstrain clade file.

    Output:
        The corrected clade name and the equivalent pango lineage.
    """

    # This function will use regex capture groups to grab the clade number 
    # and information in separate objects.
    cladePattern = '^(\d\d\w) ?(?=\((.*)\))?'
    
    # Creates empty variables to store the corrected clade name
    # and associated lineage.
    correctedCladeName = ''
    pangoLineage = ''
    
    # Performs a regex match function with the clade pattern 
    # and the provided clade name.
    result = re.match(cladePattern, clade)

    if result:
        # If the regex pattern found a match,
        # we can then parse the information.

        # For a case like '20C', there will be no information. Thus, the second capture group
        # will be "None"
        if result.group(2) == None:
            # Set the clade name to be the first capture group.
            correctedCladeName = result.group(1)
            # Set the pango lineage to be None.
            pangoLineage = None
        # For other cases, there will be information, and then we need to parse that data.
        else:

            # The clade number will be the first capture group.
            cladeNum = result.group(1)

            # The information will be the second capture group.
            # In some cases there was a '~' character, and this can be removed.
            # As well, the information can contain multiple values separated by ', '.
            # Thus, an easy way to parse this data is to split these values at the 
            # delimiters.
            extraInfo = result.group(2).replace("~", "").split(", ")

            # If the length of the information array is 1, then the data value
            # is either the equivalent variant or information like "Delta"
            if len(extraInfo) == 1:
                
                # If the only value in the information is not an existing lineage
                # on the tree, then this must be some information included in the clade
                # name (like "Delta")
                if checkLineageExists(tree, extraInfo[0]) == False:

                    # Add the information to the clade name
                    correctedCladeName = "{0}({1})".format(cladeNum, extraInfo[0])

                    # We do not need to set the pango lineage to "None" here because the check 
                    # for the lineage existing at the end of this method will set it then. As well, setting
                    # the lineage to 'None' here will cause an error at that step.
                
                # If the value is an existing lineage, set he clade name to be the clade
                # number only, and set the pango lineage to be the value from the information.
                else:
                    correctedCladeName = cladeNum
                    pangoLineage = extraInfo[0]

            # If the information contains two or more values, then the final value will be
            # the equivalent lineage, and the values up until that will need to be included
            # in the clade name.
            else:
                
                # Set the pangoLineage equial to the last value in the information
                pangoLineage = extraInfo[-1]

                # Create the corrected clade name by concatenating the clade number
                # with the information fields separated by commands
                correctedCladeName = "{0}({1})".format(cladeNum, ",".join(extraInfo[:-1]))

            # There is one case where the lineage contains a '/' (21C (Epsilon, B.1.427/429)).
            # Because we only need to place the clade under one lineage, we can just remove the '/429'
            # from the lineage and be okay.
            if "/" in pangoLineage:
                
                #Splits the lienage at the '/' and only grabs the first value in the split array (B.1.427)
                pangoLineage = pangoLineage.split("/")[0]

            # Some final cases to be wary of are if the equivalent lineage has been withdrawn (will not exist)
            # or is somehow non existent from earlier checks.
            if checkLineageExists(tree, pangoLineage) == False:

                # If the lineage does not exist, set the pango lineage to "None"
                pangoLineage = None

        # Returns the corrected clade name and equivalent pango lineage
        return correctedCladeName, pangoLineage
    else:

        # If the regex pattern does not find anything. This statement exits the script, as
        # it will no longer work.
        print("Error in parsing Nextstrain clade file")
        exit(0)


def parseNSCladeFile(tree, clade):
    """ The barcodes created by freyja include mutation profiles of the nextstrain clades.
    Thus, we need to find some way of adding these to the tree to include them in collapsing
    and grouping. Nextstain has a github repo with the phylogenetic relationships of these
    clades which we can parse in order to place them on the tree.

    In the raw data, each clade contains a list of children. Thus, this method acts recursively
    to parse the child clades.

    Parameters:
        tree: a tree containing pango lineages
        clade: a dictionary containing name and children for a given clade

    Output:
        A dictionary containing parsed clade name(s) as a key
        mapping to corresponding parent libneage(s)
    """

    # Create an empty dictionary. The dictionary will contain
    # keys that represent clades mapped to values representing their
    # corresponding lineage. This will be used to placed the clade
    # on the tree under that lineage.
    cladeRelationships = {}

    # The name field of a clade in the raw data contains the
    # corresponding lineage (if one exists). Thus, we must extract
    # this from the name 
    cladeName, pangoLineage = parseCladeName(tree, clade['name'])

    # If the lineage has children, we need to parse those children and 
    # append the data to dictionary
    if 'children' in clade.keys():
        # Parses each child and updates the dictionary to 
        # contain the results.
        for child in clade['children']:
             cladeRelationships.update(parseNSCladeFile(tree, child))
        
        # If there is no lineage associated with the child clade, a None
        # value is returned from the parseCladeName function.
        # We need to place the child under the current clade.
        for x in cladeRelationships.keys():
            if cladeRelationships[x] == None:
                cladeRelationships[x] = cladeName
    
    # Adds the current clade to the dictionary and associates it with
    # the corresponding pango lineage.
    cladeRelationships[cladeName] = pangoLineage

    # Returns the dictionary.
    return cladeRelationships

def buildLineageTree(outdir):
    """ Builds a tree data structure containing SARS-CoV-2 lineages.
    This is useful when creating the groups to collapse the individual sublineages
    into as well as when combining groups that have identical S-gene profiles.

    A tree data structure consists of individual nodes which map to children.

    Parameters:
        outdir - the output directory. Data files will be
                 written here

    Output:
        A tree containing SARS-CoV-2 lineages
    """

    # Most lineages are obtained from the pango-designation github. This data source is
    # updated frequently with new lineages and updates to existing lineages.
    #
    # Each line of the data file contains a lineage and description separated by a tab character.
    # The file also contains withdrawn lineages (Beginning with a '*' character) which are useful for our pipeline as 
    # previously classified lineages may have been withdrawn. By mapping these withdrawn
    # lineages we can be sure that the older data does not need to be rerun.
    LineageUrl = "https://raw.githubusercontent.com/cov-lineages/pango-designation/master/lineage_notes.txt"
    ur.urlretrieve(LineageUrl, outdir + "lineages.txt")

    # Lineages are named in a hierarchical manner (i.e B is the parent of B.1, and so on). However, when
    # a name would contain more than 3 numbers (4 characters), it is aliased to shorten it (Ex: BA.1 = B.1.1.529.1).
    # Thus, this is something we need to take into account when placing lineages on the tree.
    #
    # The pango-designation github contains an alias key file which maps aliases to their corresponding lineage.
    AliasUrl = "https://raw.githubusercontent.com/cov-lineages/pango-designation/master/pango_designation/alias_key.json"
    ur.urlretrieve(AliasUrl, outdir + "alias_key.json")

    # Finally, the USHER phylogenetic tree (used by freyja to build the barcodes), contains the nextstrain clades in addition
    # to the pango lineages. Thus, to ensure that we group these into the proper collapsing group,
    # we must place these clades onto the tree. In order to do so we need to know the most equivalent lineage. The nextstrain
    # github has a repository containing a clade phylogenetic tree where they list the clades and their corresponding
    # equivalent lineages. 
    # 
    # We can pull this file and parse it to add the clades on the tree.
    NextStrainCladeUrl = "https://raw.githubusercontent.com/nextstrain/ncov-clades-schema/master/src/clades.json"
    ur.urlretrieve(NextStrainCladeUrl, outdir + "NSClades.json")
    
    # Reads the alias and nextstrain clade json files into 
    # dictionaries.
    aliases = json.load(open(outdir + "/alias_key.json"))
    nsclades = json.load(open(outdir + "/NSClades.json"))

    # Opens the lineages file and skips the header line.
    lineageFile = open(outdir + "lineages.txt", "r")
    lineageFile.readline()

    # We first need to read through the lineages file and separate the viable from the 
    # withdrawn lineages. The viable lineages will have no issue being placed on the tree.
    # Thus, we only need to grab the lineage. However, some of the withdrawn lineages do
    # not have an existing parent (even one that has been withdrawn) and we need to keep their
    # information which contains information on what they are aliases of or were reclassified as.
    # Then we could place them under these lineages rather than a parent.
    lineages = []
    withdrawnLines = []
    for line in lineageFile:
        # Withdrawn lineage begin with a '* character'
        # If the lines do not start with this character, it must be a viable lineage
        if line[0] != "*":
            # The lineage is separated by the description by a tab (except for a few cases where
            # it is separated by a space, but we correct for this using the replace function).
            # So we can split the line by the tab character and append the first value to the
            # list of lineages.
            lineages.append(line.strip().replace(" Alias", "\tAlias").split("\t")[0])
        else:
            # Add the entire line to the list of withdrawn lineages (being sure to
            # correct lines that are not separated by a tab)
            withdrawnLines.append(line.strip().replace(" Withdrawn", "\tWithdrawn"))

    # Create an empty tree with a node labeled root.
    t = Tree()
    t.create_node("root", "root")

    # Create a list to store invalid lineages (those that do not have a valid parent lineage)
    # and recombinant lineages
    invalid = []

    t, invalid = addLineagesToTree(t, lineages, aliases)

    t, invalidWithdrawn = addWithdrawnLineagesToTree(t, withdrawnLines, aliases)

    invalid.append(invalidWithdrawn)
    
    # Finally, we need to add the Nextstrain clades to the tree

    # Parse the file to create a dictionary mapping the
    # clade to a parent lineage.
    cladeToParentLineage = parseNSCladeFile(t, nsclades)

    # Create a list of clades to add by grabbing
    # the dictionary keys.
    cladesToAdd = list(cladeToParentLineage.keys())

    # Loop over the list of clades until all are added to the tree.
    while len(cladesToAdd) > 0:

        # Grab the first clade in the list.
        clade = cladesToAdd[0]

        # Check whether the parent lineage tied to that clade exists in the tree
        if checkLineageExists(t, cladeToParentLineage[clade]) == False:
        #if cladeToParentLineage[clade] not in existingNodes:
            
            # If the parent does not exist, it is likely present in the 
            # list of clades to add and has not been reached yet. Append the
            # clade to the end of the list and come back to it.
            cladesToAdd.append(clade)
        else:
            
            # If the parent does exist, add the clade to the tree.
            t.create_node(clade, clade, parent=cladeToParentLineage[clade]) 

        # Remove the clade at the start of the list.
        cladesToAdd.pop(0)

    # The tree is now complete, so we can return it.
    return t

def getSublineageCollapse(tree, groups, barcodeLineages):
    """ Creates the sublineage collapse map 
    given the defined groups.

    The user input a file with a format similar to the following:
       
       Omicron\tBA.1,BA.3
       Omicron (BA.2)\tBA.2
       Omicron (BA.2.12.1)\tBA.2.12.1
       Delta\tB.1.617.2
    
    Which denotes that for each group, the sublineages of those
    provided should be collapsed under that group. (Ex: BA.1 sublineages
    should be collapsed under Omicron). The function then grabs all of the sublineags
    for the parents listed and places them into a dictionary mapped to the
    group provided.

    One case to be considered is when a sublineage of a group is to be classified
    under a group itself. This can be seen with the example above with the groups 'Omicron (BA.2)'
    and 'Omicron (BA.2.12.1)'. By nature of the tree, BA.2.12.1 and all of its sublineages are
    sublineages of BA.2 and would fall under both groups. Thus, we need to remove all of the BA.2.12.1
    sublineags from the other BA.2 sublineages. The function takes this exception into account

    Parameters:
        tree: A tree containing SARS-CoV-2 lineages
        groups: A dictionary where each key is a group mapped to values
                of lineages to collapse into that group.
        barcodeLineages: A list of lineages present in the barcodes (to
                         account for lineages that may not be present in
                         the tree already)

    Output:
        A dictionary mapping groups to all of the sublineages which will
        fall under them.
    """

    # The function first goes through each of the lineages provided by the user
    # and finds all of the sublineages. This will later be used to remove lineages that
    # are sublineages of a variant in one group, but the user desires in their own group
    # (Ex. BA.2.12.1 is its own group. Thus, we need to remove it from the sublineages of
    # BA.2 )
    # 
    # It first creates a dictionary to store each lineage and its sublineages.
    parentSublineages = {}
    # Loops over each group
    for g in groups.keys():
        # Loops over each lineage under each group
        for p in groups[g]:
            # Grabs the sublineages of that lineage
            sublins = getSubLineages(tree, p)
            # If sublineages were returned, 
            # append the parent to the list
            if sublins != None:
                sublins.append(p)
            # If no sublineages were
            # returned, create a new list
            # containing only the parent.
            else:
                sublins = [p]
            
            # Add the parent and the sublineages 
            # to the running list.
            parentSublineages[p] = sublins

    # Now, we can use the previously created dictionary to remove
    # overlapping sublineages.

    # Loops over each parent in the dictionaries keys.
    for p in parentSublineages.keys():
        # Performs a nested loop over each parent in 
        # the dictionaries keys
        for p2 in parentSublineages.keys():

            # Checks whether the parent is present in the
            # sublineages of another parent. (Because the sublineage
            # list also contains the parent, we have to be sure that the 
            # parents we are looking at are not the same)
            if p in parentSublineages[p2] and p != p2:
                
                # If the parent is present, we can then simply remove
                # all of lineages from the first parent's sublineages
                # from the other parent's.
                p2Sublins = parentSublineages[p2]
                p1Sublins = parentSublineages[p]
                parentSublineages[p2] = [item for item in p2Sublins if item not in p1Sublins]


    # Now that we have grabbed all of the sublineages for each parent provided
    # by the user and removed any overlapping sublineages, we can create a new dictionary 
    # and append the lists of sublineages under the groups supplied by the user.
    # 
    # Ex: Omicron\tBA.1,BA.3 - The BA.1 and BA.3 lineages will be appended together and
    # mapped to the key 'Omicron'

    # Creates an empty dictionary.
    sublineageMap = {}

    # Loops over the groups provided by the user.
    for g in groups.keys():
        # Loops over all of the lineages under the group.
        for lin in groups[g]:

            # If the group has not been added to the collapse
            # map dictionary, create a new key value pair
            # housing the lineage's sublineages
            if g not in sublineageMap.keys():
                sublineageMap[g] = parentSublineages[lin]

            # If the group has already been added to the collapse
            # map dictionary, append the lineage's sublineages
            else:
                sublineageMap[g].extend(parentSublineages[lin])

    # Now that we have created entries for the lineages
    # requested by the user, any lineages not present in these
    # groups will need to be added to the "Not A VOC" group

    # Create an empty list to store the "Not a VOC" lineages
    notAVOC = []

    # Loops over every node in the tree.
    for node in tree.expand_tree(mode=Tree.DEPTH):

        # Grabes the id of each node, which corresponds
        # to the lineages name
        lin = tree[node].identifier
        
        # Creates a boolean value denoting
        # whether the lineage is present in
        # another grouping.
        notCollapsed = True

        # Loops over all of the values (lists of lineages in each group)
        # in the collapse map
        for list in sublineageMap.values():
            # If the lineage is present in the list,
            # set the boolean to false and exit the loop 
            # (too prevent unnecessary coparisons) 
            if lin in list:
                notCollapsed = False
                break

        # If the boolean value is still true (the lineage
        # was not found in the existing groups), add it
        # to the list of "Not A VOC" lineages
        if notCollapsed:
            notAVOC.append(lin)

    # Create a new group in the sublienage map mapping 
    # to the "Not a VOC" lineages
    sublineageMap["Not a VOC"] = notAVOC

    # The final case to check for is if a lineage is present in the
    # barcodes, but not in the lineage tree already. These lineages
    # will be stored under an "UNKNOWN" group

    # Create an empty list to store these lineages
    notFoundLins = []

    # Loop over each lineage in the list of
    # lineages in the barcodes
    for lin in barcodeLineages:

        # If the lineage does not exist in the tree
        if not checkLineageExists(tree, lin):

            # The lineage may still be classifiable, as some contain
            # an existing lineage within their name (Ex: BA.2.75_dropout)
            # Thus, we can try to catch that lineage using a regular expression
            
            # Defines a regex pattern that will match to a lineage and
            # place it within a capture group.
            lineageRegexPattern = r"(\w{1,3}(?:\.\d+)+)"

            # Searches the lineage using the regex pattern
            lineageSearch = re.search(lineageRegexPattern, lin)

            # Checks whether a lineage was found within the name
            if lineageSearch:

                # If so, grab the capture group
                linInName = lineageSearch.group(1)

                # Check whether the lineage in the name exists in 
                # the tree.
                if checkLineageExists(tree, linInName):
                    
                    # If it does exist, we can find where that
                    # lineage is placed in the sublineage map,
                    # and add the unknown lineage to that group 
                    
                    # Loop over every group in the sublineage map
                    for g in sublineageMap.keys():

                        # Check whether the lineage from within the
                        # unknown's name is found in that group
                        if linInName in sublineageMap[g]:
                            # If so, add the unknown lineage under that group
                            sublineageMap[g].append(lin)
                            # Break to prevent unecessary comparisons
                            break
                # If the lineage pulled from the name does not exist, add
                # the unknown lineages to the unknown list
                else:
                    notFoundLins.append(lin)
            # If no lineage pattern was found in the lineage's name
            else:
                # Add it to the list of not found lineages
                notFoundLins.append(lin)

    if len(notFoundLins) != 0:
        # Create a new group in the sublineage map 
        # to store these unknown lineages.
        sublineageMap["Unknown"] = notFoundLins

    # Return the sublineage map
    return sublineageMap

def removeFromsublineageMap(lins, sm):
    """ Takes a list of lineages and removes them from
    a sublineage map. This function is useful when combining groups 
    for S-gene barcodes.

    Parameters:
        lins: a list of lineages to be removed
        sm: a sublineage map dictionary
    
    Output:
        A modified sublineage map with the provided lineages
        removed
    """

    # Loops over ever lineage in the input list
    for lin in lins:
        # Loops over every group in the sublineage map
        # dictionary
        for g in sm.keys():
            # If the lineage is present in the
            # group's list of lineages, remove it
            # from the list
            if lin in sm[g]:
                sm[g].remove(lin)
    # Return the modified sublineage map
    return sm

def writesublineageMap(sm, outDir):
    """ Writes a sublineage map to a file

    Parameters:
        sm: a sublineage map dictionary
        outDir: the directory to write the file to.

    Output:
        None
    """

    # Opens a file named sublineage-map.tsv in the output directory
    o = open("{0}sublineage-map.tsv".format(outDir), "w+")

    # Write a header into the file.
    o.write("Group\tSublineages\n")
    # Loop over every group in the sublineage map
    for g in sm.keys():

        # Check whether the group has lineages grouped under it
        if len(sm[g]) != 0:
            # Write the group name and list of lineages
            # to the file separated by a tab. The list
            # of lineages is joined with a comma.
            o.write("{0}\t{1}\n".format(g, ",".join(sm[g])))

    # Close the file stream.
    o.close()

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
    parser = argparse.ArgumentParser(usage = "Barcode and Sublineage Collapse Update - can be used to manually generate barcodes and sublineage maps")

    parser.add_argument("-i", "--input", required = False, type=str, \
        help="File containing USHER Barcodes to be filtered. If not provided, 'freyja update' will automatically be run and the output barcodes will be used.", \
        action = 'store', dest = 'infile')
    parser.add_argument("-o", "--outdir", required = True, type=str, \
        help='[Required] - directory to place output files', \
        action = 'store', dest = 'outdir')
    parser.add_argument("-c", "--collapseLineages", required = True, type=str, \
        help = "[Required] - Supply this option with a tsv file containing a VOC name and corresponding lineages on each line separated by a tab. The variants falling under that category should be separated by commas (Ex: Omicron\\tBA.1,BA.3)", \
        action = 'store', dest = 'collapse')
    parser.add_argument("--s_gene", required=False, \
        help = "Supplying this option tells the pipeline to filter the barcodes and lineages to include only S gene mutations", \
        action = 'store_true', dest = 'sgene')

    args = parser.parse_args()

    # Parses the output directory inputted by the user
    outdir = parseDirectory(args.outdir)

    # Creates the lineage tree
    lineageTree = buildLineageTree(outdir)

    # Parses the --input option
    df = ''
    if args.infile:

        # If the user supplied the input file to use, parse that file into 
        # a pandas dataframe and notify the user.
        df = parseCSVToDF(args.infile, ',', header=True)
        print("Input file, {0}, provided. Freyja update will not be run and this file will be used instead.\n".format(args.infile))
    else:
        # If the user did not supply an input file, run 'freyja update' and read the barcode in
        # as a pandas dataframe. 
        print("Fetching latest barcodes using 'freyja update'\n")
        runFreyjaUpdate(outdir)
        barcodes = outdir + "usher_barcodes.csv"
        df = parseCSVToDF(barcodes, ',', header=True)


    print("NOTE: All 'proposed', 'misc', and recombinant lineages will be filtered from the barcodes\n")
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

    # Parses the sublineage map option and creates the collapse
    # map dictionary. 
    sublineageMap=''
    # Checks whether the file submitted by the user exists.
    if os.path.exists(args.collapse):

        # If the file exists, it is opened
        cFile = open(args.collapse, "r")

        # Creates an empty dictionary which will hold
        # the groups as keys and list of parent lineages
        # as values
        lineagesToCollapse = {}

        # Reads a line from the input file to skip the header
        cFile.readline()

        # Loops over the lines in the file
        for line in cFile:
            # Splits the line a the tab character.
            # The first value will be the group name
            # and the second value will be a list of parent lineages
            # separated by commas.
            splitLine = line.strip().split("\t")

            # Creates a new entry in the lineages to collapse 
            # dictionary. The key will be the name of the group
            # and the value will be a list of the parent lineages
            # that fall into that group
            lineagesToCollapse[splitLine[0]] = splitLine[1].split(",")

        # Uses the lineages to collapse dictionary created from the input file
        # to create a sublineage map file
        sublineageMap = getSublineageCollapse(lineageTree, lineagesToCollapse, list(df.index))


    else:
        # If the file does not exist, exit the script and notify the user.
        sys.exit("ERROR: File {0} does not exist!".format(args.collapse))

    # If the user supplied the --s_gene option, we need to remove
    # variants outside of the S gene from the barcodes, combine
    # variants with identical S gene mutation profiles, and add these
    # groupsings to the collapse map
    if args.sgene:
        print("S-Gene Option supplied.\nModifying barcodes and sublineage map to account for S-gene identical variants\n")
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
        # and the lineages present in 
        groupFile = open("{0}S-Gene-Indistinguishable-Groups.txt".format(outdir), "w+")
    
        # Creates a new dataframe to store the combined lineages and their mutation profiles
        newCols = cols
        newCols.insert(0, '')
        newdf = pd.DataFrame(columns=newCols)

        #parentSubGroups = {}
        # Loops over all of the groups produced by the groupby
        # function to combine them into 1 entry in the new dataframe.
        # The groups will contain 1+ lineages (an s-gene unique lineage 
        # will be its own group)
        for grp in dup_groups.keys():

            # Grabs the individual variants from the group
            groupLins = list(dup_groups[grp].values)

            # Grabs the columns where the variants have a 1. This indicates 
            # that the variant has a given mutation 
            muts = df.columns[df.loc[groupLins[0],:].isin([1])].values

            # Create a variable to store the label for the group in the final
            # barcodes file.
            bcLabel = ''
        
            # If there is more than 1 variant in the group, we need to 
            # rename this group and reflect the relationship
            # within the collapse Map.
            if len(groupLins) > 1:

                # The naming of the lineage groups is important 
                # to making sure that previously run data does not need to be
                # rerun when new lineages are added/withdrawn. 
                #
                # The group of s-gene identical lineages will be added to
                # the collapse map as a new group, and the lineages will be
                # removed from their previous collapse group. The name of the
                # s-gene identical lineage group will then be added under the
                # collapse group which contained the majority of lineages
                # in the s-gene identical group (this is done because
                # some s-gene identical groups contain lineages from multiple
                # different collapse groups (e.x. Not a VOC and BA.1)) 
                # 
                # To keep s-gene identical group names unique, they will follow the following format:
                #
                # PARENTLINEAGE_Sublineages_Like_LINEAGEFROMGROUP
                #
                # Where 
                #   PARENTLINEAGE = closest common parent of the lineages in the group
                # and
                #   LINEAGEFROMGROUP = the first lineage from the lineages in the
                #   collapse grouo majority when sorted in alphabetical order.
                #   (e.x. {BA.1, BA.1.1, AY.1} will be PARENTLINEAGEG_Sublineages_Like_BA.1)


                # Create an empty variable to store the group's label
                groupLabel = ''


                # One potential is that lineages from different collapse
                # groups have identical s-gene profiles and are thus
                # grouped together. We will need to determine
                # which collapse group to place the group under (as we could
                # choose different options). To solve this, we will count the number
                # how many lineages from each collapse group are present in the s-gene
                # identical group, and place the s-gene idetnical group under
                # the collapse group that is most represented. 

                # Create an empty dictionary which will map collapse groups
                # to the list of their lineages present in the s-gene identical group
                sepByCollapseGoup = {}

                # Now, we need to loop over the lineages in the
                # s gene identical group and determine which collapse
                # group they fall under
                for lin in groupLins:
                    # Loop over the groups in the sublineage collapse map
                    for group in sublineageMap.keys():
                        # Check whether the lineage falls under that 
                        # collapse group
                        if lin in sublineageMap[group]:
                            # If the lineage fell under that collapse group,
                            # 

                            # Check whether the collapse group has already been added to
                            # the dictionary.
                            if group not in sepByCollapseGoup.keys():
                                # If not, create an entry holding the lineage
                                sepByCollapseGoup[group] = [lin]
                            else:
                                # If it has, append the lineage to the list
                                # of lineages.
                                sepByCollapseGoup[group].append(lin)

                            # Break to prevent unnecessary iterations
                            break

                # Now that we have grouped the lineages in the s-gene identical
                # group by their individual collapse groups, we can determine 
                # which collapse group to place the group under
                collapseGroup = ''

                # As well, we can sort the lineages from the majority collapse group
                # and choose the 'Similar to' lineage to add to the group name.
                similarTo = ''
                
                # There may be a case where none of the lineage were
                # found in the collapse map. Thus, we need to check whether
                # any collapse gorups were added to the dictionary
                if len(sepByCollapseGoup.keys()) == 0:
                    # If there were no collapse groups found, we can
                    # collapse the s-gene identical group under "Unknown"
                    collapseGroup = "Unknown"
                    
                    # The 'Similar to' lineage will be just be 
                    # the first lineage in the s-gene identical group
                    # when sorted alphabetically
                    similarTo = sorted(groupLins)[0]
                else:
                    # Otherwise, we can can find the collapse group that had the most lineages
                    # in the in the s-gene identical group and select that to place
                    # the s-gene identical group under
                    collapseGroup = max(sepByCollapseGoup, key=lambda x: len(sepByCollapseGoup[x]))

                    # Then, the 'similar to' lineage will be the first lineage in the 
                    # list of lineages from the majority collapse group when sorted alphabetically.
                    similarTo = sorted(sepByCollapseGoup[collapseGroup])[0]

                # Now, we can find the parent lineage to add to the group name, by finding
                # the common parent of the lineages in the s-gene identical group.
                parent = getCommonLineageParent(lineageTree, groupLins)

                # If the parent is 'root', it means that 
                # both B and A sublineages are present in the group
                # and a better name for that parent would be "B/A"
                if parent == "root":
                    parent = "B/A"
                # If the parent returned was "None", then the lineages in the group
                # have no identifiable parent. We will label them as "Unknown"
                elif parent == "None":
                    parent = "Unknown"


                # The group label can be created with the group common parent and "similar
                # to" lineage 
                groupLabel = "{0}_Sublineages_Like_{1}".format(parent, similarTo)

                # Now, we can add the s-gene identical group under the collapse group determined
                # earlier, remove the lineages in the s-gene identical group, from the map, and
                # add a new key value pair for the 

                # Adds the S-gene identical group under the collapse group 
                # determined earlier
                sublineageMap[collapseGroup].append(groupLabel)

                # Remove the lineages in the s-gene identical group from their collapse groups
                sublineageMap = removeFromsublineageMap(groupLins, sublineageMap)

                # Create a new collapse group in the sublienage map for the s-gene 
                # identical group.
                sublineageMap[groupLabel] = groupLins

                # Set the label for the barcode file equal to the label for the group
                bcLabel = groupLabel

                # Write data about the s-gene identical group to an out file
                # for human reference.
                groupFile.write("Grouping Name: {0}\n".format(groupLabel))
                groupFile.write("Lineages Represented: {0}\n".format(", ".join(groupLins)))
                groupFile.write("\n")
            # If the group only contains 1 lineage, it must
            # be s-gene unique.
            else:
                # The label for the barcode file can simply be the lineage
                # name
                bcLabel = groupLins[0]

            # Grabs the entire row for one of the variants in the group from the original dataframe
            # (since they are all the same within the group, we can just grab the first one).
            barcodes = df.loc[groupLins[0],:].values.tolist()

            # Adds the row into the new dataframe.
            barcodes.insert(0, bcLabel)
            newdf.loc[len(newdf.index)] = barcodes

        # Writes the dataframe to a csv and closes the text filestream.
        newdf.to_csv("{0}S_Gene_barcodes.csv".format(outdir), index=False)
        groupFile.close()
    else:
        df.index.name = None
        df.to_csv("{0}filtered_barcodes.csv".format(outdir), index=True)

    writesublineageMap(sublineageMap, outdir)
    if os.path.exists("{0}usher_barcodes.csv".format(outdir)):
        os.rename("{0}usher_barcodes.csv".format(outdir), "{0}raw_barcodes.csv".format(outdir))

if __name__ == "__main__":
    main()
