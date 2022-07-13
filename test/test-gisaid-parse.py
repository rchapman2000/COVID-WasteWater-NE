import os
import sys
# Sets the path so that the scripts can be imported
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

import unittest
import subprocess
import pandas as pd

from bin.scripts.parse_gisaid_data import collapseLineages, writeDataFrame

# A quick function to read in a csv. Loops over every line in
# the csv files and places the data into a list. Then returns a
# master list containing all individual lists.
def readCSVToList(file):
    # Open the file
    f = open(file, "r")
    # Creates an empty list to store each line
    list = []
    for line in f:
        # Removes the newline character and splits the file 
        # into a list at the commas
        ls = line.strip("\n").split(",")
        # Adds the line to the master list
        list.append(ls)
    f.close()
    return list


class TestPatientDataParse(unittest.TestCase):
    
    # A unit test for the collapse lineages function of the gisaid parser.
    def test_collapseLineages(self):
        # Creates data for a test input
        sample = "Sample1"
        unfiltData = readCSVToList(SCRIPT_DIR + "/patient-data-test-files/test-unfiltered-data.csv")
        map = pd.read_csv(SCRIPT_DIR + "/patient-data-test-files/sublin-test.csv")

        # Creates a list representing what the output should looklike
        correct_results = [["Sample1", "Delta", "0.7"], ["Sample1", "Not a VOC", "0.3"]]

        result = collapseLineages(sample, unfiltData, map)

        # Test passes if the result of collapse lineages matches the
        # correct (intended) result
        self.assertEqual(result, correct_results)


    # A unit test for the write dataframe function of the gisaid parser.
    def test_writeDataFrame(self):

        # Creates data for test input
        outfile = SCRIPT_DIR + "/patient-data-test-files/testOut"
        data = [["SampleX", "Delta", "1.0"]]
        header= "Sample,Lineage,Abundance\n"

        writeDataFrame(data, outfile, header)

        # Checks to make sure that the output file was created
        self.assertTrue(os.path.exists(outfile + ".csv"))

        # Opens the output file 
        f = open(outfile + ".csv", "r")
        # Checks that the first line is a header
        self.assertEqual(f.readline(), "Sample,Lineage,Abundance\n")
        # Checks that hte following line matches what should have been
        # produced given the data
        self.assertEqual(f.readline(), "SampleX,Delta,1.0\n")

        # Closes the filestream and deletes the file.
        f.close()
        os.remove(outfile + ".csv")

    # A unit test to test the entire script runs with the --byWeek option supplied (grouping by week).
    # The script is run given a set of parameters and the output is compared to existing output files containing
    # the anticipated result.
    def test_scriptByWeek(self):
        # Sets the command and runs it using subprocess
        cmd = "python3 {0}/../bin/scripts/parse_gisaid_data.py -i {0}/patient-data-test-files/metadata-test.tsv " \
        "-o {0}/patient-data-test-files/testOut --sublineageMap {0}/patient-data-test-files/sublin-test2.csv " \
        "--startDate 2021-11-29 --endDate 2022-06-20 --byWeek".format(SCRIPT_DIR)
        subprocess.run(cmd,check=True, stdout=subprocess.PIPE, stderr=sys.stdout, shell=True)

        # Tests to ensure that the correct output files have been created:
        #   - a filtered dataframe
        #   - an unfiltered dataframe
        self.assertTrue(os.path.exists(SCRIPT_DIR + "/patient-data-test-files/testOut-filtered-dataframe.csv"))
        self.assertTrue(os.path.exists(SCRIPT_DIR + "/patient-data-test-files/testOut-unfiltered-dataframe.csv"))

        # Reads in the data from the generated output and known output files
        correctFilt = readCSVToList(SCRIPT_DIR + "/patient-data-test-files/byWeekCorrect/filtered.csv")
        correctUnfilt = readCSVToList(SCRIPT_DIR + '/patient-data-test-files/byWeekCorrect/unfiltered.csv')
        outFilt = readCSVToList(SCRIPT_DIR + "/patient-data-test-files/testOut-filtered-dataframe.csv")
        outUnfilt = readCSVToList(SCRIPT_DIR + "/patient-data-test-files/testOut-unfiltered-dataframe.csv")

        # Compares the correct filtered dataframe to the data output by the command
        self.assertEqual(correctFilt, outFilt)
        # Compares the correct unfiltered dataframe to the data output by the command
        self.assertEqual(correctUnfilt, outUnfilt)

        # Removes the output files created
        os.remove(SCRIPT_DIR + "/patient-data-test-files/testOut-filtered-dataframe.csv")
        os.remove(SCRIPT_DIR + "/patient-data-test-files/testOut-unfiltered-dataframe.csv")
    
    # A unit test to test that hte entire script runs defaultly (grouping by date).
    # The script is run given a set of parameters and the output is compared to existing output files containing
    # the anticipated result.
    def test_scriptByDate(self):
        # Sets the command and runs it using subprocess
        cmd = "python3 {0}/../bin/scripts/parse_gisaid_data.py -i {0}/patient-data-test-files/metadata-test.tsv " \
        "-o {0}/patient-data-test-files/testOut --sublineageMap {0}/patient-data-test-files/sublin-test2.csv " \
        "--startDate 2021-11-29 --endDate 2022-06-20".format(SCRIPT_DIR)
        subprocess.run(cmd,check=True, stdout=subprocess.PIPE, stderr=sys.stdout, shell=True)

        # Tests to ensure that the correct output files have been created:
        #   - a filtered dataframe
        #   - an unfiltered dataframe
        self.assertTrue(os.path.exists(SCRIPT_DIR + "/patient-data-test-files/testOut-filtered-dataframe.csv"))
        self.assertTrue(os.path.exists(SCRIPT_DIR + "/patient-data-test-files/testOut-unfiltered-dataframe.csv"))

        # Reads in the data from the generated output and known output files
        correctFilt = readCSVToList(SCRIPT_DIR + "/patient-data-test-files/byDateCorrect/filtered.csv")
        correctUnfilt = readCSVToList(SCRIPT_DIR + '/patient-data-test-files/byDateCorrect/unfiltered.csv')
        outFilt = readCSVToList(SCRIPT_DIR + "/patient-data-test-files/testOut-filtered-dataframe.csv")
        outUnfilt = readCSVToList(SCRIPT_DIR + "/patient-data-test-files/testOut-unfiltered-dataframe.csv")

        # Compares the correct filtered dataframe to the data output by the command
        self.assertEqual(correctFilt, outFilt)
        # Compares the correct unfiltered dataframe to the data output by the command
        self.assertEqual(correctUnfilt, outUnfilt)
        
        # Removes the output files created
        os.remove(SCRIPT_DIR + "/patient-data-test-files/testOut-filtered-dataframe.csv")
        os.remove(SCRIPT_DIR + "/patient-data-test-files/testOut-unfiltered-dataframe.csv")



if __name__ == "__main__":
    unittest.main(verbosity=2)
