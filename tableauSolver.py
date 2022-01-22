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

# pass parent's state identifier to children
def inherit_state(oper):
    for child in oper.children:
        child.state = oper.state

# resolve double negation
def solve_double_neg(oper, formula_tree):
    inherit_state(oper)
    detach_parent(oper)
    formula_tree.remove(oper)

# solve negation (only in front of atoms)
def solve_neg(oper, formula_tree, world):
    # if more than 1 child node or more than 1 step away from terminal node
    if len(oper.children) > 1 or oper.height > 1:
        print("separate negation node before not-terminal/non-atom! abort")
        print("child node: ", oper.descendants)
        sys.exit("ERROR")
        # negation in front of non-atom found; should never happen
    inherit_state(oper)
    # check atom's truth valuation in the model
    atom = oper.children[0]
    print(atom.name)
    result = world.access_atom(atom.name, False, atom.state)
    # if contradiction encountered, wipe the branch
    if result == False:
        return -99
    # otherwise, wipe resolved nodes and continue
    else:
        formula_tree.remove(atom)
        formula_tree.remove(oper)
        print(formula_tree)


# sort roots by priority
def priority_sort(el):
    return el.priority


# TODO: operation for erasing branch with return -99
# TODO: add model as argument where appropriate
# TODO: duplicate for branching formulas
# TODO: sidebar for tier-3 operators
# TODO: work in a trigger for discovering new relations and checking sidebar

# general loop (for now):
# make up a formula
#formula_tree = generate_formula(5)          # number subject to change
# for x in range(10):
#     formula_tree.extend(generate_formula(5))
# loop until tableau complete or a branch closes
# while True:

# temp code for testing
formula_tree = []
write_atom(formula_tree, "a")

# initial pass (start of tableau)
root = find_roots(formula_tree)
build_rnd_subformula(formula_tree, "NEG", 1)
root = formula_tree[-1]
# set state 0 for the top connective
root.state = 0
world = Model(2, 2, 1)                  # TODO: automate later
print("initial tree:")
render_branch(root)
solve_neg(root, formula_tree, world)
print("new model state:")
world.print_states()


# for later passes
# resolvables = find_roots(formula_tree)
# resolvables.sort(key=lambda x: x.priority)
# for n in resolvables:
#     render_branch(n)
