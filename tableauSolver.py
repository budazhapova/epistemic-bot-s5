from model import Model
from formulaBuilder import *
from anytree import Node, RenderTree
from copy import deepcopy
import sys


# checks if there are any previous box-like operators for the old state
# and if so, triggers resolution of them for the new state
def trigger_sidebar(agent, old_state, new_state, world):
    rel_set = world.check_relations(old_state, agent)
    if not rel_set:
        sys.exit("TRIGGER ERROR. no relations found")
    # first, find available roots in the sidebar
    epist_nodes = find_roots(world.sidebar)
    for n in epist_nodes:
        # if there's a box-like operator with the same agent in the same set of states,
        #   solve it again for new state
        if n.state in rel_set and n.children[0].name == agent:
            repeat_solve_K_or_neg_M(n, new_state, world)
# FIXME: check if set of relations works!!

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
def solve_double_neg(oper, world):
    # if formula branches after double negation node, abort
    if len(oper.children) > 1:
        print("more than one child of DOUBLE_NEG node!")
        render_branch(oper)
        sys.exit("DOUBLE NEG ERROR")
    world.inherit_state(oper)
    world.detach_parent(oper)
    world.formula_tree.remove(oper)

# solve negation (only in front of atoms)
def solve_neg(oper, world):
    # if more than 1 step away from terminal node, there are multiple negations
    if oper.height > 1:
        # if next node is double negation, remove it
        for child in oper.children:
            if child.name == "DOUBLE_NEG":
                world.remove_branch_node(oper, child, world.formula_tree)
        # in case there is a negation pileup
    world.inherit_state(oper)
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
def solve_and(oper, world):
    # if AND operator is misapplied
    if len(oper.children) != 2:
        print("binary operator with wrong number of children!")
        render_branch(oper)
        sys.exit("AND ERROR")
    world.inherit_state(oper)
    world.detach_parent(oper)
    world.formula_tree.remove(oper)

# resolve NOT-OR operator
def solve_neg_or(oper, world):
    if len(oper.children) != 2:
        print("binary operator with wrong number of children!")
        render_branch(oper)
        sys.exit("NEG-OR ERROR")
    # apply negation to both child-nodes
    for child in oper.children:
        insert_neg_node(oper, child, world.formula_tree)
    world.inherit_state(oper)
    world.detach_parent(oper)
    world.formula_tree.remove(oper)

# resolve NOT-IMPLIES operator
def solve_neg_imp(oper, world):
    if len(oper.children) != 2:
        print("binary operator with wrong number of children!")
        render_branch(oper)
        sys.exit("NEG-IMP ERROR")
    # 'a does not imply b' means 'a and not-b'
    right_child = oper.children[1]
    insert_neg_node(oper, right_child, world.formula_tree)
    world.inherit_state(oper)
    world.detach_parent(oper)
    world.formula_tree.remove(oper)

# PRIORITY TIER 3
# deals with box-like operators (K or not-M)
def resolve_epist_box(oper, new_state_id, world, negation=False, first_call=True):
    # 'first_call' means this is the first time we're resolving this operator
    # and the original is located in the main formula_tree, not the sidebar
    if first_call:
        source = world.formula_tree
    else:
        source = world.sidebar
    # if not-M is being resolved, push negation on top of formula
    if negation:
        child_node = oper.children[1]
        insert_neg_node(oper, child_node, source)
    # assign state to the formula under epistemic operator
    world.confer_state(oper, new_state_id)
    # if first time resolving, remove epist oper (otherwise keep in the sidebar)
    if first_call:
        world.remove_epist_op(oper, source)

# K stands for (agent knows subformula),
# not-M stands for (agent doesn't consider subformula possible)
def solve_initial_K_neg_M(oper, world):
    if oper.name == "NEG_M":
        negation = True
    else:
        negation = False
    home_state = oper.state
    agent = oper.children[0].name
    # retrieve this state's accessibility relations for this agent
    # can access at least itself
    relations = world.check_relations(home_state, agent)
    # if no relations found, register reflexive accessibility
    if not relations:
        world.add_relation(home_state, home_state, agent)
        relations = {home_state}
    print(f"retrieved relations of state {home_state}: {relations}")
    # first, put a copy of current subtree into sidebar
    world.copy_subformula(oper, world.sidebar)
    # then, resolve the original
    # if only reflexive relation exists, no extra steps needed
    if len(relations) == 1:
        resolve_epist_box(oper, home_state, world, negation)
        return
    # otherwise there's more than 1 accessible state
    for state_id in relations:
        # do reflexive access last
        if state_id == home_state:
            pass
        top_index = world.copy_subformula(oper, world.formula_tree)
        top_node = world.formula_tree[top_index]
        resolve_epist_box(top_node, state_id, world, negation)
    # finally, state accesses itself
    resolve_epist_box(oper, home_state, world, negation)

# TODO: can these two be folded into one??
# works with previously resolved box-like epist operators from the sidebar
def repeat_solve_K_or_neg_M(oper, new_state_id, world):
    negation = False
    if oper.name == "NEG_M":
        negation = True
    agent = oper.children[0].name
    print(f"sidebar new relation: state {oper.state} to {new_state_id} for agent {agent}")
    # copy subformula from sidebar to formula tree
    top_index = world.copy_subformula(oper, world.formula_tree)
    top_node = world.formula_tree[top_index]
    resolve_epist_box(top_node, new_state_id, world, negation, first_call=False)

# PRIORITY TIER 4 -- diamondlike operators
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
    # change child's state, remove epist operator and agent
    world.confer_state(oper, new_state_id)
    world.remove_epist_op(oper, world.formula_tree)
    # trigger new state exploration for previously explored box operators
    trigger_sidebar(agent, home_state_id, new_state_id, world)

# PRIORITY TIER 5 -- branching binary operators (OR, not-AND, IMP, BI-IMP and not-BI-IMP)
def solve_branching(oper, world):
    # top operator determines how we structure the following
    rule = oper.name
    # pass down the state id to children
    world.inherit_state(oper)
    # copy child branches, then remove them from main
    left_branch = []
    right_branch = []
    # world.copy_subformula(oper.children[0], left_branch)
    # world.copy_subformula(oper.children[1], right_branch)
    # TODO: which branch copying method to use??
    left_branch = world.replicate_branch(oper.children[0])
    right_branch = world.replicate_branch(oper.children[1])
    world.wipe_branch(world.formula_tree, oper)
    # create copy the current model
    world_prime = world.copy_model()
        # outcome depends on rule used:
    # not-AND => not-A, not-B
    if rule == "NEG_AND":
        make_neg(left_branch, left_branch[0])
        make_neg(right_branch, right_branch[0])
    # OR => no negation necessary
    elif rule == "OR":
        pass
    # IMP => not-A, right
    elif rule == "IMP":
        make_neg(left_branch, left_branch[0])
    # BI_IMP => A + B, not-A + not-B
    # FIXME: check if replicate_branch works properly??
    elif rule == "BI_IMP":
        temp_copy = world.replicate_branch(left_branch)
        # temp_copy = deepcopy(left_branch)
        left_branch.extend(deepcopy(right_branch))
        # right branch contains negations of A as well as B
        make_neg(right_branch, right_branch[0])
        make_neg(temp_copy, temp_copy[0])
        right_branch.extend(temp_copy)
    # NEG_BI_IMP => A + not-B, not-A + B
    elif rule == "NEG_BI_IMP":
        temp_right = world.replicate_branch(right_branch)
        temp_left = world.replicate_branch(left_branch)
        # temp_right = deepcopy(right_branch)
        # temp_left = deepcopy(left_branch)
        make_neg(temp_left, temp_left[0])
        make_neg(temp_right, temp_right[0])
        left_branch.extend(temp_right)
        right_branch.extend(temp_left)
    # reinsert left branch into world-copy, right branch into original model object
    world_prime.formula_tree.extend(left_branch)
    print("model copy contains after attaching:")
    roots_prime = find_roots(world_prime.formula_tree)
    for r in roots_prime:
        render_branch(r)
    world.formula_tree.extend(right_branch)
    # try to solve left branch in world_prime first
    while world_prime.formula_tree:
        solver_loop(world_prime)
    # FIXME: check whether wrapper list for models is necessary?


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
    if world.sidebar:
        sidebar_roots = find_roots(world.sidebar)
        print("sidebar:")
        for s in sidebar_roots:
            render_branch(s)
    oper_name = resolvables[0].name
    result = 0
    print("resolving ", oper_name)
    # if highest priority root is a lone atomic predicate
    if resolvables[0].type == "atom":
        result = solve_atom(resolvables[0], world)
    # otherwise, it must be an operator
    elif oper_name == "NEG":
        result = solve_neg(resolvables[0], world)
    elif oper_name == "DOUBLE_NEG":
        solve_double_neg(resolvables[0], world)
    elif oper_name == "AND":
        solve_and(resolvables[0], world)
    elif oper_name == "NEG_OR":
        solve_neg_or(resolvables[0], world)
    elif oper_name == "NEG_IMP":
        solve_neg_imp(resolvables[0], world)
    elif oper_name == "K" or oper_name == "NEG_M":
        solve_initial_K_neg_M(resolvables[0], world)
    elif oper_name == "M" or oper_name == "NEG_K":
        solve_M_or_neg_K(resolvables[0], world)
    elif resolvables[0].priority == 5:
        solve_branching(resolvables[0], world)
    else:
        sys.exit("UNIMPLEMENTED OPERATOR")
    
    # TODO: add reverting to other branch functionality
    if result == -99:
        print("CONTRADICTION FOUND")
        world.formula_tree.clear()
        del world
        return
    print("current model state:")
    world.print_states()
    
    # if branch is open and complete (no operators left, no contradiction)
    if not world.formula_tree:
        print("OPEN AND COMPLETE BRANCH => NOT A TAUTOLOGY")
        sys.exit()


# TODO: operation for erasing branch with return -99
# TODO: duplicate for branching formulas


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
main_world = Model(3, 2)                     # TODO: automate
# FIXME: is this necessary if the branching happens in a method??
# this list holds all the models generated in the course of tableau solving
# all_worlds = []
# all_worlds.append(main_world)

# generate formula of given length and max operator priority
generate_formula(main_world.formula_tree, 7, 4)
# find root nodes (should only be one!)
roots = find_roots(main_world.formula_tree)
if len(roots) > 1:
    sys.exit("ERROR more than one top connective")
# negate first connective for the tableau
make_neg(main_world.formula_tree, roots[0])
# set state 0 for the top connective
# for root in roots:
#     root.state = 0
main_world.formula_tree[-1].state = 0

# TODO: consider an outer loop that accounts for branching?
while main_world.formula_tree:
    solver_loop(main_world)
print("\nBRANCH COMPLETE \nend tableau solver output")
