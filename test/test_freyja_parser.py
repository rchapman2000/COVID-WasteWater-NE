import os
import sys
import shutil

import unittest
import subprocess as sp
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_FILE_DIR = SCRIPT_DIR + "/freyja-parse-test-files"

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

class TestFreyjaParser(unittest.TestCase):
    
    def test_script_valid_bySample(self):
        cmd="python3 {0}/../bin/scripts/parse_freyja.py -i {1}/inDir -o {1}/outDir -s {1}/sublin-test.csv -m {1}/master-test.csv".format(SCRIPT_DIR, TEST_FILE_DIR)
        sp.run(cmd, check=True, stdout=sp.PIPE, stderr=sys.stdout, shell=True)

        self.assertTrue(os.path.exists(TEST_FILE_DIR + "/outDir/Site-1-filtered-dataframe.csv"))
        self.assertTrue(os.path.exists(TEST_FILE_DIR + "/outDir/Site-1-unfiltered-dataframe.csv"))
        self.assertTrue(os.path.exists(TEST_FILE_DIR + "/outDir/Site-1-lineageMatrix.csv"))
        self.assertTrue(os.path.exists(TEST_FILE_DIR + "/outDir/Site-2-filtered-dataframe.csv"))
        self.assertTrue(os.path.exists(TEST_FILE_DIR + "/outDir/Site-2-unfiltered-dataframe.csv"))
        self.assertTrue(os.path.exists(TEST_FILE_DIR + "/outDir/Site-2-lineageMatrix.csv"))

        outs1filt = readCSVToList(TEST_FILE_DIR + "/outDir/Site-1-filtered-dataframe.csv")
        corrects1filt = readCSVToList(TEST_FILE_DIR + "/correctBySample/Site-1-filtered-dataframe.csv")
        outs1unfilt = readCSVToList(TEST_FILE_DIR + "/outDir/Site-1-unfiltered-dataframe.csv")
        corrects1unfilt = readCSVToList(TEST_FILE_DIR + "/correctBySample/Site-1-unfiltered-dataframe.csv")
        outs1mat = readCSVToList(TEST_FILE_DIR + "/outDir/Site-1-lineageMatrix.csv")
        corrects1mat = readCSVToList(TEST_FILE_DIR + "/correctBySample/Site-1-lineageMatrix.csv")

        outs2filt = readCSVToList(TEST_FILE_DIR + "/outDir/Site-2-filtered-dataframe.csv")
        corrects2filt = readCSVToList(TEST_FILE_DIR + "/correctBySample/Site-2-filtered-dataframe.csv")
        outs2unfilt = readCSVToList(TEST_FILE_DIR + "/outDir/Site-2-unfiltered-dataframe.csv")
        corrects2unfilt = readCSVToList(TEST_FILE_DIR + "/correctBySample/Site-2-unfiltered-dataframe.csv")
        outs2mat = readCSVToList(TEST_FILE_DIR + "/outDir/Site-2-lineageMatrix.csv")
        corrects2mat = readCSVToList(TEST_FILE_DIR + "/correctBySample/Site-2-lineageMatrix.csv")
        

        self.assertEqual(outs1filt, corrects1filt)
        self.assertEqual(outs1unfilt, corrects1unfilt)
        self.assertEqual(outs1mat, corrects1mat)
        self.assertEqual(outs2filt, corrects2filt)
        self.assertEqual(outs2unfilt, corrects2unfilt)
        self.assertEqual(outs2mat, corrects2mat)

        for root, dirs, files in os.walk(TEST_FILE_DIR + "/outDir/"):
            for f in files:
                os.remove(os.path.join(root, f))

    
    def test_script_valid_byDate(self):
        cmd="python3 {0}/../bin/scripts/parse_freyja.py -i {1}/inDir -o {1}/outDir -s {1}/sublin-test.csv -m {1}/master-test.csv --byDate".format(SCRIPT_DIR, TEST_FILE_DIR)
        sp.run(cmd, check=True, stdout=sp.PIPE, stderr=sys.stdout, shell=True)

        self.assertTrue(os.path.exists(TEST_FILE_DIR + "/outDir/Site-1-filtered-dataframe.csv"))
        self.assertTrue(os.path.exists(TEST_FILE_DIR + "/outDir/Site-1-unfiltered-dataframe.csv"))
        self.assertTrue(os.path.exists(TEST_FILE_DIR + "/outDir/Site-1-lineageMatrix.csv"))
        self.assertTrue(os.path.exists(TEST_FILE_DIR + "/outDir/Site-2-filtered-dataframe.csv"))
        self.assertTrue(os.path.exists(TEST_FILE_DIR + "/outDir/Site-2-unfiltered-dataframe.csv"))
        self.assertTrue(os.path.exists(TEST_FILE_DIR + "/outDir/Site-2-lineageMatrix.csv"))

        outs1filt = readCSVToList(TEST_FILE_DIR + "/outDir/Site-1-filtered-dataframe.csv")
        corrects1filt = readCSVToList(TEST_FILE_DIR + "/correctByDate/Site-1-filtered-dataframe.csv")
        outs1unfilt = readCSVToList(TEST_FILE_DIR + "/outDir/Site-1-unfiltered-dataframe.csv")
        corrects1unfilt = readCSVToList(TEST_FILE_DIR + "/correctByDate/Site-1-unfiltered-dataframe.csv")
        outs1mat = readCSVToList(TEST_FILE_DIR + "/outDir/Site-1-lineageMatrix.csv")
        corrects1mat = readCSVToList(TEST_FILE_DIR + "/correctByDate/Site-1-lineageMatrix.csv")

        outs2filt = readCSVToList(TEST_FILE_DIR + "/outDir/Site-2-filtered-dataframe.csv")
        corrects2filt = readCSVToList(TEST_FILE_DIR + "/correctByDate/Site-2-filtered-dataframe.csv")
        outs2unfilt = readCSVToList(TEST_FILE_DIR + "/outDir/Site-2-unfiltered-dataframe.csv")
        corrects2unfilt = readCSVToList(TEST_FILE_DIR + "/correctByDate/Site-2-unfiltered-dataframe.csv")
        outs2mat = readCSVToList(TEST_FILE_DIR + "/outDir/Site-2-lineageMatrix.csv")
        corrects2mat = readCSVToList(TEST_FILE_DIR + "/correctByDate/Site-2-lineageMatrix.csv")
        

        self.assertEqual(outs1filt, corrects1filt)
        self.assertEqual(outs1unfilt, corrects1unfilt)
        self.assertEqual(outs1mat, corrects1mat)
        self.assertEqual(outs2filt, corrects2filt)
        self.assertEqual(outs2unfilt, corrects2unfilt)
        self.assertEqual(outs2mat, corrects2mat)

        for root, dirs, files in os.walk(TEST_FILE_DIR + "/outDir/"):
            for f in files:
                os.remove(os.path.join(root, f))

    def test_script_valid_byWeek(self):
        cmd="python3 {0}/../bin/scripts/parse_freyja.py -i {1}/inDir -o {1}/outDir -s {1}/sublin-test.csv -m {1}/master-test.csv --byWeek".format(SCRIPT_DIR, TEST_FILE_DIR)
        sp.run(cmd, check=True, stdout=sys.stdout, stderr=sys.stdout, shell=True)

        self.assertTrue(os.path.exists(TEST_FILE_DIR + "/outDir/Site-1-filtered-dataframe.csv"))
        self.assertTrue(os.path.exists(TEST_FILE_DIR + "/outDir/Site-1-unfiltered-dataframe.csv"))
        self.assertTrue(os.path.exists(TEST_FILE_DIR + "/outDir/Site-1-lineageMatrix.csv"))
        self.assertTrue(os.path.exists(TEST_FILE_DIR + "/outDir/Site-2-filtered-dataframe.csv"))
        self.assertTrue(os.path.exists(TEST_FILE_DIR + "/outDir/Site-2-unfiltered-dataframe.csv"))
        self.assertTrue(os.path.exists(TEST_FILE_DIR + "/outDir/Site-2-lineageMatrix.csv"))

        outs1filt = readCSVToList(TEST_FILE_DIR + "/outDir/Site-1-filtered-dataframe.csv")
        corrects1filt = readCSVToList(TEST_FILE_DIR + "/correctByWeek/Site-1-filtered-dataframe.csv")
        outs1unfilt = readCSVToList(TEST_FILE_DIR + "/outDir/Site-1-unfiltered-dataframe.csv")
        corrects1unfilt = readCSVToList(TEST_FILE_DIR + "/correctByWeek/Site-1-unfiltered-dataframe.csv")
        outs1mat = readCSVToList(TEST_FILE_DIR + "/outDir/Site-1-lineageMatrix.csv")
        corrects1mat = readCSVToList(TEST_FILE_DIR + "/correctByWeek/Site-1-lineageMatrix.csv")
        outs2filt = readCSVToList(TEST_FILE_DIR + "/outDir/Site-2-filtered-dataframe.csv")
        corrects2filt = readCSVToList(TEST_FILE_DIR + "/correctByWeek/Site-2-filtered-dataframe.csv")
        outs2unfilt = readCSVToList(TEST_FILE_DIR + "/outDir/Site-2-unfiltered-dataframe.csv")
        corrects2unfilt = readCSVToList(TEST_FILE_DIR + "/correctByWeek/Site-2-unfiltered-dataframe.csv")
        outs2mat = readCSVToList(TEST_FILE_DIR + "/outDir/Site-2-lineageMatrix.csv")
        corrects2mat = readCSVToList(TEST_FILE_DIR + "/correctByWeek/Site-2-lineageMatrix.csv")
        

        self.assertEqual(outs1filt, corrects1filt)
        self.assertEqual(outs1unfilt, corrects1unfilt)
        self.assertEqual(outs1mat, corrects1mat)
        self.assertEqual(outs2filt, corrects2filt)
        self.assertEqual(outs2unfilt, corrects2unfilt)
        self.assertEqual(outs2mat, corrects2mat)

        for root, dirs, files in os.walk(TEST_FILE_DIR + "/outDir/"):
            for f in files:
                os.remove(os.path.join(root, f))



if __name__ == "__main__":
    unittest.main(verbosity=2)