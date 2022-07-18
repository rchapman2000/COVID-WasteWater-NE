import sys
import os
import argparse
import re
import pandas as pd
from datetime import datetime
import utilities #import parseDirectory, parseDate, collapseLineages, parseCSVToDF, writeDataFrame


def grabFiles(d):
    """ Gathers files matching a specific pattern from 
    a directory

    Paramters:
        d : A directory path to be searched
    
    Output:
        A list containing names of '.demix' files found in
        the directory
    """

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


def parseSampleName(files, r):
    """ Removes a pattern from a set of files using a 
    regex pattern.

    Parameters:
        files: a list of file names

        r: a regex pattern to be used. The pattern must return a group containing
        the filename

    Output:
        A dictionary contaning sample name keys paired with their respective
        file.
    """
    
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


def parseDemix(file):
    """ Parses a '.demix' files to retrive the lineages and abundances 
    identified in the sample.

    Parameters: 
        file: path to a '.demix' file to be parsed.

    Output:
        A list of lineagess and a list of abundances parsed from the file.
    """
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
        split = line.strip("\n").strip(" ").split("\t")

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


def getAverage(list):
    """ Returns the average of a list of float values

    Parameters:
        list: a list of float values

    Output:
        The average of the list of values.
    """
    floatvals = [float(x) for x in list]
    return sum(floatvals) / len(floatvals)


def writeLineageMatrix(samples, master, lngAbunds, outfile):
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
    o = open(outfile, "w+")
    
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
        o.write(x + "," + ",".join([str(i) for i in lngAbunds[x]]) + '\n')

    # Closes the output stream.
    o.close()


def parseByGroup(site, groups, groupCol, master, indir, sampleToFile, abunCutoff, sublinMap):
    """ Instead of parsing by samples groups the samples by either week or dates and
    calculates average abundance of lineages present in samples for those groups.

    Parameters:
        site: The wastewater site being analyzed currently

        groups: a list of groups to be analyzed (either dates or weeks)

        groupCol: the column in the masterfile containing the group identifier
        (either: 'Week' or 'Date')

        master: a pandas dataframe containing the data from the masterfile.

        indir: the directory containing the input .demix files

        sampleToFile: a dictionary pairing sample name keys to file values

        abunCutoff: the cutoff below which to not collapse lineages

        sublinMap: a pandas dataframe linking lineages to parent names
        for collapsing

    Output:
        lngAbunds: a dictionary linking lineage keys to a list of abundances.
        The list contains a spot for each sample in the site. The abundance at a 
        given position represents the lineages abundance in the sample at that same position
        in the list of samples.

        unfilteredData: a list of lists containing data for samples in the site. The lists contain sample
        names, lineages, and abundances.

        filteredData: a list of lists containing data for the samples in the site. This data contains lineages
        that have been collapsed into their parents. The lists contain names, lineages, and abundances.
    """
    # Defines lists/disctionaries to store processed data.
    lngAbunds = {}
    unfilteredData = []
    filteredData = []
    for g in groups:

        # For each group, grab all of the samples found for the given site and group.
        groupSamples = []
        if (site == 'All'):
            groupSamples = master.loc[(master[groupCol] == g)].Sample.tolist()
        else:
            groupSamples = master.loc[(master[groupCol] == g) & (master['Site'] == site)].Sample.tolist()

        # For every sample in the group, parse the .demix file to grab lineages and
        # abundances present in the file. Then adds the lineage to a dictionary pairing
        # a lineage to a list of abundances.
        groupLngAbunds = {}
        for sample in groupSamples:
            lngs, abunds = parseDemix(indir + sampleToFile[sample] + ".demix")
            sampleUnfilteredData = []
            # Loop over every lineage found in the file.
            for ln in lngs:
                # If the lineage is not already in the dictionary,
                # create a new list to store abundances for that lineage.
                # The list will be the length of the number of samples in the group
                # and will initially be filled with zeroes.
                if ln not in groupLngAbunds.keys():
                    groupLngAbunds[ln] = [0 for i in range(0, len(groupSamples))]

                # Grab the list of abundances associated with the given lineage
                # and insert the current sample's abundance. The abundance's position in
                # this list will matcht the sample's position in the list of samples
                # for the given group.
                groupLngAbunds[ln][groupSamples.index(sample)] = abunds[lngs.index(ln)]

        # Now loop over each lineage found for the given group, and add the average 
        # abundance for that week to the overall list of lineages.
        for ln in groupLngAbunds.keys():
            # If the lineage has not been added yet, create an empty list 
            # of the same length as the number of groups in the site. The list will be filled
            # with zeros.
            if ln not in lngAbunds.keys():
                lngAbunds[ln] = [0 for i in range(0, len(groups))]
                    
            # Grab the list of abundances associated with the given lineage
            # and insert the average of the groups's abundances for that lineage into
            # the list. The average abundance's position in this list will match the group's
            # position in the list of groups.
            lngAbunds[ln][groups.index(g)] = getAverage(groupLngAbunds[ln])

            # Create a data entry for the week's lineage and add it to the unfiltered 
            # dataframe data. The entry containst the group, the lineage, and the average abundance
            data = [g, ln, getAverage(groupLngAbunds[ln])]
            sampleUnfilteredData.append(data)

        # Once all of the average abundances have been calculated for that group, collapses
        # the lineages and adds that to the master filtered dataframe data. 
        # Also, appends the unfiltered data for the given sample to the master unfiltered
        # dataframe data. 
        collapsedlngs = utilities.collapseLineages(g, sampleUnfilteredData, abunCutoff, sublinMap)
        filteredData = filteredData + collapsedlngs
        unfilteredData = unfilteredData + sampleUnfilteredData

    return lngAbunds, unfilteredData, filteredData

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
    parser.add_argument('-p', '--pattern', required=False, type=str, \
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
    indir = utilities.parseDirectory(args.indir)
    outdir = utilities.parseDirectory(args.outdir)

    # Reads in the sublineage map into a pandas dataframe. If the file
    # does not exist, the script exists and notifies the user.
    sublinMap = utilities.parseCSVToDF(args.sublin, ",", header=True)
    #if os.path.exists(args.sublin):
    #    sublinMap = pd.read_csv(args.sublin, header=0)
    #else:
    #    sys.exit("ERROR: File {0} does not exist!".format(args.sublin))

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
                weeks = master.loc[master['Site'] == site]['Week'].drop_duplicates().values.tolist()
            
            # Calculate lineage abundances and dataframe data for the weeks
            lngAbunds, unfilteredData, filteredData = parseByGroup(site, weeks, 'Week', master, indir, sampleToFile, abunCutoff, sublinMap)
            # Write the lineage matrix for the weeks
            writeLineageMatrix(weeks, master, lngAbunds, outdir + site + "-lineageMatrix.csv")
        
        # The user did not specify that data to be grouped by weeks. Thus,
        # it will be grouped by individual collection dates in each site.
        elif args.byDate:
            
            # Grabs all of the dates associated with the gven site from the masterfile.
            # If the site is 'All', then every unique date found in the masterfile is
            # added to the list of dates.
            dates = []
            if (site == 'All'):
                dates = master['Date'].drop_duplicates().values.tolist()
            else:
                dates = master.loc[master['Site'] == site]['Date'].drop_duplicates().values.tolist()

            # Calculate lineage abundances and dataframe data for the dates
            lngAbunds, unfilteredData, filteredData = parseByGroup(site, dates, 'Date', master, indir, sampleToFile, abunCutoff, sublinMap)
            # Write the lineage matrix for the dates
            writeLineageMatrix(dates, master, lngAbunds, outdir + site + "-lineageMatrix.csv")
        
        else:

            samples = []
            # Identifies all of the sample associated with a given site.
            # If the site is 'All', add all of the samples to the list.
            if (site == "All"):
                samples = master.Sample.tolist()
            else:
                samples = master.loc[master['Site'] == site].Sample.tolist()

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
                collapsedlngs = utilities.collapseLineages(s, sampleUnfilteredData, abunCutoff, sublinMap)
                filteredData = filteredData + collapsedlngs
                unfilteredData = unfilteredData + sampleUnfilteredData
            writeLineageMatrix(samples, master, lngAbunds, outdir + site + "-lineageMatrix.csv")
        

        # Writes the following files 
        # 1. An unfiltered dataframe, where rows contain fields for a sample/week, lienage,
        #    and abundance
        # 2. A filtered dataframe, which contains the same data as the unfiltered dataframe 
        #    except that the lineages have been combined into thier parent lineage.
        dfHeader = "sample,lineage,abundance\n"
        utilities.writeDataFrame(unfilteredData, outdir + site + "-unfiltered-dataframe", dfHeader)
        utilities.writeDataFrame(filteredData, outdir + site + "-filtered-dataframe", dfHeader)

if __name__ == "__main__":
    main()