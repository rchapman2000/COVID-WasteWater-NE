import sys
import os
import pandas as pd
from datetime import datetime as dt


def parseDirectory(d):
    """ Parses a directory to ensure it ends with a trailing slash, exists, and
    is absolute.

    Parameters:
        d: a path to a given directory.

    output:
        The directory after parsing.
    """

    #Checks to see if the directory ends in a trailing slash.
    if d[-1] != '/':
        # If not, add one.
        d = d + '/'

    # Checks to see if the directory path exists.
    if (os.path.isdir(d)):
        # If the directory exists, checks to see if the path 
        # provided is absolute.
        if os.path.isabs(d):
            # If so, return the directory
            return d
        else:
            # If the path is not absolute, add the path to the
            # current working directory.
            return os.getcwd() + '/' + d
    else:
        # If the directory does not exist, exit the script and notify the user.
        sys.exit("ERROR: Directory {0} does not exist!".format(d))


def parseCSVToDF(f, d, header):
    """Parses an input .csv file and places it into a pandas dataframe
    
    Parameters:
        f: a path to a csv file to use

        d: the delimiter of the file

        h: a boolean denoting whether the file has a header

    Output:
        A pandas dataframe containing the data from the csv file.
    """

    # Checks to ensure that the file exists.
    if os.path.exists(f):

        # If the file has a header, include this
        # in the pandas command.
        if header:
            return pd.read_csv(f, delimiter=d, header=0)
        else:
            # If there is no header, do not include a header in
            # the pandas command.
            return pd.read_csv(f, delimiter=d)
    else:
        # If the file does not exist, exit the script and notify the user.
        sys.exit("ERROR: File {0} does not exist!".format(f))

def parseDate(d,f):
    """Parses an input data in string format.
    
    Parameters:
        d: a date in string format

        f: the format of the date to be parsed

    Output:
        A datetime object representing the date.
    """
    try:
        toReturn = dt.strptime(d, f)
        return toReturn
    except ValueError:
        # If the date is in the incorrect format, notify the user and exit the script.
        sys.exit("Error: Date {0} not provided in correct format".format(d))

def parseSublinMap(sublinFile):
    """ Parses a sublineage map file into
    a dictionary

    Parameters:
        sublinFile - the name of the sublineage map file to be opened

    Output:
        A dictionary where the keys are groups name and values
        are lineages that fall within that group.
    """

    # First, check whether the provided file exists
    if os.path.exists(sublinFile):

        # If it exists, open the file and read the first
        # line to get rid of the header
        f = open(sublinFile, "r")
        f.readline()

        # Create an empty dictionary to store the sublineage map
        sublinMap = {}

        # Each line in the file should correspond to a group in the 
        # map. Thus, we need to loop over each line and parse it.
        for line in f:
            # Splitting the line at the tab will separate the group name
            # from the lineages
            splitLine = line.strip().split("\t")

            # The group name will be the first value in
            # the tab separated list
            group = splitLine[0]
            
            # If there are more htan one lineage in a group,
            # they will be separated by commas. Thus, we need to 
            # separate those.
            lineages = splitLine[1].split(",")

            # Creates key value in the dictionary mapping
            # the group name to the list of lineages
            sublinMap[group] = lineages
        
        # Closes the file and returns the dictionary
        f.close()
        return sublinMap
    else:
        # If the file does not exist, notify the user and exit.
        sys.exit("ERROR: File {0} does not exist!".format(sublinFile))



def findLineageGroup(lin, map):
    """ A recursive method that finds the final grouping of a 
    lineage within a sublineage map. It searches the values of the
    key-value pairs in the dictionary until it locates the lineage. It then 
    takes the group name and calls itself. Once the group name is no longer
    found in the values of the dictionary, we have reached the final grouping
    and this is returned.

    There are a few special cases that need to be considered:
        
        Due to how S-gene identical groups are named, the fact that a group
        is not found in the dictionary is not the end of the line. S-gene
        identical groups are named as 
        
        PARENT_Sublineages_Like_FIRSTVARIANTALPHABETICALLY.

        Thus, the parent and alphabetically first variant give some redundancy to check.
        The case could be that a new variant that comes first alphabetically has been 
        added in newer barcodes, changing the group name in the sublineage map. However,
        we can remedy this by simply grabbing the "Like variant" within the map
        and follow that to the final group name.

        Or, the first variant alphabetically may have been withdrawn in the newer update. We
        can also reach the correct final group name by taking the "parent variant' and
        finding that within the map to reach the final group name.

    Parameters:
        lin - the lineage/group name being searched
        map - the sublineage map being traversed.
    """

    # Create a boolean variable to denote whether
    # the given lineage has been found yet.
    #found = False

    # Create an empty variable to store the group name.
    group = ''

    # Loop over each group in the sublineage map
    for g in map.keys():

        # Check whether the lineage is found in that group
        if lin in map[g]:
            # If so, update the group variable to
            # contain the group that the lineage
            # was found under
            group = g

            # Once the lineage is found, we can
            # break from the loop to prevent unnecessary 
            # comparisons
            break 

    # If the group is not empty, then
    # the lineage was found
    if group != '':

        # We now need to check the group to see whether
        # it is the final classification.
        return findLineageGroup(group, map)
    # If the group is empty, then the lineage
    # was not found in any of the values
    # of the dictionary.
    else:
        # If the lineage is one of the sublineage map
        # keys, then it is the final classification and
        # should be returned
        if lin in map.keys():
            return lin
        # If the lineage is not one of they keys,
        # this means that the name provided was not
        # found within the map. Then we need to check
        # whether it is an s-gene identical group name
        # and if we can use any of the 
        # lineages present in the name to classify
        # the group.
        else:

            # We can break a group's name apart by
            # underscores to grab any lineages present
            splitName = lin.split("_")

            # We need to check whether we are looking at
            # a group name vs a lineage. A lineage should not contain any
            # underscores and should have a length of 1.
            if len(splitName) > 1:
                # If the split name has more than 1 value, then it
                # is an s-gene identical group name. In the groups,
                # the last item in the split list will be the first
                # lineage in the list alphabetically and the first
                # is the most recent common parent of the group. Thus,
                # we can grab these try to find their final groups.
                checkLikeLin = findLineageGroup(splitName[-1], map)
                checkParentLin = findLineageGroup(splitName[0], map)

                # The first lineage in the group alphabetically should be
                # used before the parent (because a likely case
                # is that another lineage was just added to the group
                # and came before this lineage alphabetically)
                if checkLikeLin != "Unknown":
                    # If a group was found for this lineage, return it.
                    return checkLikeLin

                # If no lineage group was found for the first lineage
                # alphabetically, then this lineage may have been removed
                # from the group due to being withdraw. Thus, we should
                # use the common parent's group
                elif checkParentLin != "Unknown":
                    # If a group was found for the common parent, return it.
                    return checkParentLin

                # Finally, if neither the first lineage alphabetically
                # or common parent had a group in the list, return "Unknown"
                else:
                    return "Unknown"
            
            # If the split name only contained 1 value, then this
            # was likely a single lineage and is thus unknown.
            else:
                # Return "unknown"
                return "Unknown"

def collapseLineages(sample, unfiltData, cutoff, map):
    """ Collapses individual lineages into their parents based on
    a user provided sublineage map. Abundance values are summed for each
    lineage under a given parent. As well, if the user supplied
    an abundance cutoff, lineages that have abundances above
    this threshold will not be collapsed.

    Parameters:
        sample: the name of the sample being parsed.

        unfiltData - the data containing lineages and abundances
        to be collapsed

        cutoff: the percent cutoff above which a lineage will
        not be collapsed

        map: a pandas dataframe containing the sublineage map.

    Output:
        A list of lists containing collapsed lienage data. Each list
        will contain the sample name, lineage, and abundance.
    """
    filteredDict = {}

    # Loops over each row in the data and adds the entries to a new dictionary
    # which maps the lineage to the abundance
    for row in unfiltData:
        lineage = row[1]
        abundance = row[2]
        site = row[3]
        
        # If the abundance is above the specified cutoff, do not collapse it.
        if float(abundance) >= float(cutoff):
            filteredDict[lineage] = [abundance, site]
        # If the abundance is below the cutoff, collapse it into the
        # specified parent lineage.
        else:
            # Grab the Lineage Group provided in the sublineage map for the given lineage.
            lineageGroup = findLineageGroup(lineage, map)
            # If the parent lineage has already been added to the dictionary,
            # add the abundance to the current abundance for that lineage.
            if lineageGroup in filteredDict.keys():
                filteredDict[lineageGroup] = [str(float(filteredDict[lineageGroup][0]) + float(abundance)), site]
            # If the parent lineage has not been added, create a new mapping in the dictionary.
            else:
                filteredDict[lineageGroup] = [abundance, site]

    # Format the data back into a dataframe-style format (sample, lineage, abundance, site)
    returnData = []
    for lineage in filteredDict.keys():
        returnData.append([sample, lineage] + filteredDict[lineage])

    return returnData

def writeDataFrame(data, outfile, header):
    """ Writes data into a 'dataframe'-like format for
    visualization and analysis.

    Parameters:
        data: a list of lists containing data to be written. Each
        list should contain the following three datapoints:
            1. Sample/Group Name
            2. Lineage
            3. Abundance
        
        outfile: the name of the file to be written to.

        header: the header of the dataframe to be written.

    Output: 
        None
    """
    
    # Opens the output file and creates it if it does not exist.
    outdf = open(outfile + ".csv", "w+")
    
    # Writes the header to the file.
    outdf.write(header)
    
    # Loops over each line in the data, joins the values with a 
    # comma, and adds a newline character to the end.
    for d in data:
        sample = d[0]
        lin = d[1]
        abundance = round(float(d[2]), 4)
        site = d[3]
        outdf.write("{0},{1},{2},{3}\n".format(sample, lin, abundance, site))
    
    # Closes the output file stream.
    outdf.close()

def writeLineageMatrix(samples, lngAbunds, outfile):
    """ Formats and outputs a file in matrix style format. The 
    Columns represent samples/dates/weeks and the rows represent
    a lineages. The intersection of the column and row is the abundance
    of that lineage within the sample.

    Parameters:
        samples: A list of sample names/dates/weeks to output
        
        lngAbunds: a dictionary where lineages keys are paired with
        lists of abundance values. The abundance values are present
        at the same index in the list as their sample in the samples
        list.

        outfile: The name of a file to write the data to.

    Output: 
        Nothing to return.
    """
    
    # Opens the output file and creates it if it does not exist.
    o = open(outfile + ".csv", "w+")
    
    # Grabs the collection date associated with each sample and appends
    # them to a list.
    #dates = []
    #for s in samples:
        #dates.append(master.loc[master['Sample'] == s].Date.values[0])
    
    # Writes the header column of the file by joining the list
    # of dates with commas.
    o.write("," + ",".join(samples) + "\n")

    # Loops over the abundaces in the dicationary and writes each line joined
    # with commas.
    for x in lngAbunds.keys():
        o.write(x + "," + ",".join([str(round(float(i),4)) for i in lngAbunds[x]]) + '\n')

    # Closes the output stream.
    o.close()