import sys
import os
import argparse
import pandas as pd
from datetime import datetime, timedelta
from utilities import collapseLineages, writeDataFrame, \
    parseCSVToDF, parseDate

def main():
    # Creates an argument parser and defines the possible arguments
    # that can be taken.
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--input', required = True, type=str, \
        help='[Required] - path to gisaid metadata file', \
        action = 'store', dest = 'infile')
    parser.add_argument('-o', '--output', required = True, type=str, \
        help='[Required] - Output file name', action='store', dest='outfile')
    parser.add_argument('-s', '--sublineageMap', required = True, type = str, \
        help = '[Required] - File containing mappings to sublineages to parent lineages', \
        action = 'store', dest = 'sublin')
    parser.add_argument("--startDate", required=True, type=str, \
        help="First date of range to be parsed (Date should be in format YYYY-MM-DD)", \
        action = 'store', dest='startDate')
    parser.add_argument("--endDate", required=True, type=str, \
        help="Final date of range to be parsed (Date should be in format YYYY-MM-DD)", \
        action = 'store', dest='endDate')
    parser.add_argument('--abundanceThreshold', required=False, type=float, \
        help = 'Abundance Percent Threshold below which the lineage will be combined with its parent. Must be a decimal between 0 and 1. [Default = Collapse all Lineages]', \
        action = 'store', dest='abunCutoff')
    parser.add_argument("--byWeek", required=False, \
        help="Produce data grouped by week rather than by week", \
            action='store_true', dest='byWeek')

    # Grabs arguments entered by the user.
    args = parser.parse_args()

    # Uses pandas to read in the metadata and sublineage map files.
    MD = parseCSVToDF(args.infile, '\t', header=True)
    sublinMap = parseCSVToDF(args.sublin, ",",header=True)

    # Parses in the start and end dates supplied by the user.
    startDate = parseDate(args.startDate, "%Y-%m-%d")
    endDate = parseDate(args.endDate, "%Y-%m-%d")

    if endDate < startDate:
        sys.exit("ERROR: The provided end date, {0}, comes before the provided start date, {1}".format(endDate, startDate))

    # The script defautly collapses all lineages, so the cutoff is set to a number larger
    # one.datetime.strptime(row['Collection date'], "%Y-%m-%d")
    cutoff = 10
    if args.abunCutoff:
        # Checks to make sure that the cutoff is betwen 0 and 1
        if args.abunCutoff < 1 and args.abuncutoff > 0:
            cutoff = args.abuncutoff
        else:
            sys.exit("ERROR: The abundance cutoff povided, {0}, is not a decimal betwen 0 and 1.".format(args.abunCutoff))

    # Filters the accession ID, collectiondate, and lineage columns from the metadata file
    filteredMD = MD[["Accession ID", "Collection date", "Pango lineage"]]

    # Filteres the data to only contain rows with complete collection dates
    # (i.e. not missing the day or month) and with assigned lineages only.
    filteredMD = filteredMD[filteredMD['Collection date'].str.contains('\d\d\d\d-\d\d-\d\d')]
    filteredMD = filteredMD[filteredMD['Pango lineage'] != "Unassigned"]

    # Adds a column to the dataframe to use for distinguishing between merging by date and week
    filteredMD['DateToUse'] = ''

    # Loops over each rop in the metadata to exclude dates that fall outside of the 
    # specificed range. Additionally, this handles assigning each row a week, if the
    # --byWeek option was specified.
    for index, row in filteredMD.iterrows():

        # Grabs the collection date
        date = parseDate(row['Collection date'], "%Y-%m-%d")#datetime.strptime(row['Collection date'], "%Y-%m-%d")
        
        # Checks to ensure that the date falls within the correct range.
        if (date >= startDate and date <= endDate):
            
            # If the user wants week groupings, the DateToUse column is set to the Monday 
            # of the week that the sample was collected on.
            if args.byWeek:
                row['DateToUse'] = (date - timedelta(days=date.weekday())).strftime("%m/%d/%Y")
            
            # The DateToUse column is just set to the date.
            else:
                row['DateToUse'] = date.strftime("%m/%d/%Y")

    # Removes any rows with empty DateToUse columns (indicates that the collection date was out of
    # the specified range)
    filteredMD = filteredMD[filteredMD['DateToUse'] != '']

    # Grabs a list of all f the unique dates/weeks present in the data.
    dates = filteredMD['DateToUse'].unique().tolist()

    # Defines lists/disctionaries to store processed data.
    lngAbunds = {}
    unfilteredData = []
    filteredData = []

    # Loops over the set of dates to process the data for each date
    for d in dates:
        
        # Counts the number of Gisaid entries on the given date
        samplesInDate = len(filteredMD[filteredMD['DateToUse'] == d]['Accession ID'].tolist())
        # Grabs a list of all unique lineages from samples in the given date range
        lngs = filteredMD[filteredMD['DateToUse'] == d]['Pango lineage'].unique().tolist()
        dateData = []

        # Loops over each of the lineages found on that date to 
        # calculate the percent abundance.
        for ln in lngs:

            # Calculates the percent abundance by dividing the number of samples
            # assigned that lingeage on the given date by the total number of samples
            # collected that date.
            lngPct = len(filteredMD[(filteredMD['Pango lineage'] == ln) & (filteredMD['DateToUse'] == d)]['Pango lineage'].tolist()) / samplesInDate

            # Checks to see if the lineage has been added to the master list
            # previously
            if ln not in lngAbunds.keys():
                # If not, creates a list containing 0s for each of the dates
                # present in the data
                lngAbunds[ln] = [0 for i in range(0, len(dates))]

            # Accesses the list associated with the lineage and sets the value at the
            # same position as the date in the dates list to the abundance.
            lngAbunds[ln][dates.index(d)] = lngPct
            # Adds the data to a list containing rows of data
            dateData.append([d, ln, lngPct])
        
        # Collapses the lineages for the given date based on the sublineage map
        # and cutoff specified by the user
        collapsedlngs = collapseLineages(d, dateData, cutoff, sublinMap)
        
        # Adds the filtered and unfiltered data to the master list
        filteredData = filteredData + collapsedlngs
        unfilteredData = unfilteredData + dateData

    # Writes the data to dataframe files
    dfHeader = "sample,lineage,abundance\n"
    writeDataFrame(unfilteredData, args.outfile + "-unfiltered-dataframe", dfHeader)
    writeDataFrame(filteredData, args.outfile + "-filtered-dataframe", dfHeader)


    



if __name__ == "__main__":
    main()