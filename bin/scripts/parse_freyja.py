import sys
import os
import argparse
import re
import pandas as pd
from datetime import datetime


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

#### grabFiles:
#
# grathers files matching a specific regex pattern from a specified 
# directory.
#
# Input:
#   d - a string represening the path to a directory
#
# Output:
#   a list containg file names of '.demix' files present in the
#       directory
def grabFiles(d):

    # Grabs the list of files present in the directory.
    fileList = os.listdir(d)
    files = []

    # Loops over the files and selects the ones that
    # end in '.demix'.
    for f in fileList:
        
        # Uses regex to match the files with the ending '.demix'.
        # it also applies a group that captures everything before
        # the '.demix' file handle.
        result = re.match(".+?(?=\.demix)", f)
        # If the file matched the pattern, add the file name (without
        # the '.demix' to the list of files to return.
        if result:
            files.append(result.group(0))

    # If no files were found, notify the user and stop the script.
    if (len(files) == 0):
        sys.exit("Directory entered does not contain any .demix files")

    return files

#### parseSampleNames;
#
# Removes a pattern from a set of files using regex to retrieve
# sample names.
#
# Input:
#   files - a list of files
#   r - the regex pattern to be applied to the files
#
# Output:
#   a dictionary matching a sample name to a file name 
def parseSampleName(files, r):
    
    sampleToFile = {}
    # Loops over all of the files provided and removes the pattern
    for f in files: 
        # Uses regex to match the pattern to the file.
        result = re.match(r, f)

        if result:
            # If the pattern matched the file, add a mapping between the sample name
            # and file name to the dictionary.
            sampleToFile[result.group()] = f
        else:
            # If the pattern was not found, exit the script and notify the user.
            sys.exit("Pattern Not found in the file {0}!".format(f))

    return sampleToFile

#### parseDemix:
#
# Parses the .demix files produced by freyja to grab a list of lineages
# and abundances found in a given sample.
#
# Input:
#   file - a '.demix' file to analyze
# 
# Output:
#   Both a list of lineages and abundances that were parsed from the given file.
def parseDemix(file):
    # Open the file provided.
    f = open(file, "r")

    # Create empty lists to store the lineages and abundances generated.
    lngs = []
    abunds = []

    # Loop over the lines in the file until it finds either a line
    # starting with 'lineages' or 'abundances'.
    for line in f:
        # Removes the trailing newline character and split
        # the line at a tab character.
        split = line.strip().split("\t")

        # If the line starts with lineages.
        if split[0] == "lineages":
            # Append the present lineages to the list.
            lngs = split[1].split(" ")
        # If the line starts with abundances.
        if split[0] == "abundances":
            # Append the abundances to the list.
            abunds = split[1].split(" ")
    # Close the filestream.
    f.close()
    return lngs, abunds

#### getWeekAverage:
#
# Calcualtes the average of the list provided.
#
# Input:
#   list - a list containing abundance values for a set of samples
#
# Output:
#   the average of the values in the list for that week.
def getAverage(list):
    floatvals = [float(x) for x in list]
    return sum(floatvals) / len(floatvals)

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
        if float(row[2]) >= cutoff:
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

#### writeLineageMatrix:
#
# Writes data into a matrix style format for human visualization.
# Each column is a sample, and each row is a lineage. Values in the
# matrix represent abundances for that lineage within the sample.
#
# Input:
#   samples - a list of sample names
#   master - the masterfile provided to the script
#   lngAbunds - the dictionary linking a lineage to a list of
#               abunances
#   outfile - the name of the file to write the data to.
#
# Output:
#   None
def writeLineageMatrix(samples, master, lngAbunds, outfile):
    
    # Opens the output file and creates it if it does not exist.
    o = open(outfile, "w+")
    
    # Grabs the collection date associated with each sample and appends
    # them to a list.
    dates = []
    for s in samples:
        dates.append(master.loc[master['Sample'] == s].Date.values[0])
    
    # Writes the header column of the file by joining the list
    # of dates with commas.
    o.write("," + ",".join(dates) + "\n")

    # Loops over the abundaces in the dicationary and writes each line joined
    # with commas.
    for x in lngAbunds.keys():
        o.write(x + "," + ",".join([str(i) for i in lngAbunds[x]]) + "\n")

    # Closes the output stream.
    o.close()

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


def main():

    # Creates an argument parser and defines the possible arguments
    # that can be taken.
    parser = argparse.ArgumentParser( \
        usage = "python3 parse_freyja.py")

    parser.add_argument('-i', '--input', required = True, type=str, \
        help='[Required] - path to folder containing \'.demix\' files produced by Freyja', \
        action = 'store', dest = 'indir')
    parser.add_argument('-o', '--output', required = True, type=str, \
        help='[Required] - Directory to place output files', action='store', dest='outdir')
    parser.add_argument('-s', '--sublineageMap', required = False, type = str, \
        help = '[Required] - File containing mappings to sublineages to parent lineages', \
        action = 'store', dest = 'sublin')
    parser.add_argument('-m', '--mastersheet',required=True, type=str, \
        help = "[Required] - Mastersheet that can be used to link samples to their date and site", action = 'store', \
        dest='master')
    parser.add_argument('--removeFromFile', required=False, type=str, \
        help = "A regex pattern that can be used to remove extraneous info from file name to derive the sample name", \
        action = 'store', dest = 'filePattern')
    parser.add_argument("--byDate", required=False, \
        help = "Groups the sames by the date and reports lienage abundance percentages for those dates", \
        action = "store_true", dest="byDate")
    parser.add_argument('--byWeek', required=False, \
        help='Groups samples by week and reports average lineage abundance percentages for those weeks', \
        action ='store_true', dest='byWeek')  
    parser.add_argument('--combineAll', required=False, \
        help='Outputs data files containing average abundances for all samples present in the input file', \
        action='store_true', dest='combineAll') 
    parser.add_argument('--abundanceThreshold', required=False, type=float, \
        help = 'Abundance Percent Threshold below which the lineage will be combined with its parent. [Default = Collapse all Lineages]', \
        action = 'store', dest='abunCutoff')

    # Grabs arguments entered by the user.
    args = parser.parse_args()

    # Parses the input and output directories.
    indir = parseDirectory(args.indir)
    outdir = parseDirectory(args.outdir)

    # Reads in the sublineage map into a pandas dataframe. If the file
    # does not exist, the script exists and notifies the user.
    sublinMap = ''
    if os.path.exists(args.sublin):
        sublinMap = pd.read_csv(args.sublin, header=0)
    else:
        sys.exit("ERROR: File {0} does not exist!".format(args.sublin))

    # Abundance cutoff is 100% by default meaning that every lineage
    # will be collapsed regardless of abundance.
    # If the user specified a different percent, this will be set.
    abunCutoff = 100
    if args.abunCutoff:
        abunCutoff = args.abunCutoff


    # Grabs the input files from the input directory
    # specified by the user.
    files = grabFiles(indir)

    # Creates a dictionary that links each sample to a file.
    # Primarily useful if the user specifies the sample pattern
    # option, so that both the sample name without the pattern,
    # and original file name can be saved.
    sampleToFile = {}
    for f in files:
        sampleToFile[f] = f
    # If the user specified a pattern to be removed from the files,
    # create a dictionary linking the parsed sample name to the sample
    # file.
    if args.filePattern:
        sampleToFile = parseSampleName(files, args.filePattern)

    # Reads in the masterfile into a pandas dataframe and removes
    # any samples in the masterfile that are not present among the
    # input directories.If the file does not exist, the script exits
    #  and notifies the user.
    if os.path.exists(args.master):
        master = pd.read_csv(args.master, quotechar='"')
        master = master[master['Sample'].isin(sampleToFile.keys())]
    else:
        sys.exit("ERROR: File {0} does not exist!".format(args.master))
    
    # Creates a list of all of the unique sites to group the data
    # by. Additinoally, if the user has specified that they want to 
    # have a combined sample, an 'All' site will be added to the sites list.
    sites = master.Site.unique().tolist()
    if args.combineAll:
        sites.append("All")
    
    # Loops over all of the sites identified from the masterfile and
    # creates the datafiles for each.
    for site in sites:
        samples = []
        
        # Identifies all of the sample associated with a given site.
        # If the site is 'All', add all of the samples to the list.
        if (site == "All"):
            samples = master.Sample.tolist()
        else:
            samples = master.loc[master['Site'] == site].Sample.tolist()
        
        # Defines lists/disctionaries to store processed data.
        lngAbunds = {}
        unfilteredData = []
        filteredData = []

        # If the user would like the data grouped by week, follow this block.
        if args.byWeek:

            # Grabs all of the weeks associated with the given site from the masterfile.
            # If the site is 'All', then every unique week found in the masterfile is
            # added to the list of weeks.
            weeks = []
            if (site == 'All'):
                weeks = master['Week'].drop_duplicates().values.tolist()
            else:
                #weeks = master.loc[master['Site'] == site][['Year', 'Week']].drop_duplicates().values.tolist()
                weeks = master.loc[master['Site'] == site]['Week'].drop_duplicates().values.tolist()
            
            # Loop over every week for this site and calculate the lineages and abundances
            # found in samples for that week.
            for w in weeks:
                #week = "{0} Week {1}".format(w[0], w[1])
                #weekSamples = master.loc[(master['Year'] == w[0]) & (master['Week'] == w[1]) & (master['Site'] == site)].Sample.tolist()

                # For each week, grab all of the samples found for the given site and week.
                weekSamples = []
                if (site == 'All'):
                    weekSamples = master.loc[(master['Week'] == w)].Sample.tolist()
                else:
                    weekSamples = master.loc[(master['Week'] == w) & (master['Site'] == site)].Sample.tolist()

                # For every sample in the week, parse the .demix file to grab lineages and
                # abundances present in the file. Then adds the lineage to a dictionary pairing
                # a lineage to a list of abundances.
                wkLngAbunds = {}
                for sample in weekSamples:
                    lngs, abunds = parseDemix(indir + sampleToFile[sample] + ".demix")
                    sampleUnfilteredData = []
                    # Loop over every lineage found in the file.
                    for ln in lngs:
                        # If the lineage is not already in the dictionary,
                        # create a new list to store abundances for that lineage.
                        # The list will be the length of the number of samples in this week
                        # and will initially be filled with zeroes.
                        if ln not in wkLngAbunds.keys():
                            wkLngAbunds[ln] = [0 for i in range(0, len(weekSamples))]

                        # Grab the list of abundances associated with the given lineage
                        # and insert the current sample's abundance. The abundance's position in
                        # this list will matcht the sample's position in the list of samples
                        # for the given week.
                        wkLngAbunds[ln][weekSamples.index(sample)] = abunds[lngs.index(ln)]

                # Now loop over each lineage found for the given week, and add the average 
                # abundance for that week to the overall list of lineages.
                for ln in wkLngAbunds.keys():
                    # If the lineage has not been added yet, create an empty list 
                    # of the same length as the number of weeks in the site. The list will be filled
                    # with zeros.
                    if ln not in lngAbunds.keys():
                        lngAbunds[ln] = [0 for i in range(0, len(weeks))]
                    
                    # Grab the list of abundances associated with the given lineage
                    # and insert the average of the week's abundances for that lineage into
                    # the list. The average abundance's position in this list will match the week's
                    # position in the list of weeks.
                    lngAbunds[ln][weeks.index(w)] = getAverage(wkLngAbunds[ln])

                    # Create a data entry for the week's lineage and add it to the unfiltered 
                    # dataframe data. The entry containst the week, the lineage, and the average abundance
                    data = [w, ln, getAverage(wkLngAbunds[ln])]
                    sampleUnfilteredData.append(data)

                # Once all of the average abundances have been calculated for that week, collapses
                # the lineages and adds that to the master filtered dataframe data. 
                # Also, appends the unfiltered data for the given sample to the master unfiltered
                # dataframe data. 
                collapsedlngs = collapseLineages(w, sampleUnfilteredData, abunCutoff, sublinMap)
                filteredData = filteredData + collapsedlngs
                unfilteredData = unfilteredData + sampleUnfilteredData
        
        # The user did not specify that data to be grouped by weeks. Thus,
        # it will be grouped by individual collection dates in each site.
        elif args.byDate:
            dates = []
            if (site == 'All'):
                dates = master['Date'].drop_duplicates().values.tolist()
            else:
                dates = master.loc[master['Site'] == site]['Date'].drop_duplicates().values.tolist()

            # Loop over every date for this site and calculate the lineages and abundances
            # found in samples collected that date.
            for d in dates:

                # For each date, grab all of the samples found for the given site and date.
                dateSamples = []
                if (site == 'All'):
                    dateSamples = master.loc[(master['Date'] == d)].Sample.tolist()
                else:
                    dateSamples = master.loc[(master['Date'] == d) & (master['Site'] == site)].Sample.tolist()

                # For every sample in the week, parse the .demix file to grab lineages and
                # abundances present in the file. Then adds the lineage to a dictionary pairing
                # a lineage to a list of abundances.
                dtLngAbunds = {}
                for sample in dateSamples:
                    lngs, abunds = parseDemix(indir + sampleToFile[sample] + ".demix")
                    sampleUnfilteredData = []
                    # Loop over every lineage found in the file.
                    for ln in lngs:
                        # If the lineage is not already in the dictionary,
                        # create a new list to store abundances for that lineage.
                        # The list will be the length of the number of samples in this week
                        # and will initially be filled with zeroes.
                        if ln not in dtLngAbunds.keys():
                            dtLngAbunds[ln] = [0 for i in range(0, len(dateSamples))]

                        # Grab the list of abundances associated with the given lineage
                        # and insert the current sample's abundance. The abundance's position in
                        # this list will matcht the sample's position in the list of samples
                        # for the given week.
                        dtLngAbunds[ln][dateSamples.index(sample)] = abunds[lngs.index(ln)]
                
                # Loops overa ll of the lineages found for that date
                for ln in dtLngAbunds.keys():
                    # If the lineage has not been added yet, create an empty list 
                    # of the same length as the number of dates in the site. The list will be filled
                    # with zeros.
                    if ln not in lngAbunds.keys():
                        lngAbunds[ln] = [0 for i in range(0, len(dates))]
                    
                    # Grab the list of abundances associated with the given lineage
                    # and insert the average of the date's abundances for that lineage into
                    # the list. The average abundance's position in this list will match the date's
                    # position in the list of weeks.
                    lngAbunds[ln][dates.index(d)] = getAverage(dtLngAbunds[ln])

                    # Create a data entry for the week's lineage and add it to the unfiltered 
                    # dataframe data. The entry containst the date, the lineage, and the average abundance
                    data = [d, ln, getAverage(dtLngAbunds[ln])]
                    sampleUnfilteredData.append(data)

                # Once all of the average abundances have been calculated for that date, collapses
                # the lineages and adds that to the master filtered dataframe data. 
                # Also, appends the unfiltered data for the given sample to the master unfiltered
                # dataframe data. 
                collapsedlngs = collapseLineages(d, sampleUnfilteredData, abunCutoff, sublinMap)
                filteredData = filteredData + collapsedlngs
                unfilteredData = unfilteredData + sampleUnfilteredData
        
        else:
            for s in samples:
                lngs, abunds = parseDemix(indir + sampleToFile[s] + ".demix")
                sampleUnfilteredData = []
                # Loop over every lineage found in the file.
                for ln in lngs:
                    # If the lineage is not already in the dictionary,
                    # create a new list to store abundances for that lineage.
                    # The list will be the length of the number of samples in this week
                    # and will initially be filled with zeroes.
                    if ln not in lngAbunds.keys():
                        lngAbunds[ln] = [0 for i in range(0, len(samples))]

                    # Grab the list of abundances associated with the given lineage
                    # and insert the current sample's abundance. The abundance's position in
                    # this list will matcht the sample's position in the list of samples
                    # for the given week.
                    lngAbunds[ln][samples.index(s)] = abunds[lngs.index(ln)]
                
                    data = [s, ln, lngAbunds[ln][samples.index(s)]]
                    sampleUnfilteredData.append(data)

                # Once all of the average abundances have been calculated for that date, collapses
                # the lineages and adds that to the master filtered dataframe data. 
                # Also, appends the unfiltered data for the given sample to the master unfiltered
                # dataframe data. 
                collapsedlngs = collapseLineages(s, sampleUnfilteredData, abunCutoff, sublinMap)
                filteredData = filteredData + collapsedlngs
                unfilteredData = unfilteredData + sampleUnfilteredData

        

        # Writes the output files 
        # 1. A 'Lineage Matrix' which has rows representing lineages and columns
        #    representing samples/weeks
        # 2. An unfiltered dataframe, where rows contain fields for a sample/week, lienage,
        #    and abundance
        # 3. A filtered dataframe, which contains the same data as the unfiltered dataframe 
        #    except that the lineages have been combined into thier parent lineage.
        writeLineageMatrix(samples, master, lngAbunds, outdir + site + "-lineageMatrix.csv")
        dfHeader = "sample,lineage,abundance\n"
        writeDataFrame(unfilteredData, outdir + site + "-unfiltered-dataframe", dfHeader)
        writeDataFrame(filteredData, outdir + site + "-filtered-dataframe", dfHeader)

if __name__ == "__main__":
    main()