from model import Model
from formulaBuilder import *
from anytree import Node, RenderTree, render

# when using a branching rule, first evaluate a copy subtree for left branch
def copy_subtree(subtree):
    duplicate_formula = subtree
    # TODO: work into actual code

def detach_parent(oper_node):
    for child in oper_node.children:
        child.parent = None

def solve_double_neg(oper, formula_tree):
    detach_parent(oper)
    formula_tree.remove(oper)

def solve_neg(oper, formula_tree):
    detach_parent(oper)
    # set atom to false





# general loop (for now):
# make up a formula
formula_tree = generate_formula(4)          # number subject to change
# loop until tableau complete or a branch closes
# while True:
resolvables = find_roots(formula_tree)
# resolvables_sorted = resolvables.sort(key=lambda x:connectives[x.name])
for n in resolvables:
    render_branch(n)
    # sort available oper/connectives in priority order of resolving
    # priority_order = []
    # for x in range(1,6):
    #     for r in resolvables:
# TODO: wipe out; rework Node as a subclass to include priority tier of operators and state as properties