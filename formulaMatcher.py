from anytree import Node, LevelOrderIter
from model import Model
from presets import *
from stringConverter import *

# AND, OR, and BI_IMP are symmetric operators and require different approach

# compares formulas to one another
def compare_formulas(old_f, new_f):
    # if the operators match, check their children
    if old_f.name == new_f.name:
        # if this is the end of the branch for both, return
        if old_f.is_leaf and new_f.is_leaf:
            return True
        # if only one of them is the end of the branch, formulas are not equivalent
        elif old_f.is_leaf or new_f.is_leaf:
            return False
        # otherwise, continue comparing formulas
        else:
            # exception for symmetrical operators: need to match in any order
            if new_f.name in ["AND", "NEG_AND", "OR", "NEG_OR", "BI_IMP", "NEG_BI_IMP"]:
                children_comp = []
                # first, compare left child of old formula to both children of the new
                comparison = compare_formulas(old_f.children[0], new_f.children[0])
                children_comp.append(comparison)
                comparison = compare_formulas(old_f.children[0], new_f.children[1])
                children_comp.append(comparison)
                # if neither match, abort
                if children_comp[0] == False and children_comp[1] == False:
                    return False
                # if only one matches, try to match the other children
                elif children_comp[0] == False:
                    comparison = compare_formulas(old_f.children[1], new_f.children[0])
                    return comparison
                elif children_comp[1] == False:
                    comparison = compare_formulas(old_f.children[1], new_f.children[1])
                    return comparison
                # otherwise, both comparisons returned True, so right child of old formula...
                # ..only needs to match one child of new formula
                else:
                    comparison = compare_formulas(old_f.children[1], new_f.children[0])
                    if comparison == True:
                        return True
                    comparison = compare_formulas(old_f.children[1], new_f.children[1])
                    if comparison == True:
                        return True
                    else:
                        return False

            # if operator is not symmetrical
            else:
                counter = 0
                for child in new_f.children:
                    comparison = compare_formulas(old_f.children[counter], child)
                    counter += 1
                    if comparison == False:
                        return False
                # otherwise, all comparisons return True
                return True
    else:
        return False