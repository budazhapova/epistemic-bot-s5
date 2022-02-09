from model import Model
from formulaBuilder import *
from anytree import Node, RenderTree
import sys

# when using a branching rule, first evaluate a copy subtree for left branch
# TODO: reevaluate!
def copy_subtree(subtree, world):
    duplicate_formula = subtree
    duplicate_world = world
    # TODO: work into actual code
    return duplicate_formula, duplicate_world

# sever parent-child association between nodes
def detach_parent(oper_node):
    for child in oper_node.children:
        child.parent = None

# insert new negation node between parent and child
def insert_neg_node(parent_node, child_node, formula_tree):
    neg_node = make_neg(formula_tree, "NEG", child_node)
    if neg_node != 0:
        neg_node.parent = parent_node
        child_node.parent = neg_node

# remove a node from the middle of branch and knit the edges
def remove_branch_node(parent_node, middle_node, formula_tree):
    state_id = parent_node.state
    successor = middle_node.children[0]
    # pass state to child node
    confer_state(successor, state_id)
    # change branch structure
    middle_node.parent = None
    successor.parent = parent_node
    # erase the middle node
    formula_tree.remove(middle_node)

# pass parent's state identifier to children (we stay in the same state)
def inherit_state(oper):
    for child in oper.children:
        child.state = oper.state

# TODO: remove if redundant
# set children's state to new_state
def confer_state(oper, new_state):
    for child in oper.children:
        child.state = new_state

# remove epistemic operator nodes from tree
def remove_epist_op(epist_op, new_state, formula_tree):
    for child in epist_op.children:
        if child.type == "agent":
            formula_tree.remove(child)
        else:
            child.state = new_state
            child.parent = None
    formula_tree.remove(epist_op)

# triggers when new relation has been discovered
def trigger_sidebar(agent, old_state, new_state, world):
    if not world.check_relations(old_state, agent):
        sys.exit("TRIGGER ERROR. no relations found")
    # TODO: trigger sidebar

# PRIORITY TIER 0
# resolve an atom at the end of a branch
def solve_atom(atom, world):
    if atom.height != 0:
        print("single atom at non-terminal node!\n function solve_atom")
        sys.exit("ATOM ERROR")
    result = world.access_atom(atom.name, True, atom.state)
    if result == False:
        return -99
    else:
        world.formula_tree.remove(atom)
        # print(formula_tree)

# PRIORITY TIER 1
# TODO: test this implementation or just straigh-up removing next
# resolve multiple negations
def solve_multi_neg(node, neg_count):
    # if current node has more than 1 child, stop
    if len(node.children) > 1:
        return node
    # recursively count how many negations in a row there are
    for child in node.children:
        if child.name == "DOUBLE_NEG":
            neg_count += 2
            solve_multi_neg(child, neg_count)
        elif "NEG" in child.name:
            neg_count += 1
            solve_multi_neg(child, neg_count)

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
def solve_neg(oper, world):
    # if more than 1 step away from terminal node, there are multiple negations
    if oper.height > 1:
        # if next node is double negation, remove it
        for child in oper.children:
            if child.name == "DOUBLE_NEG":
                remove_branch_node(oper, child, world.formula_tree)
        # in case there is a negation pileup
    inherit_state(oper)
    # check atom's truth valuation in the model
    atom = oper.children[0]
    result = world.access_atom(atom.name, False, atom.state)
    # if contradiction encountered, wipe the branch
    if result == False:
        return -99
    # otherwise, wipe resolved nodes and continue
    else:
        world.formula_tree.remove(atom)
        world.formula_tree.remove(oper)
        # print(formula_tree)

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
        insert_neg_node(oper, child, formula_tree)
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
    insert_neg_node(oper, right_child, formula_tree)
    inherit_state(oper)
    detach_parent(oper)
    formula_tree.remove(oper)

# PRIORITY TIER 3
def solve_initial_K(oper, agent, world):
    # retrieve this state's accessibility relations for this agent
    home_state = oper.state
    # can access at least itself
    relations = world.check_relations(home_state, agent)
    if not relations:
        sys.exit("K ERROR. Accessibility relations empty")
    print(f"retrieved relations of state {home_state}: {relations}")

# PRIORITY TIER 4
# resolve M (agent considers possible) operator
# or NOT-K (agent does not know) operator
def solve_M_or_neg_K(oper, world):
    home_state_id = oper.state
    agent = oper.children[0].name
    # create new state in model
    world.add_state()
    new_state_id = len(world.states) - 1
    # add new accessibility relation to the model
    world.add_relation(home_state_id, new_state_id, agent)
    current_set = world.check_relations(home_state_id, agent)
    print(f"agent {agent} relation sets: {current_set}")
    # if resolving NEG-K, insert negation
    if oper.name == "NEG_K":
        right_child = oper.children[1]
        insert_neg_node(oper, right_child, world.formula_tree)
    # change child's state, remove M operator and agent
    remove_epist_op(oper, new_state_id, world.formula_tree)



# sort roots by priority
def priority_sort(el):
    return el.priority

# general action choice loop
def solver_loop(world):
    resolvables = find_roots(world.formula_tree)
    resolvables.sort(key=lambda x: x.priority)
    print("\ncurrent available roots in priority order:")
    for n in resolvables:
        render_branch(n)
    oper_name = resolvables[0].name
    result = 0
    print("resolving ", oper_name)
    # if highest priority root is a lone atomic predicate
    if resolvables[0].type == "atom":
        result = solve_atom(resolvables[0], world)
    # otherwise, it must be an operator
    elif oper_name == "DOUBLE_NEG":
        solve_double_neg(resolvables[0], world.formula_tree)
    elif oper_name == "NEG":
        result = solve_neg(resolvables[0], world)
    elif oper_name == "AND":
        solve_and(resolvables[0], world.formula_tree)
    elif oper_name == "NEG_OR":
        solve_neg_or(resolvables[0], world.formula_tree)
    elif oper_name == "NEG_IMP":
        solve_neg_imp(resolvables[0], world.formula_tree)
    # TODO: insert tier 3 operators later
    elif oper_name == "M" or oper_name == "NEG_K":
        solve_M_or_neg_K(resolvables[0], world)
    else:
        sys.exit("UNIMPLEMENTED OPERATOR")
    # sidebar used here
    
    # TODO: add reverting to other branch functionality
    if result == -99:
        print("CONTRADICTION FOUND")
        world.formula_tree.clear()
        del world
        return
    print("current model state:")
    world.print_states()


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

# list formula_tree stores the formula in tree-node form
# sidebar is where we put formulas that might be expanded again later
# if a new accessibility relation is discovered
world = Model(3, 2)                     # TODO: automate

# generate formula of given length and max operator priority
generate_formula(world.formula_tree, 5, 4)
# find root nodes (should only be one!)
roots = find_roots(world.formula_tree)
if len(roots) > 1:
    sys.exit("ERROR more than one top connective")
# TODO: don't forget to negate the top connective!
# set state 0 for the top connective
for root in roots:
    root.state = 0

while world.formula_tree:
    solver_loop(world)
print("\nBRANCH COMPLETE \nend tableau solver output")
