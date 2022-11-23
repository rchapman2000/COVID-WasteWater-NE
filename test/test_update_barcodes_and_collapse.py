from ast import Sub
from cmath import exp
from dis import findlinestarts
import os
from re import A
import sys
from tabnanny import check

import unittest
import pandas as pd
import subprocess as sp
from treelib import Node, Tree

from bin.scripts.data_manip_utils import parseSublinMap, findLineageGroup

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_FILE_DIR = SCRIPT_DIR + "/update-barcodes-and-collapse-test-files"

def cleanUpFiles():
    FilesToRemove = ["S_Gene_barcodes.csv", "S_Gene_Unfiltered.csv", "S-Gene-Indistinguishable-Groups.txt", "sublineage-map.tsv", "filtered_barcodes.csv", "public-latest.all.masked.pb.gz", \
                        "alias_key.json", "lineages.txt", "NSClades.json", "raw_barcodes.csv", "curated_lineages.json"]

    for f in FilesToRemove:
        fp = TEST_FILE_DIR + "/" + f
        if os.path.exists(fp):
            os.remove(fp)

class TestSGeneBarcodeParser(unittest.TestCase):

    def test_script_noInFile_WholeGenome(self):

        cmd = "python3 {0}/../bin/scripts/update_barcodes_and_collapse.py -o {2} -c {3}".format(SCRIPT_DIR, TEST_FILE_DIR + "/test-input-barcodes.csv", TEST_FILE_DIR, TEST_FILE_DIR + "/test-collapse.tsv")
        sp.run(cmd, check=True, stdout=sp.PIPE, stderr=sys.stdout, shell=True)

        self.assertTrue(os.path.exists(TEST_FILE_DIR + "/filtered_barcodes.csv"))
        self.assertFalse(os.path.exists(TEST_FILE_DIR + "/S_Gene_barcodes.csv"))
        self.assertFalse(os.path.exists(TEST_FILE_DIR + "/S_Gene_Unfiltered.csv"))
        self.assertFalse(os.path.exists(TEST_FILE_DIR + "/S-Gene-Indistinguishable-Groups.txt"))

        cleanUpFiles()

    def test_script_noInFile_SGene(self):
        cmd = "python3 {0}/../bin/scripts/update_barcodes_and_collapse.py -o {2} -c {3} --s_gene".format(SCRIPT_DIR, TEST_FILE_DIR + "/test-input-barcodes.csv", TEST_FILE_DIR, TEST_FILE_DIR + "/test-collapse.tsv")
        sp.run(cmd, check=True, stdout=sp.PIPE, stderr=sys.stdout, shell=True)

        self.assertFalse(os.path.exists(TEST_FILE_DIR + "/usher_barcodes.csv"))
        self.assertFalse(os.path.exists(TEST_FILE_DIR + "filtered_barcodes.csv"))
        self.assertTrue(os.path.exists(TEST_FILE_DIR + "/S_Gene_barcodes.csv"))
        self.assertTrue(os.path.exists(TEST_FILE_DIR + "/S_Gene_Unfiltered.csv"))
        self.assertTrue(os.path.exists(TEST_FILE_DIR + "/S-Gene-Indistinguishable-Groups.txt"))

        cleanUpFiles()

    #def test_script_withInFile_WholeGenome(self):
        
    #    expected_bcs = ['B', "B.15", "B.20", "BA.2.12.1"]
        
    #    cmd = "python3 {0}/../bin/scripts/update_barcodes_and_collapse.py -i {1} -o {2} -c {3}".format(SCRIPT_DIR, TEST_FILE_DIR + "/test-input-barcodes.csv", TEST_FILE_DIR, TEST_FILE_DIR + "/test-collapse.tsv")
    #    sp.run(cmd, check=True, stdout=sp.PIPE, stderr=sys.stdout, shell=True)

    #    self.assertFalse(os.path.exists(TEST_FILE_DIR + "/S_Gene_barcodes.csv"))
    #    self.assertFalse(os.path.exists(TEST_FILE_DIR + "/S_Gene_Unfiltered.csv"))
    #    self.assertFalse(os.path.exists(TEST_FILE_DIR + "/S-Gene-Indistinguishable-Groups.txt"))

    #    df = pd.read_csv(TEST_FILE_DIR + "/usher_barcodes.csv")

    #    barcodes = df.iloc[:,0].values.tolist()

    #    self.assertEqual(barcodes, expected_bcs)

        #cleanUpFiles()

    def test_script_withInFile_SGene(self):

        expected_bcs = ["B_Sublineages_Like_B", "BA.2.12.1"]

        cmd = "python3 {0}/../bin/scripts/update_barcodes_and_collapse.py -i {1} -o {2} -c {3} --s_gene".format(SCRIPT_DIR, TEST_FILE_DIR + "/test-input-barcodes.csv", TEST_FILE_DIR, TEST_FILE_DIR + "/test-collapse.tsv")
        sp.run(cmd, check=True, stdout=sp.PIPE, stderr=sys.stdout, shell=True)

        self.assertFalse(os.path.exists(TEST_FILE_DIR + "/usher_barcodes.csv"))
        self.assertFalse(os.path.exists(TEST_FILE_DIR + "filtered_barcodes.csv"))
        self.assertTrue(os.path.exists(TEST_FILE_DIR + "/S_Gene_barcodes.csv"))
        self.assertTrue(os.path.exists(TEST_FILE_DIR + "/S_Gene_Unfiltered.csv"))
        self.assertTrue(os.path.exists(TEST_FILE_DIR + "/S-Gene-Indistinguishable-Groups.txt"))

        df = pd.read_csv(TEST_FILE_DIR + "/S_Gene_barcodes.csv")

        barcodes = df.iloc[:,0].values.tolist()
        
        self.assertEqual(barcodes, expected_bcs)

        cleanUpFiles()

    #def test_script_noFilt_withInFile(self):


    def test_SublinMap_WholeGenome(self):
        cmd = "python3 {0}/../bin/scripts/update_barcodes_and_collapse.py -i {1} -o {2} -c {3}".format(SCRIPT_DIR, TEST_FILE_DIR + "/test-input-barcodes.csv", TEST_FILE_DIR, TEST_FILE_DIR + "/test-collapse-2-groups.tsv")
        sp.run(cmd, check=True, stdout=sp.PIPE, stderr=sys.stdout, shell=True)

        sublinMap = parseSublinMap(TEST_FILE_DIR + "/sublineage-map.tsv")

        mapKeys = list(sublinMap.keys())
        self.assertEqual(mapKeys, ["Omicron (BA.2.12.1)", "Delta", "Not a VOC"])
        self.assertFalse("B_Sublineages_Like_B" in mapKeys)

        self.assertEqual(findLineageGroup("BA.2.12.1", sublinMap), "Omicron (BA.2.12.1)")
        self.assertEqual(findLineageGroup("AY.1", sublinMap), "Delta")
        self.assertEqual(findLineageGroup("B", sublinMap), "Not a VOC")
        self.assertEqual(findLineageGroup("B.15", sublinMap), "Not a VOC")
        self.assertEqual(findLineageGroup("B.20", sublinMap), "Not a VOC")

        cleanUpFiles()


    def test_SublinMap_SGene(self):
        cmd = "python3 {0}/../bin/scripts/update_barcodes_and_collapse.py -i {1} -o {2} -c {3} --s_gene".format(SCRIPT_DIR, TEST_FILE_DIR + "/test-input-barcodes.csv", TEST_FILE_DIR, TEST_FILE_DIR + "/test-collapse-2-groups.tsv")
        sp.run(cmd, check=True, stdout=sp.PIPE, stderr=sys.stdout, shell=True)

        sublinMap = parseSublinMap(TEST_FILE_DIR + "/sublineage-map.tsv")

        self.assertEqual(list(sublinMap.keys()), ["Omicron (BA.2.12.1)", "Delta", "Not a VOC", "B_Sublineages_Like_B"])

        self.assertEqual(sublinMap["B_Sublineages_Like_B"], ["B", "B.15", "B.20"])
        self.assertEqual(findLineageGroup("B_Sublineags_Like_B", sublinMap), "Not a VOC")
        self.assertEqual(findLineageGroup("BA.2.12.1", sublinMap), "Omicron (BA.2.12.1)")
        self.assertEqual(findLineageGroup("AY.1", sublinMap), "Delta")

        cleanUpFiles()

    #def test_script_withoutInfile(self):
    #    cmd = "python3 {0}/../bin/scripts/update_barcodes_and_collapse.py -o {1} -c {2} --s_gene".format(SCRIPT_DIR, TEST_FILE_DIR, TEST_FILE_DIR + "/test-collapse.tsv")
    #    sp.run(cmd, check=True, stdout=sp.PIPE, stderr=sys.stdout, shell=True)

    #    self.assertTrue(os.path.exists(TEST_FILE_DIR + "/curated_lineages.json"))
    #    self.assertTrue(os.path.exists(TEST_FILE_DIR + "/usher_barcodes.csv"))
    #    self.assertTrue(os.path.exists(TEST_FILE_DIR + "/S_Gene_barcodes.csv"))
    #    self.assertTrue(os.path.exists(TEST_FILE_DIR + "/S_Gene_Unfiltered.csv"))
    #    self.assertTrue(os.path.exists(TEST_FILE_DIR + "/LineageGroups.txt"))

        #os.remove(TEST_FILE_DIR + "/curated_lineages.json")
        #os.remove(TEST_FILE_DIR + "/usher_barcodes.csv")
        #os.remove(TEST_FILE_DIR + "/S_Gene_barcodes.csv")
        #os.remove(TEST_FILE_DIR + "/S_Gene_Unfiltered.csv")
        #os.remove(TEST_FILE_DIR + "/LineageGroups.txt")

if __name__ == "__main__":
    unittest.main(verbosity=2)
