from binhex import openrsrc
from model import Model
from formulaBuilder import *
from anytree import Node, RenderTree
import sys

# when using a branching rule, first evaluate a copy subtree for left branch
def copy_subtree(subtree, world):
    duplicate_formula = subtree
    duplicate_world = world
    # TODO: work into actual code
    return duplicate_formula, duplicate_world

# sever parent-child association between nodes
def detach_parent(oper_node):
    for child in oper_node.children:
        child.parent = None

# insert new node between parent and child
def insert_node(new_node, parent_node, child_node):
    new_node.parent = parent_node
    child_node.parent = new_node

# pass parent's state identifier to children (we stay in the same state)
def inherit_state(oper):
    for child in oper.children:
        child.state = oper.state

# PRIORITY TIER 0
# resolve an atom at the end of a branch
def solve_atom(atom, formula_tree, world):
    if atom.height != 0:
        print("single atom at non-terminal node!\n function solve_atom")
        sys.exit("ATOM ERROR")
    result = world.access_atom(atom.name, True, atom.state)
    if result == False:
        return -99
    else:
        formula_tree.remove(atom)
        print(formula_tree)

# PRIORITY TIER 1
# resolve double negation
def solve_double_neg(oper, formula_tree):
    # if formula branches after double negation node, abort
    if len(oper.children) > 1:
        print("more than one child of DOUBLE_NEG node!")
        render_branch(oper)
        sys.exit("DOUBLE NEG ERROR")
    inherit_state(oper)
    detach_parent(oper)
    formula_tree.remove(oper)

# solve negation (only in front of atoms)
def solve_neg(oper, formula_tree, world):
    # if more than 1 child node or more than 1 step away from terminal node
    if len(oper.children) > 1 or oper.height > 1:
        print("separate negation node before not-terminal/non-atom! abort")
        print("child node: ", oper.descendants)
        sys.exit("NEG ERROR")
        # negation in front of non-atom found; should never happen
    inherit_state(oper)
    # check atom's truth valuation in the model
    atom = oper.children[0]
    result = world.access_atom(atom.name, False, atom.state)
    # if contradiction encountered, wipe the branch
    if result == False:
        return -99
    # otherwise, wipe resolved nodes and continue
    else:
        formula_tree.remove(atom)
        formula_tree.remove(oper)
        print(formula_tree)

# PRIORITY TIER 2
# resolve AND operators
def solve_and(oper, formula_tree):
    # if AND operator is misapplied
    if len(oper.children) != 2:
        print("binary operator with wrong number of children!")
        render_branch(oper)
        sys.exit("AND ERROR")
    inherit_state(oper)
    detach_parent(oper)
    formula_tree.remove(oper)

# resolve NOT-OR operator
def solve_neg_or(oper, formula_tree):
    if len(oper.children) != 2:
        print("binary operator with wrong number of children!")
        render_branch(oper)
        sys.exit("NEG-OR ERROR")
    # apply negation to both child-nodes
    for child in oper.children:
        neg_node = make_neg(formula_tree, "NEG", child)
        if neg_node != 0:
            insert_node(neg_node, oper, child)
    inherit_state(oper)
    detach_parent(oper)
    formula_tree.remove(oper)

# resolve NOT-IMPLIES operator
def solve_neg_imp(oper, formula_tree):
    if len(oper.children) != 2:
        print("binary operator with wrong number of children!")
        render_branch(oper)
        sys.exit("NEG-IMP ERROR")
    # 'a does not imply b' means 'a and not-b'
    right_child = oper.children[1]
    new_neg = make_neg(formula_tree, "NEG", right_child)
    if new_neg != 0:
        insert_node(new_neg, oper, right_child)
    inherit_state(oper)
    detach_parent(oper)
    formula_tree.remove(oper)


# sort roots by priority
def priority_sort(el):
    return el.priority

# general action choice loop
def solver_loop(formula_tree, world):
    resolvables = find_roots(formula_tree)
    resolvables.sort(key=lambda x: x.priority)
    print("\ncurrent available roots in order:")
    for n in resolvables:
        render_branch(n)
    oper_name = resolvables[0].name
    # if highest priority root is a lone atomic predicate
    if resolvables[0].type == "atom":
        solve_atom(resolvables[0], formula_tree, world)
    # otherwise, it must be an operator
    elif oper_name == "DOUBLE_NEG":
        solve_double_neg(resolvables[0], formula_tree)
    elif oper_name == "NEG":
        solve_neg(resolvables[0], formula_tree, world)
    elif oper_name == "AND":
        solve_and(resolvables[0], formula_tree)
    elif oper_name == "NEG_OR":
        solve_neg_or(resolvables[0], formula_tree)
    elif oper_name == "NEG_IMP":
        solve_neg_imp(resolvables[0], formula_tree)
    # sidebar used here


# TODO: operation for erasing branch with return -99
# TODO: duplicate for branching formulas
# TODO: sidebar for tier-3 operators -- work in usage
# TODO: trigger for checking old K and not-M formulas upon discovering new relations

# general loop (for now):
# make up a formula
#formula_tree = generate_formula(5)          # number subject to change
# for x in range(10):
#     formula_tree.extend(generate_formula(5))
# loop until tableau complete or a branch closes
# while True:

# temp code for testing
formula_tree = []
# sidebar is where we put formulas that might be expanded again later
# if a new accessibility relation is discovered
sidebar = []
write_atom(formula_tree, "a")

# initial pass (start of tableau)
build_rnd_subformula(formula_tree, "NEG", 1)
write_atom(formula_tree, "b")
roots = find_roots(formula_tree)
make_bin_con(formula_tree, "NEG_OR", roots[0], roots[1])
roots = find_roots(formula_tree)
# set state 0 for the top connective
for root in roots:
    root.state = 0
world = Model(2, 2, 1)                  # TODO: automate
print("initial tree:")
render_branch(root)
solve_neg_or(root, formula_tree)
# solve_neg(roots[0], formula_tree, world)
roots = find_roots(formula_tree)
for root in roots:
    render_branch(root)
print("\ncurrent model state:")
world.print_states()
# solve_atom(formula_tree[-1], formula_tree, world)
# print("current model state:")
# world.print_states()
