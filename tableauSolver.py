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


# sort roots by priority
def priority_sort(el):
    return el.priority



# general loop (for now):
# make up a formula
formula_tree = generate_formula(5)          # number subject to change
# for x in range(10):
#     formula_tree.extend(generate_formula(5))
# loop until tableau complete or a branch closes
# while True:
resolvables = find_roots(formula_tree)
resolvables.sort(key=lambda x: x.priority)
for n in resolvables:
    render_branch(n)
