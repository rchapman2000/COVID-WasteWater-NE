import sys
import os
import argparse
import pandas as pd
from datetime import datetime, timedelta


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

    args = parser.parse_args()

    MD = pd.read_csv(args.infile, delimiter="\t", header=0)
    #print(MD["Location"].unique().tolist())

    sublinMap = ''
    if os.path.exists(args.sublin):
        sublinMap = pd.read_csv(args.sublin, header=0)
    else:
        sys.exit("ERROR: File {0} does not exist!".format(args.sublin))

    filteredMD = MD[["Accession ID", "Collection date", "Pango lineage"]]
    #print(len(filteredMD.index))
    filteredMD = filteredMD[filteredMD['Collection date'].str.contains('\d\d\d\d-\d\d-\d\d')]
    #print(len(filteredMD.index))
    #print(filteredMD['Collection date'].unique().tolist())
    filteredMD = filteredMD[filteredMD['Pango lineage'] != "Unassigned"]
    #print(len(filteredMD.index))
    #print(filteredMD)
    #print(filteredMD["Pango lineage"].unique().tolist())

    filteredMD['Week'] = ''

    #o = open(args.outfile, 'w+')
    for index, row in filteredMD.iterrows():
        #print(row['Collection date'])
        date = datetime.strptime(row['Collection date'], "%Y-%m-%d")
        if (date >= datetime.strptime(args.startDate, "%Y-%m-%d") and date <= datetime.strptime(args.endDate, "%Y-%m-%d")):
            row['Week'] = (datetime.strptime(row['Collection date'], "%Y-%m-%d") - timedelta(days=date.weekday())).strftime("%m/%d/%Y")
    #print(filteredMD)
    filteredMD = filteredMD[filteredMD['Week'] != '']
    #print(filteredMD)

    weeks = filteredMD['Week'].unique().tolist()
    #print(weeks)

    lngAbunds = {}
    unfilteredData = []
    filteredData = []
    for w in weeks:
        #print("-----------------------")
        #print("Week {0} contains {1} Samples.".format(w, len(filteredMD[filteredMD['Week'] == w]['Accession ID'].tolist())))
        #print("Sample Dates = {0}".format(filteredMD[filteredMD['Week'] == w]['Collection date'].unique().tolist()))
        #print(filteredMD[filteredMD['Week'] == w]['Accession ID'].tolist())
        #print(filteredMD[filteredMD['Week'] == w]['Accession ID'].tolist())
        #print(len(filteredMD[filteredMD['Week'] == w]['Accession ID'].tolist()))
        samplesInWeek = len(filteredMD[filteredMD['Week'] == w]['Accession ID'].tolist())
        lngs = filteredMD[filteredMD['Week'] == w]['Pango lineage'].unique().tolist()
        weekData = []
        for ln in lngs:
            #print(ln)
            #print(filteredMD[(filteredMD['Pango lineage'] == ln) & (filteredMD['Week'] == w)]['Pango lineage'].tolist())
        
            lngPct = len(filteredMD[(filteredMD['Pango lineage'] == ln) & (filteredMD['Week'] == w)]['Pango lineage'].tolist()) / samplesInWeek
            #print("Lineage {0} is present {1} times, thus {2}\%".format(ln, len(filteredMD[(filteredMD['Pango lineage'] == ln) & (filteredMD['Week'] == w)]['Pango lineage'].tolist()), lngPct))
            #print(lngPct)
            if ln not in lngAbunds.keys():
                lngAbunds[ln] = [0 for i in range(0, len(weeks))]

            lngAbunds[ln][weeks.index(w)] = lngPct
            weekData.append([w, ln, lngPct])
        
        collapsedlngs = collapseLineages(w, weekData, sublinMap)
        filteredData = filteredData + collapsedlngs
        unfilteredData = unfilteredData + weekData

    dfHeader = "sample,lineage,abundance\n"
    writeDataFrame(unfilteredData, args.outfile + "-unfiltered-dataframe", dfHeader)
    writeDataFrame(filteredData, args.outfile + "-filtered-dataframe", dfHeader)


    



if __name__ == "__main__":
    main()