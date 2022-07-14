import sys
import os
import pandas as pd
from datetime import datetime as dt

#### parseDirectory:
#
# Ensures that the directory passed to the script has a trailing 
# slash, is a valid path, and is transformed into an absolute path.
#
# Input:
#   d - a string representing the path to a directory
#
# Output:
#   a corrected string representing the path to a directory
def parseDirectory(d):

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
    if os.path.exists(f):
        if header:
            return pd.read_csv(f, delimiter=d, header=0)
        else:
            return pd.read_csv(f, delimiter=d)
    else:
        sys.exit("ERROR: File {0} does not exist!".format(f))

def parseDate(d,f):
    try:
        toReturn = dt.strptime(d, f)
        return toReturn
    except ValueError:
         sys.exit("Error: Date {0} not provided in correct format".format(d))

#### collapseLineages:
#
# Collapses lineages under the defined parent lineage based on the
# user provided sublineage map. Abundance values are summed for each
# to generate the total abundance for the parent lineages.
#
# Input:
#   sample - the name of the sample being parsed currently.
#   unfiltData - unfiltered data to be collapsed during in this method.
#   cutoff - a threshold where if a lineage has a greater abundance,
#            it will not be collapsed into its parent.
#   map - the sublineage map file provided by the user.
def collapseLineages(sample, unfiltData, cutoff, map):
    
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

#### writeDataFrame:
#
# Writes data into a dataframe like format for easy visualization.
#
# Input:
#   data - the data to be written into the dataframe
#   outfile - the name of the file to be written to
#   header - the header of the dataframe to be written.
#
# Output:
#   None
def writeDataFrame(data, outfile, header):
    
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