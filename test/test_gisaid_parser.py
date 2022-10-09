import os
import sys
# Sets the path so that the scripts can be imported
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

import unittest
import subprocess as sp
import pandas as pd

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

    # A unit test to test the entire script runs with the --byWeek option supplied (grouping by week).
    # The script is run given a set of parameters and the output is compared to existing output files containing
    # the anticipated result.
    def test_scriptByWeek_SGene_Sublin_Map(self):
        # Sets the command and runs it using subprocess
        cmd = "python3 {0}/../bin/scripts/parse_gisaid_data.py -i {0}/gisaid-parse-test-files/metadata-test.tsv " \
        "-o {0}/gisaid-parse-test-files/ --sublineageMap {0}/gisaid-parse-test-files/sublin-test-s-gene.tsv " \
        "--startDate 2021-11-29 --endDate 2022-06-20 --byWeek".format(SCRIPT_DIR)
        sp.run(cmd,check=True, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)

        # Tests to ensure that the correct output files have been created:
        #   - a filtered dataframe
        #   - an unfiltered dataframe
        self.assertTrue(os.path.exists(SCRIPT_DIR + "/gisaid-parse-test-files/Filtered-dataframe.csv"))
        self.assertTrue(os.path.exists(SCRIPT_DIR + "/gisaid-parse-test-files/Unfiltered-dataframe.csv"))

        # Reads in the data from the generated output and known output files
        correctFilt = readCSVToList(SCRIPT_DIR + "/gisaid-parse-test-files/byWeekCorrect/filtered.csv")
        correctUnfilt = readCSVToList(SCRIPT_DIR + '/gisaid-parse-test-files/byWeekCorrect/unfiltered.csv')
        outFilt = readCSVToList(SCRIPT_DIR + "/gisaid-parse-test-files/Filtered-dataframe.csv")
        outUnfilt = readCSVToList(SCRIPT_DIR + "/gisaid-parse-test-files/Unfiltered-dataframe.csv")

        # Compares the correct filtered dataframe to the data output by the command
        self.assertEqual(correctFilt, outFilt)
        # Compares the correct unfiltered dataframe to the data output by the command
        self.assertEqual(correctUnfilt, outUnfilt)

        # Removes the output files created
        os.remove(SCRIPT_DIR + "/gisaid-parse-test-files/Filtered-dataframe.csv")
        os.remove(SCRIPT_DIR + "/gisaid-parse-test-files/Unfiltered-dataframe.csv")
    
    # A unit test to test that hte entire script runs defaultly (grouping by date).
    # The script is run given a set of parameters and the output is compared to existing output files containing
    # the anticipated result.
    def test_scriptByDate_SGene_Sublin_Map(self):
        # Sets the command and runs it using subprocess
        cmd = "python3 {0}/../bin/scripts/parse_gisaid_data.py -i {0}/gisaid-parse-test-files/metadata-test.tsv " \
        "-o {0}/gisaid-parse-test-files/ --sublineageMap {0}/gisaid-parse-test-files/sublin-test-s-gene.tsv " \
        "--startDate 2021-11-29 --endDate 2022-06-20".format(SCRIPT_DIR)
        sp.run(cmd,check=True, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)

        # Tests to ensure that the correct output files have been created:
        #   - a filtered dataframe
        #   - an unfiltered dataframe
        self.assertTrue(os.path.exists(SCRIPT_DIR + "/gisaid-parse-test-files/Filtered-dataframe.csv"))
        self.assertTrue(os.path.exists(SCRIPT_DIR + "/gisaid-parse-test-files/Unfiltered-dataframe.csv"))

        # Reads in the data from the generated output and known output files
        correctFilt = readCSVToList(SCRIPT_DIR + "/gisaid-parse-test-files/byDateCorrect/filtered.csv")
        correctUnfilt = readCSVToList(SCRIPT_DIR + '/gisaid-parse-test-files/byDateCorrect/unfiltered.csv')
        outFilt = readCSVToList(SCRIPT_DIR + "/gisaid-parse-test-files/Filtered-dataframe.csv")
        outUnfilt = readCSVToList(SCRIPT_DIR + "/gisaid-parse-test-files/Unfiltered-dataframe.csv")

        # Compares the correct filtered dataframe to the data output by the command
        self.assertEqual(correctFilt, outFilt)
        # Compares the correct unfiltered dataframe to the data output by the command
        self.assertEqual(correctUnfilt, outUnfilt)

        # Removes the output files created
        os.remove(SCRIPT_DIR + "/gisaid-parse-test-files/Filtered-dataframe.csv")
        os.remove(SCRIPT_DIR + "/gisaid-parse-test-files/Unfiltered-dataframe.csv")

    def test_scriptByWeek_WholeGenome_Sublin_Map(self):
        # Sets the command and runs it using subprocess
        cmd = "python3 {0}/../bin/scripts/parse_gisaid_data.py -i {0}/gisaid-parse-test-files/metadata-test.tsv " \
        "-o {0}/gisaid-parse-test-files/ --sublineageMap {0}/gisaid-parse-test-files/sublin-test-whole-genome.tsv " \
        "--startDate 2021-11-29 --endDate 2022-06-20 --byWeek".format(SCRIPT_DIR)
        sp.run(cmd,check=True, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)

        # Tests to ensure that the correct output files have been created:
        #   - a filtered dataframe
        #   - an unfiltered dataframe
        self.assertTrue(os.path.exists(SCRIPT_DIR + "/gisaid-parse-test-files/Filtered-dataframe.csv"))
        self.assertTrue(os.path.exists(SCRIPT_DIR + "/gisaid-parse-test-files/Unfiltered-dataframe.csv"))

        # Reads in the data from the generated output and known output files
        correctFilt = readCSVToList(SCRIPT_DIR + "/gisaid-parse-test-files/byWeekCorrect/filtered.csv")
        correctUnfilt = readCSVToList(SCRIPT_DIR + '/gisaid-parse-test-files/byWeekCorrect/unfiltered.csv')
        outFilt = readCSVToList(SCRIPT_DIR + "/gisaid-parse-test-files/Filtered-dataframe.csv")
        outUnfilt = readCSVToList(SCRIPT_DIR + "/gisaid-parse-test-files/Unfiltered-dataframe.csv")

        # Compares the correct filtered dataframe to the data output by the command
        self.assertEqual(correctFilt, outFilt)
        # Compares the correct unfiltered dataframe to the data output by the command
        self.assertEqual(correctUnfilt, outUnfilt)

        # Removes the output files created
        os.remove(SCRIPT_DIR + "/gisaid-parse-test-files/Filtered-dataframe.csv")
        os.remove(SCRIPT_DIR + "/gisaid-parse-test-files/Unfiltered-dataframe.csv")
    
    # A unit test to test that hte entire script runs defaultly (grouping by date).
    # The script is run given a set of parameters and the output is compared to existing output files containing
    # the anticipated result.
    def test_scriptByDate_WholeGenome_Sublin_Map(self):
        # Sets the command and runs it using subprocess
        cmd = "python3 {0}/../bin/scripts/parse_gisaid_data.py -i {0}/gisaid-parse-test-files/metadata-test.tsv " \
        "-o {0}/gisaid-parse-test-files/ --sublineageMap {0}/gisaid-parse-test-files/sublin-test-whole-genome.tsv " \
        "--startDate 2021-11-29 --endDate 2022-06-20".format(SCRIPT_DIR)
        sp.run(cmd,check=True, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)

        # Tests to ensure that the correct output files have been created:
        #   - a filtered dataframe
        #   - an unfiltered dataframe
        self.assertTrue(os.path.exists(SCRIPT_DIR + "/gisaid-parse-test-files/Filtered-dataframe.csv"))
        self.assertTrue(os.path.exists(SCRIPT_DIR + "/gisaid-parse-test-files/Unfiltered-dataframe.csv"))

        # Reads in the data from the generated output and known output files
        correctFilt = readCSVToList(SCRIPT_DIR + "/gisaid-parse-test-files/byDateCorrect/filtered.csv")
        correctUnfilt = readCSVToList(SCRIPT_DIR + '/gisaid-parse-test-files/byDateCorrect/unfiltered.csv')
        outFilt = readCSVToList(SCRIPT_DIR + "/gisaid-parse-test-files/Filtered-dataframe.csv")
        outUnfilt = readCSVToList(SCRIPT_DIR + "/gisaid-parse-test-files/Unfiltered-dataframe.csv")

        # Compares the correct filtered dataframe to the data output by the command
        self.assertEqual(correctFilt, outFilt)
        # Compares the correct unfiltered dataframe to the data output by the command
        self.assertEqual(correctUnfilt, outUnfilt)

        # Removes the output files created
        os.remove(SCRIPT_DIR + "/gisaid-parse-test-files/Filtered-dataframe.csv")
        os.remove(SCRIPT_DIR + "/gisaid-parse-test-files/Unfiltered-dataframe.csv")

    def test_script_end_date_before_start_date(self):
        startDate = "2021-01-01"
        endDate = "2020-01-01"

        expected_error = "ERROR: The provided end date, {0}, comes before the provided start date, {1}".format(endDate, startDate)
        with self.assertRaises(sp.CalledProcessError) as cm:
            # Sets the command and runs it using subprocess
            cmd = "python3 {0}/../bin/scripts/parse_gisaid_data.py -i {0}/gisaid-parse-test-files/metadata-test.tsv " \
            "-o {0}/gisaid-parse-test-files/ --sublineageMap {0}/gisaid-parse-test-files/sublin-test-s-gene.tsv " \
            "--startDate {1} --endDate {2}".format(SCRIPT_DIR, startDate, endDate)
            sp.run(cmd, check=True, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
            self.assertEqual(cm.exception.message, expected_error)

    def test_script_abundance_greater_than_one(self):
        cutoff = 20
        expected_error = "ERROR: The abundance cutoff povided, {0}, is not a decimal betwen 0 and 1.".format(cutoff)

        with self.assertRaises(sp.CalledProcessError) as cm:
            cmd = "python3 {0}/../bin/scripts/parse_gisaid_data.py -i {0}/gisaid-parse-test-files/metadata-test.tsv " \
            "-o {0}/gisaid-parse-test-files/ --sublineageMap {0}/gisaid-parse-test-files/sublin-test-s-gene.tsv " \
            "--startDate 2021-11-29 --endDate 2022-06-20 --abundanceThreshold {1}".format(SCRIPT_DIR, cutoff)
            sp.run(cmd,check=True, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
            self.assertEqual(cm.exception.message, expected_error)


if __name__ == "__main__":
    unittest.main(verbosity=2)
