import sys
import os
from treelib import Node, Tree
import urllib.request as ur
import json
import re

def checkLineageExists(tree, lin):
    """ Determines whether a lineage exists in
    a given tree
    
    Parameters:
        tree: a tree object containg SARS-CoV-2 Lineages
        lin: the desired lineage to be searched

    Output:
        If the lineage is found in the tree, True
        If the lineage is not found in the tree, False
    """

    # Uses the get_node method of the tree 
    # to search for a node with the id
    # matching the given lineage
    if tree.get_node(lin):
        # If a node is found, return true
        return True
    else:
        # If no node is found, return false
        return False

def getParentLineage(tree, lin):
    """ Grabs the parent lineage for a
    given lineage node

    Parameters:
        tree: a tree object containing SARS-CoV-2 Lineages
        lin: a SARS-CoV-2 lineage

    Output:
        The parent lineage of the provided lineage if it exists
        in the tree. None if the provided lineage does not exist
        in the tree
    """
    
    parent = None
    
    # First checks whether the lineage provided 
    # exists within the tree
    if checkLineageExists(tree,lin):
        # Uses the parent function of the tree library
        # to grab the parent node of the node for the given lineage
        parentNode = tree.parent(lin)
        # The lineage name of the parent node is
        # stored in the identifier attribute
        parent = parentNode.identifier

    # Returns the lineage name of the parent if 
    # if the lineage existed, or None if it does not
    return parent

def getSubLineages(tree, lin):
    """ A recursive method that retreives
    all of the sublineages of a given lineage.

    Parameters:
        tree: a tree containing SARS-CoV-2 lineages
        lin: a lineage whose sublineages are desired.

    Output:
        A list containing the lineage's sublineages if the 
        lineage exists within the tree. None if the lineage
        does not exist or has no children
    """

    # Creates an empty list to store the sublineages
    subLins = []

    # First, checks whether the provided lineage exists
    # within the tree.
    if checkLineageExists(tree, lin):

        # If the lineage does exist, find its children

        # Uses the get_node() to grab the 
        # node corresponding to the provided lineage
        # on the tree.
        n = tree.get_node(lin)

        # Uses the children() function to grab
        # the children of the node.
        childNodes = tree.children(n.identifier)

        # Because of the structure of a tree,
        # the children method only grabs the immediate chidlren of
        # the node, but the complete list of sublineages also
        # considers the sublineages of those children. 
        # 
        # Thus, if there are children nodes, we need to grab their sublineages as well.
        if len(childNodes) > 0:

            # Loops over the child nodes.
            for c in childNodes:

                # Adds the child's lineags to the list of sublineages
                subLins.append(c.identifier)

                # Grabs the sublineages of the child
                cChildren = getSubLineages(tree, c.identifier)

                # Checks whether the sublineages of the
                # child contains any lienages.
                if cChildren != None:
                    # If so, extend the list of sublineages to
                    # include the child's sublineages
                    subLins.extend(cChildren)

        # If there are no child nodes, set the list of sublineages
        # to "None"
        else:
            subLins = None
    else:
        subLins = None

    # Return the list of sublineages
    return subLins

def getLineagesInTree(tree):
    """ Grabs a list of all lineages present in a given tree

    Parameters:
        t: the tree object to be searched
    
    Output:
        A list containing lineages present in the tree

    """

    # Use the expand_tree function to get a list
    # of all nodes in the tree
    nodes = tree.expand_tree(mode=Tree.DEPTH)

    # Creates a list to store the lineage names
    # of the tree nodes.
    lineages = []
    
    # Loops over every node from the tree and
    # adds the identifier to the list of lineages
    for n in nodes:
        lineages.append(tree[n].identifier)

    # Returns the list of lineages
    return lineages

def commonAncestor(tree, lin1, lin2):
    """ Identifies the common parent of two lineages provided.

    The method identifies which node is lower depth-wise
    down the tree, traverses up the parents until it is
    at the same depth as the other node, and then traverses up
    both until the nodes are equal.

    Parameters:
        tree: A tree containing SARS-CoV-2 lineages
        lin1: one of the lineages to be compated.
        lin2: one of the lineages to be compared.
    """

    # Uses the get_node() method to grab
    # the tree node for the lineages provided.
    n1 = tree.get_node(lin1)
    n2 = tree.get_node(lin2)

    # Creates empty variables to store the higher
    # and lower nodes.
    lower = ''
    higher = ''

    # Uses the depth() function to identify which
    # node is lower down on the tree.
    if tree.depth(n1) > tree.depth(n2):
        lower = n1
        higher = n2
    else:
        lower = n2
        higher = n1

    
    # Traverses up the parents of the lineage lower
    # down on the tree until it has the same depth as
    # the higher one.
    while tree.depth(lower) != tree.depth(higher):
        lower = tree.parent(lower.identifier)

    # Traverse up the parents of both lineages until
    # the same node is reached. This node is
    # the nearest common parent.
    while lower != higher:
        lower = tree.parent(lower.identifier)
        higher = tree.parent(higher.identifier)

    # Return the identifier (the lineage name) of the
    # common parent node.
    return lower.identifier

def getCommonLineageParent(tree, lins):
    """ Identifies the common parent of
    all lineages present in a list by recursively 
    truncating the list until only two lineages remain.

    Parameters:
        tree: a tree containing SARS-CoV-2 lineages
        lins: a list of lineages
        unknownLins: a list of lineages not found on the tree.

    Output:
        The common parent of the sublineages.
    """

    parent = ''

    # If there are only two lineages provided,
    # we need to check whether one or both lineages exists in 
    # the tree.
    if len(lins) == 2:

        # If both lineages do not exist,set the parent to None
        if checkLineageExists(tree, lins[0]) == False and checkLineageExists(tree, lins[1]) == False:
            parent = "None"
        # If the first lineage does not exist, but the second does, set the parent to
        # the second lineage
        elif checkLineageExists(tree, lins[0]) == False and checkLineageExists(tree, lins[1]) == True:
            parent = lins[1]
        # If the second lineage does not exist, but the first does, set the parent to
        # the first lineage
        elif checkLineageExists(tree, lins[0]) == True and checkLineageExists(tree, lins[1]) == False:
            parent = lins[0]
        # If both lineages exist, set the parent to the common ancestor.
        else:
            parent = commonAncestor(tree, lins[0], lins[1])
    
    # If there are more than two lineages in the list.
    else:

        # Find the common parent lineage of the list without the first value.
        previousParent = getCommonLineageParent(tree, lins[1:])

        # If both the parent of the previous two lineages was "None" and the
        # current lineage do not exist in the tree, set the parent
        # to "None" 
        if checkLineageExists(tree, lins[0]) == False and previousParent == "None":
            parent = "None"
        # If the current lineage does not exist in the tree, and the previous parent is
        # not "None" (it was a valid lineage), set the parent to the previous parent 
        elif checkLineageExists(tree, lins[0]) == False and previousParent != "None":
            parent = previousParent
        # If the current lineage exists and the previous parent equals "None", set
        # the parent to the current lineage
        elif checkLineageExists(tree, lins[0]) == True and previousParent == "None":
            parent = lins[0]
        # Both the previous parent and the current lineage exist in the tree, so find the
        # common parent
        else:
            parent = commonAncestor(tree, lins[0], previousParent)

    # Return the parent lineage.
    return parent

def convertLongAlias(lin, aliases):
    """ Takes an unaliased lineage and converts it to the aliased name. Aliasing is
    done to shorten the names of long lineages. The alias replaces the first 
    3 or 6 numbers in a lineage with letters (Ex: BA.5 = B.1.1.529.5).

    Parameters:
        lin: the lineage to be aliased
        aliases: a dictionary mapping an alias to a given lineage

    Output:
        The aliased equivalent of the provided lineage
    """

    # Splits the given lineage into a list at each '.' character
    split = lin.split(".")

    # Because an alias replaces the first 4 or 7 characters (single letter + 3/6 numbers),
    # we just need to find the alias corresponding to these characters
    # and tack on the extra characters. 
    aliasedLineage = None
    if len(split) > 7:
        # If the lineage has more than 7 characters,
        # concatenate the first 7 characters into a string, 
        # and identify the corresponding alias.

        aliasedLineage = None

        # Loops over every alias in the dictionary
        for a in aliases.keys():
            # If the first 7 characters of the lineage = the alias' lineage
            if ".".join(split[:7]) == aliases[a]:

                # Concatenate the alias with the remaining characters
                aliasedLineage =  a + "." + ".".join(split[7:])

    elif len(split) > 4:
        # If the lineage has more than 4 characters but less than 7
        # concatenate the first 4 characters into a string, 
        # and identify the corresponding alias.

        aliasedLineage = None
        # Loops over every alias in the dictionary
        for a in aliases.keys():

            # If the first 7 characters of the lineage = the alias' lineage
            if ".".join(split[:4]) == aliases[a]:

                # Concatenate the alias with the remaining characters
                aliasedLineage =  a + "." + ".".join(split[4:])
    # If the lineage contains 4 characters or less, there is no need
    # to alias it.
    else:
        aliasedLineage = lin
    
    # Return the aliased (or not if <= 4 characters) lineage
    return aliasedLineage

def parseParentFromLineage(l, aliases):
    """ Determines the parent of a given lineage based
    on the lineage's name (not from a tree). Lineages are named in a heirarchical manner 
    (Ex: B.1 is the parent of B.1.1), so this can be used in many cases.
    However, aliasing also occurs to prevent lengthy lineage names (Ex: BA.5 = B.1.1.529.5). The data
    file where the lineages are obtained from presents the lineages in their aliased format if their
    names were to be longer then 4 characters. Aliasing presents an interesting case where the parent
    of a lineages that has just been aliased (i.e. BA.5) will not contain the alias (Ex: B.1.1.529 is the parent of BA.5). 
    Thus, we need to consider the alias/unaliased forms of the lineages when determining the variant parent.

    Parameters:
        l: a SARS-CoV-2 lineage
        aliases: a dictionary mapping an aliase to a corresponding lineage.
    Output:
        The parent lineage name
    """

    # Splits the lineage into a list of component characters
    # at the '.' characters.
    splitLineage = l.split(".")

    # Special Case: If the lineage is B or A, the parent will be
    # the tree root node.
    if l == "B" or l =='A':
        parent = "root"
    # If the length of the lineage is two, we need to check for an alias.
    # The linaege may not need to be dealiased, as in the case of B.1, or it may
    # as in the case of BA.2 where the parent is B.1.1.529 (this is the lineage given
    # in the tree).
    elif len(splitLineage) == 2:
        # The first set of characters in the lineage name will always contain an alias
        # if one is present.
        alias = splitLineage[0]

        # Checks to see whether the alias is present in the dictionary
        if alias in aliases.keys():
            # If the alias is present, grab the dealised lineage, which is the
            # value in the alias dictionary.
            dealiased = aliases[alias]
            
            # 'B' and 'A' map to "" in the alias diciontary as they are not
            # an alias to any lineages. Thus, the parent will be B or A lineage 
            # themselves.
            if dealiased == "":
                # the parent of thse lineages will be the first
                # character (B or A)
                parent = splitLineage[0]
            else:
                # Now, an alternative case arises. As linaeges grow longer,
                # aliases can represent up to 7 sets of characters (Ex:
                # BC = B.1.1.529.1.1.1). However, these lienages themselves 
                # contain a set of characters that can be aliased (B.1.1.529.1.1.1 -> BA.1.1.1).
                # The parent node in the tree will be the aliased version, thus we need to realias,
                # the dealiased parent.
                parent = convertLongAlias(dealiased, aliases)
        else:
            # If the alias does not exist in the alias dictionary, the lineage is invalid.
            # Thus, we will return the word invalid.
            parent = "invalid"
    else:
        # If a lineage cotains greater than two sets of characters, there is no need to
        # convert between aliases. Because the lineages are already aliased, we do not have to
        # worry getting lineages longer than 7 sets of characters. And, the parent of these lineages will exist in its 
        # aliased form within the tree.
        
        #Thus, we can return the the lineage minus its last set of characters.
        parent = ".".join(splitLineage[:-1])

    # Return the parent.
    return parent

def addLineagesToTree(tree, lineages, aliases):
    # Create a list to store invalid lineages (those that do not have a valid parent lineage)
    invalid = []

    # Loop over the list of lineages, removing those that were added to the tree or deemed invalid.
    while len(lineages) > 0:

        # Grab the lineage at the start of the list.
        l = lineages[0]

        # Recominant lineages begin with X, so if the lineage does
        # not begin with 'X' we will add it to the tree
        if l[0] != "X":

            # First, we identify the lineage's parent.
            parent = parseParentFromLineage(l, aliases)

            # If the function returned 'invalid' as the parent,
            # add the lineage to the list of invalid lineages.
            if parent == "invalid":
                invalid.append(l)
            # If the parent is valid, we then need to see if check if the parent lienage is
            # already placed in the tree.
            elif checkLineageExists(tree, parent) == False:
                
                # If the parent is not in the tree, there are two potentials:
                # The lineage could be invalid or the parent is present in the list of lineages
                # has not been added to the tree yet.

                # If the lineage is not invalid, then the parent likely has not been added
                # yet. So we can simply add the lineage to the end of the list and
                # return to it later.
                if l not in invalid:
                    lineages.append(l)
            # If the parent lineage is already present in the tree, we 
            # can add the lineage.
            else:
                tree.create_node(l, l, parent)
        else:
            invalid.append(l)

        # Removes the lineage from the front of the list.
        lineages.pop(0)

    return tree, invalid


def addWithdrawnLineagesToTree(tree, withdrawnLines, aliases):
    # For the withdrawn lineages, there are cases when the lineage
    # does not have an existing parent (even among the withdrawn lineage).
    # Instead of just removing these linages we can grab the lineage that it
    # was reclassified as or an alias of from the description and place
    # the withdrawn lineage under that on the tree.
    #
    # This regex pattern matches the format of a lineage.
    lineageRegexPattern = r"(\w{1,3}(?:\.\d+)+)"
    
    invalid = []

    # Loops over the list of withdrawn lineages
    for w in withdrawnLines:
        # Because the withdrawn lineages still have the information
        # associated with them. We need to separate the two. As well,
        # we need to remove the '*' character from the lineage.
        lineage = w.split("\t")[0].replace("*", "")
        info = w.split("\t")[1]

        # Now, we can try to grab the parent given the lineage.
        parent = parseParentFromLineage(lineage, aliases)

        # There are cases where a lineage is listed both as existing and withdrawn.
        # Thus, if the lineage exists, we need to skip this.
        if checkLineageExists(tree, lineage):
            pass # Do nothing - left this case if future addition is needed

        # We also need to check whether the parent lineage exists.
        #
        # If not, we can check whether a related lineage is present in the description,
        elif checkLineageExists(tree, parent) == False:
            
            # searches for a match for the lineage regex pattern in the
            # lineage information.
            lineageResult = re.search(lineageRegexPattern, info)
            
            # Check whether the regex found a match
            if lineageResult:
                
                # If a match was found, check whether the linage in the decription
                # is already present in the tree.
                if checkLineageExists(tree, lineageResult.group(1)):
                    
                    # If the lineage was found, we can use this as the parent for
                    # the withdrawn lineage.
                    parent = lineageResult.group(1)
                    tree.create_node(lineage, lineage, parent)
                else:
                    
                    # If the lineage was not found in the tree, we can find what would
                    # be the parent of that lineage and add the withdrawn lineage under that.
                    equivalentParent = parseParentFromLineage(lineageResult.group(1), aliases)
                    tree.create_node(lineage, lineage, equivalentParent)
           
            # If the regex pattern did not match, add the withdrawn lineage to the 
            # list of invalid lineages.
            else:
                invalid.append(lineage)
        
        # If the parent lineage obtained from the withdrawn lineage does exist,
        # we can add the withdrawn lineage directly to the tree.
        else:
            tree.create_node(lineage, lineage, parent)

    return tree, invalid