from cmath import exp
import os
from re import A
import sys

import unittest
import pandas as pd
import subprocess as sp

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_FILE_DIR = SCRIPT_DIR + "/s-gene-test-files"

class TestSGeneBarcodeParser(unittest.TestCase):

    def test_script_withInfile(self):

        expected_vars = ["B|B.15|B.20", "BA.2.12.1"]

        cmd = "python3 {0}/../bin/scripts/s_gene_barcodes.py -i {1} -o {2}".format(SCRIPT_DIR, TEST_FILE_DIR + "/test-input-barcodes.csv", TEST_FILE_DIR)
        sp.run(cmd, check=True, stdout=sp.PIPE, stderr=sys.stdout, shell=True)

        self.assertTrue(os.path.exists(TEST_FILE_DIR + "/S_Gene_barcodes.csv"))
        self.assertTrue(os.path.exists(TEST_FILE_DIR + "/S_Gene_Unfiltered.csv"))
        self.assertTrue(os.path.exists(TEST_FILE_DIR + "/LineageGroups.txt"))

        df = pd.read_csv(TEST_FILE_DIR + "/S_Gene_barcodes.csv")

        vars = df.iloc[:,0].values.tolist()
        
        self.assertEqual(vars, expected_vars)

        os.remove(TEST_FILE_DIR + "/S_Gene_barcodes.csv")
        os.remove(TEST_FILE_DIR + "/S_Gene_Unfiltered.csv")
        os.remove(TEST_FILE_DIR + "/LineageGroups.txt")

    def test_script_withoutInfile(self):
        cmd = "python3 {0}/../bin/scripts/s_gene_barcodes.py -o {1}".format(SCRIPT_DIR, TEST_FILE_DIR)
        sp.run(cmd, check=True, stdout=sp.PIPE, stderr=sys.stdout, shell=True)

        self.assertTrue(os.path.exists(TEST_FILE_DIR + "/curated_lineages.json"))
        self.assertTrue(os.path.exists(TEST_FILE_DIR + "/usher_barcodes.csv"))
        self.assertTrue(os.path.exists(TEST_FILE_DIR + "/S_Gene_barcodes.csv"))
        self.assertTrue(os.path.exists(TEST_FILE_DIR + "/S_Gene_Unfiltered.csv"))
        self.assertTrue(os.path.exists(TEST_FILE_DIR + "/LineageGroups.txt"))

        os.remove(TEST_FILE_DIR + "/curated_lineages.json")
        os.remove(TEST_FILE_DIR + "/usher_barcodes.csv")
        os.remove(TEST_FILE_DIR + "/S_Gene_barcodes.csv")
        os.remove(TEST_FILE_DIR + "/S_Gene_Unfiltered.csv")
        os.remove(TEST_FILE_DIR + "/LineageGroups.txt")

if __name__ == "__main__":
    unittest.main(verbosity=2)
