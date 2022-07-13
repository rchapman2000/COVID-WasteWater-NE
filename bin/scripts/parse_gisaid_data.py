import sys
import os
import argparse
import pandas as pd
from datetime import datetime, timedelta


#### collapseLineages:
#
# Collapses lineages under the defined parent lineage based on the
# user provided sublineage map. Abundance values are summed for each
# to generate the total abundance for the parent lineages.
#
# Input:
#   sample - the name of the sample being parsed currently.
#   unfiltData - unfiltered data to be collapsed during in this method.
#   map - the sublineage map file provided by the user.
def collapseLineages(sample, unfiltData, map):
    
    filteredDict = {}

    # Loops over each row in the data and adds the entries to a new dictionary
    # which maps the lineage to the abundance
    for row in unfiltData:
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


def main():
    # Creates an argument parser and defines the possible arguments
    # that can be taken.
    parser = argparse.ArgumentParser(usage = "Under Development")

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
    parser.add_argument("--byWeek", required=False, \
        help="Produce data grouped by week rather than by week", \
            action='store_true', dest='byWeek')

    # Grabs arguments entered by the user.
    args = parser.parse_args()

    # Uses pandas to read in the metadata file as a .csv input
    MD = ''
    if os.path.exists(args.infile):
        MD = pd.read_csv(args.infile, delimiter="\t", header=0)
    else:
        sys.exit("ERROR: File {0} does not exist!".format(args.infile))

    sublinMap = ''
    if os.path.exists(args.sublin):
        sublinMap = pd.read_csv(args.sublin, header=0)
    else:
        sys.exit("ERROR: File {0} does not exist!".format(args.sublin))

    startDate = ''
    if datetime.strptime(args.startDate, "%Y-%m-%d"):
        startDate = datetime.strptime(args.startDate, "%Y-%m-%d")
    else:
        sys.exit("Error: Date {0} not provided in YYYY-MM-DD format".format(args.startDate))
    
    endDate = ''
    if datetime.strptime(args.endDate, "%Y-%m-%d"):
        endDate = datetime.strptime(args.endDate, "%Y-%m-%d")
    else:
        sys.exit("Error: Date {0} not provided in YYYY-MM-DD format".format(args.startDate))

    filteredMD = MD[["Accession ID", "Collection date", "Pango lineage"]]
    filteredMD = filteredMD[filteredMD['Collection date'].str.contains('\d\d\d\d-\d\d-\d\d')]
    filteredMD = filteredMD[filteredMD['Pango lineage'] != "Unassigned"]
    filteredMD['DateToUse'] = ''

    for index, row in filteredMD.iterrows():
        date = datetime.strptime(row['Collection date'], "%Y-%m-%d")
        if (date >= datetime.strptime(args.startDate, "%Y-%m-%d") and date <= datetime.strptime(args.endDate, "%Y-%m-%d")):
            if args.byWeek:
                row['DateToUse'] = (datetime.strptime(row['Collection date'], "%Y-%m-%d") - timedelta(days=date.weekday())).strftime("%m/%d/%Y")
            else:
                row['DateToUse'] = date.strftime("%m/%d/%Y")
    filteredMD = filteredMD[filteredMD['DateToUse'] != '']

    dates = filteredMD['DateToUse'].unique().tolist()

    lngAbunds = {}
    unfilteredData = []
    filteredData = []
    for d in dates:
        samplesInDate = len(filteredMD[filteredMD['DateToUse'] == d]['Accession ID'].tolist())
        lngs = filteredMD[filteredMD['DateToUse'] == d]['Pango lineage'].unique().tolist()
        dateData = []
        for ln in lngs:
        
            lngPct = len(filteredMD[(filteredMD['Pango lineage'] == ln) & (filteredMD['DateToUse'] == d)]['Pango lineage'].tolist()) / samplesInDate

            if ln not in lngAbunds.keys():
                lngAbunds[ln] = [0 for i in range(0, len(dates))]

            lngAbunds[ln][dates.index(d)] = lngPct
            dateData.append([d, ln, lngPct])
        
        collapsedlngs = collapseLineages(d, dateData, sublinMap)
        filteredData = filteredData + collapsedlngs
        unfilteredData = unfilteredData + dateData

    dfHeader = "sample,lineage,abundance\n"
    writeDataFrame(unfilteredData, args.outfile + "-unfiltered-dataframe", dfHeader)
    writeDataFrame(filteredData, args.outfile + "-filtered-dataframe", dfHeader)


    



if __name__ == "__main__":
    main()