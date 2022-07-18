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
        # If the abundance is above the specified cutoff, do not collapse it.
        if float(row[2]) >= float(cutoff):
            filteredDict[row[1]] = [row[2]]
        # If the abundance is below the cutoff, collapse it into the
        # specified parent lineage.
        else:
            # Grab the label provided in the sublineage map for the given lineage.
            label = map[map.Lineage == row[1]].Label.values[0]
            # If the parent lineage has already been added to the dictionary,
            # add the abundance to the current abundance for that lineage.
            if label in filteredDict.keys():
                filteredDict[label][0] = str(float(filteredDict[label][0]) + float(row[2]))
            # If the paretn lineage has not been added, create a new mapping in the dictionary.
            else:
                filteredDict[label] = [row[2]]

    # Format the data back into a dataframe-style format (sample, lineage, abundance)
    returnData = []
    for k in filteredDict.keys():
        returnData.append([sample, k] + filteredDict[k])

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
        outdf.write(",".join(str(i) for i in d) + "\n")
    
    # Closes the output file stream.
    outdf.close()