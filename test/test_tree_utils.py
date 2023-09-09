import os
from re import A
import sys
import json
import unittest
import pandas as pd
import subprocess as sp
from treelib import Node, Tree

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_FILE_DIR = SCRIPT_DIR + "/tree-utils-test-files"

from bin.scripts.tree_utils import addLineagesToTree, addWithdrawnLineagesToTree, checkLineageExists, commonAncestor, convertLongAlias, getCommonLineageParent, getLineagesInTree, getParentLineage, getSubLineages, parseParentFromLineage

aliases = json.load(open(TEST_FILE_DIR + "/alias_key.json"))


def getLineageList():
    lineageFile = open(TEST_FILE_DIR + "/test-lineages.txt", "r")

    lineages = []
    for line in lineageFile:
        lineages.append(line.strip())

    lineageFile.close()

    return lineages

def getWithdrawnLines():
    withdrawnFile = open(TEST_FILE_DIR + "/test-withdrawn.txt", "r")

    lines = []
    for line in withdrawnFile:
        lines.append(line.strip())

    withdrawnFile.close()

    return lines


class TestLineageTreeUtils(unittest.TestCase):

    def test_checkLineageExists(self):

        t = Tree()
        t.create_node("root", "root")
        t.create_node("test1", "test1", parent="root")
        t.create_node("test2", "test2", parent="root")

        self.assertTrue(checkLineageExists(t, "test1"))
        self.assertTrue(checkLineageExists(t, "test2"))
        self.assertFalse(checkLineageExists(t, "doesNotExist"))
    
    def test_getParentLineage_valid(self):
        t = Tree()
        t.create_node("root", "root")
        t.create_node("B", "B", parent="root")
        t.create_node("B.1", "B.1", parent="B")
        t.create_node("B.1.1", "B.1.1", parent="B.1")
        t.create_node("B.2", "B.2", parent="B")

        self.assertEqual(getParentLineage(t, "B.1"), "B")
        self.assertEqual(getParentLineage(t, "B.1.1"), "B.1")
        self.assertEqual(getParentLineage(t, "B.2"), "B")

    def test_getParentLineage_invalid(self):
        t = Tree()
        t.create_node("root", "root")
        t.create_node("B", "B", parent="root")
        t.create_node("B.1", "B.1", parent="B")
        t.create_node("B.1.1", "B.1.1", parent="B.1")
        t.create_node("B.2", "B.2", parent="B")

        self.assertEqual(getParentLineage(t, "A"), None)

    def test_getSubLineages_valid(self):
        t = Tree()
        t.create_node("root", "root")
        t.create_node("B", "B", parent="root")
        t.create_node("B.1", "B.1", parent="B")
        t.create_node("B.1.1", "B.1.1", parent="B.1")
        t.create_node("B.2", "B.2", parent="B")

        self.assertEqual(getSubLineages(t, "B"), ["B.1", "B.1.1", "B.2"])
        self.assertEqual(getSubLineages(t, "B.1"), ["B.1.1"])
        self.assertEqual(getSubLineages(t, "B.2"), None)

    def test_getSubLineages_invalid(self):
        t = Tree()
        t.create_node("root", "root")
        t.create_node("B", "B", parent="root")
        t.create_node("B.1", "B.1", parent="B")
        t.create_node("B.1.1", "B.1.1", parent="B.1")
        t.create_node("B.2", "B.2", parent="B")

        self.assertEqual(getSubLineages(t, "A"), None)

    def test_getLineagesInTree(self):
        t = Tree()
        t.create_node("root", "root")
        t.create_node("B", "B", parent="root")
        t.create_node("B.1", "B.1", parent="B")
        t.create_node("B.1.1", "B.1.1", parent="B.1")
        t.create_node("B.2", "B.2", parent="B")

        self.assertEqual(getLineagesInTree(t), ["root", "B", "B.1", "B.1.1", "B.2"])
    
    def test_commonAncestor(self):
        t = Tree()
        t.create_node("root", "root")
        t.create_node("B", "B", parent="root")
        t.create_node("B.1", "B.1", parent="B")
        t.create_node("B.1.1", "B.1.1", parent="B.1")
        t.create_node('B.1.2', "B.1.2", parent="B.1")
        t.create_node("B.1.1.1", "B.1.1.1", parent="B.1.1")
        t.create_node("B.2", "B.2", parent="B")
        t.create_node("B.2.1", "B.2.1", parent="B.2")

        self.assertEqual(commonAncestor(t, "B.1.1", "B.1.2"), "B.1")
        self.assertEqual(commonAncestor(t, "B.1.1.1", "B.1.1"), "B.1.1")
        self.assertEqual(commonAncestor(t, "B.1.1", "B.2"), "B")
        self.assertEqual(commonAncestor(t, "B.1.1", "B.2.1"), "B")

    def test_getCommonLineageParent_allValid(self):
        t = Tree()
        t.create_node("root", "root")
        t.create_node("B", "B", parent="root")
        t.create_node("B.1", "B.1", parent="B")
        t.create_node("B.1.1", "B.1.1", parent="B.1")
        t.create_node('B.1.2', "B.1.2", parent="B.1")
        t.create_node("B.1.1.1", "B.1.1.1", parent="B.1.1")
        t.create_node("B.2", "B.2", parent="B")
        t.create_node("B.2.1", "B.2.1", parent="B.2")

        self.assertEqual(getCommonLineageParent(t, ["B.1.1.1", "B.1.1", "B.1.2"]), "B.1")
        self.assertEqual(getCommonLineageParent(t, ["B.1", "B.1.1", "B.1.2"]), "B.1")
        self.assertEqual(getCommonLineageParent(t, ["B.1", "B.2.1", "B.2"]), "B")

    def test_getCommonLineageParent_someInvalid(self):
        t = Tree()
        t.create_node("root", "root")
        t.create_node("B", "B", parent="root")
        t.create_node("B.1", "B.1", parent="B")
        t.create_node("B.1.1", "B.1.1", parent="B.1")
        t.create_node('B.1.2', "B.1.2", parent="B.1")
        t.create_node("B.1.1.1", "B.1.1.1", parent="B.1.1")
        t.create_node("B.2", "B.2", parent="B")
        t.create_node("B.2.1", "B.2.1", parent="B.2")

        self.assertEqual(getCommonLineageParent(t, ["B.1.1.1", "B.1.1", "A"]), "B.1.1")
        self.assertEqual(getCommonLineageParent(t, ["B.1", "A", "B.1.2"]), "B.1")
        self.assertEqual(getCommonLineageParent(t, ["A", "B.2.1", "B.2"]), "B.2")

    def test_convertLongAlias_valid(self):
        linW4Characters = "B.1.1.529.1"

        linW7Characters = "B.1.1.529.5.3.1.5"

        self.assertEqual(convertLongAlias(linW4Characters, aliases), "BA.1")
        self.assertEqual(convertLongAlias(linW7Characters, aliases), "BE.5")

    def test_convertLongAlias_invalid(self):
        linW4Characters = "B.2.2.2.2"

        linW7Characters = "B.2.2.2.2.2.2.2"

        self.assertEqual(convertLongAlias(linW4Characters, aliases), None)
        self.assertEqual(convertLongAlias(linW7Characters, aliases), None)

    def test_parseParentFromLineage_valid(self):
        linWrootParent = "B"
        normalLin1 = "B.1"
        normalLin2 = "B.1.117.3"
        linWAlias = "BA.1"
        linWNestedAlias = "BE.1"
        linWLongNestedAlias = "CW.1"

        self.assertEqual(parseParentFromLineage(linWrootParent, aliases), "root")
        self.assertEqual(parseParentFromLineage(normalLin1, aliases), "B")
        self.assertEqual(parseParentFromLineage(normalLin2, aliases),"B.1.117")
        self.assertEqual(parseParentFromLineage(linWAlias, aliases), "B.1.1.529")
        self.assertEqual(parseParentFromLineage(linWNestedAlias, aliases), "BA.5.3.1")
        self.assertEqual(parseParentFromLineage(linWLongNestedAlias, aliases), "BQ.1.1.14")

    def test_parseParentFromLineage_invalid(self):
        linWNoExistingAlias = "GG.5"

        self.assertEqual(parseParentFromLineage(linWNoExistingAlias, aliases), "invalid")

    
    def test_addLineagesToTree_inOrder(self):
        lineages = ["B", "B.1", "XA", "XA.1", "B.2", "XC", "B.3", "LL.5", "B.1.1", "F.1", "B.1.1.529", "BA.5"]

        t = Tree()
        t.create_node("root", "root")

        t, invalid = addLineagesToTree(t, lineages, aliases)

        self.assertTrue(checkLineageExists(t,"B.1"))
        self.assertTrue(checkLineageExists(t,"B.2"))
        self.assertTrue(checkLineageExists(t,"B.3"))
        self.assertTrue(checkLineageExists(t,"B"))
        self.assertTrue(checkLineageExists(t,"B.1.1"))
        self.assertTrue(checkLineageExists(t,"B.1.1.529"))
        self.assertTrue(checkLineageExists(t,"BA.5"))
        self.assertTrue(checkLineageExists(t,"XA"))
        self.assertTrue(checkLineageExists(t,"XA.1"))
        self.assertTrue(checkLineageExists(t,"XC"))

        self.assertTrue(getParentLineage(t,"B"), "root")
        self.assertTrue(getParentLineage(t,"B.1"), "B")
        self.assertTrue(getParentLineage(t,"B.2"), "B")
        self.assertTrue(getParentLineage(t,"B.3"), "B")
        self.assertTrue(getParentLineage(t,"B.1.1"), "B.1")
        self.assertTrue(getParentLineage(t,"B.1.1.529"), "B.1.1")
        self.assertTrue(getParentLineage(t,"BA.5"), "B.1.1.529")
        self.assertTrue(getParentLineage(t,"XA"), "root")
        self.assertTrue(getParentLineage(t,"XA.1"), "XA")
        self.assertTrue(getParentLineage(t,"XC"), "root")

        self.assertFalse(checkLineageExists(t, "F.1"))
        self.assertFalse(checkLineageExists(t, "LL.5"))

        self.assertEqual(invalid, ["LL.5","F.1"])

    def test_addLineagesToTree_outOfOrder(self):
        lineages = ["BA.5", "LL.5", "B.1", "XA", "B.2", "B.1.1.529", "XC", "B.3", "B.1.1", "B", "F.1", "XA.1"]

        t = Tree()
        t.create_node("root", "root")

        t, invalid = addLineagesToTree(t, lineages, aliases)

        self.assertTrue(checkLineageExists(t,"B.1"))
        self.assertTrue(checkLineageExists(t,"B.2"))
        self.assertTrue(checkLineageExists(t,"B.3"))
        self.assertTrue(checkLineageExists(t,"B"))
        self.assertTrue(checkLineageExists(t,"B.1.1"))
        self.assertTrue(checkLineageExists(t,"B.1.1.529"))
        self.assertTrue(checkLineageExists(t,"BA.5"))
        self.assertTrue(checkLineageExists(t,"XA"))
        self.assertTrue(checkLineageExists(t,"XA.1"))
        self.assertTrue(checkLineageExists(t,"XC"))

        self.assertTrue(getParentLineage(t,"B"), "root")
        self.assertTrue(getParentLineage(t,"B.1"), "B")
        self.assertTrue(getParentLineage(t,"B.2"), "B")
        self.assertTrue(getParentLineage(t,"B.3"), "B")
        self.assertTrue(getParentLineage(t,"B.1.1"), "B.1")
        self.assertTrue(getParentLineage(t,"B.1.1.529"), "B.1.1")
        self.assertTrue(getParentLineage(t,"BA.5"), "B.1.1.529")
        self.assertTrue(getParentLineage(t,"XA"), "root")
        self.assertTrue(getParentLineage(t,"XA.1"), "XA")
        self.assertTrue(getParentLineage(t,"XC"), "root")

        self.assertFalse(checkLineageExists(t, "F.1"))
        self.assertFalse(checkLineageExists(t, "LL.5"))

        self.assertEqual(invalid, ["LL.5", "F.1"])

    def test_addWithDrawnLineagesToTree(self):
        t = Tree()
        t.create_node("root", "root")

        linsToAdd = getLineageList()
        withdrawnToAdd = getWithdrawnLines()

        t, invalid = addLineagesToTree(t, linsToAdd, aliases)

        t, invalidWithdrawn = addWithdrawnLineagesToTree(t, withdrawnToAdd, aliases, False)

        self.assertTrue(checkLineageExists(t, "B.2.1"))
        self.assertTrue(checkLineageExists(t, "B.2.6"))
        self.assertTrue(checkLineageExists(t, "C.15"))
        self.assertTrue(checkLineageExists(t, "B.1.1.2"))

        self.assertTrue(getParentLineage(t, "B.2.1"), "B.40")
        self.assertTrue(getParentLineage(t, "B.2.6"), "B.35")
        self.assertTrue(getParentLineage(t,"C.15"), "B.1.1.1")
        self.assertTrue(getParentLineage(t,"B.1.1.2"), "B.1.1")

        self.assertFalse(checkLineageExists(t, "GG.2"))

        self.assertEqual(invalidWithdrawn, ["GG.2"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
