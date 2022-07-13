import os
import sys
# Sets the path so that the scripts can be imported
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

import unittest
import pandas as pd

from bin.scripts.utilities import parseDirectory, \
     parseCSVToDF, collapseLineages, writeDataFrame

TEST_FILE_DIR = SCRIPT_DIR + "/utilities-test"

class TestUtilityFunctions(unittest.TestCase):

    def test_parseDirectory_valid_absolute(self):
        valid_dir = TEST_FILE_DIR + "/valid-dir/"
        expected = TEST_FILE_DIR + "/valid-dir/"

        self.assertEqual(parseDirectory(valid_dir), expected)
    
    def test_parseDirectory_valid_relative(self):
        valid_dir = "./test/"
        expected = os.getcwd() + "/./test/"

        self.assertEqual(parseDirectory(valid_dir), expected)
    
    def test_parseDirectory_valid_no_slash(self):
        valid_dir = TEST_FILE_DIR + "/valid-dir"
        expected = TEST_FILE_DIR + "/valid-dir/"

        self.assertEqual(parseDirectory(valid_dir), expected)

    def test_parseDirectory_invalid(self):
        invalid_dir = TEST_FILE_DIR + "/non-existent/"
        expected_error = "ERROR: Directory {0} does not exist!".format(invalid_dir)
        with self.assertRaises(SystemExit) as cm:
            parseDirectory(invalid_dir)
            self.assertEqual(cm.exception, expected_error)

    def test_parseCSVToDF_valid(self):
        df_path = TEST_FILE_DIR + '/file.csv'
        self.assertIsInstance(parseCSVToDF(df_path, ","), pd.DataFrame)
    
    def test_parseCSVToDF_invalid(self):
        invalid_file = TEST_FILE_DIR + "/non-existent.csv"
        expected_error = "ERROR: File {0} does not exist!".format(invalid_file)
        with self.assertRaises(SystemExit) as cm:
            parseCSVToDF(invalid_file, ",")
            self.assertEqual(cm.exception, expected_error)

    def test_writeDataFrame(self):

        # Creates data for test input
        outfile = TEST_FILE_DIR + "/testOut"
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
