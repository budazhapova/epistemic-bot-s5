from model import Model
from formulaBuilder import *
from stringConverter import *
from presets import load_preset
from anytree import Node, RenderTree
from copy import deepcopy
import sys

# SUMMARY: this file contains code of the tableau solver module. tableau_solver function takes a Model-class object (world)
#   and solves the negation of the formula contained there. returns a boolean for whether the formula is a tautology or not

# checks if there are any previous box-like operators for the old state
# and if so, triggers resolution of them for the new state
def trigger_sidebar(agent, old_state, new_state, world):
    rel_set = world.check_relations(old_state, agent)
    if not rel_set:
        sys.exit("TRIGGER ERROR. no relations found")
    # first, find available roots in the sidebar
    epist_nodes = world.find_roots(world.sidebar)
    for n in epist_nodes:
        # if there's a box-like operator with the same agent in the same pool of states,
        #   solve it again for new state
        if n.state in rel_set and n.children[0].name == agent:
            repeat_solve_K_or_neg_M(n, new_state, world)


# PRIORITY TIER 0
# resolve an atom at the end of a branch
def solve_atom(atom, world):
    # if atom.height != 0:
    #     print("single atom at non-terminal node!\n function solve_atom")
    #     sys.exit("ATOM ERROR")
    result = world.access_atom(atom.name, True, atom.state)
    if result == False:
        return -99
    else:
        world.formula_tree.remove(atom)
        # print(formula_tree)

# PRIORITY TIER 1
# called when a NEG node encountered not in front of an atom
# checks which node is next and rewrites them accordingly
def solve_multi_neg(node, world):
    # if current node has more than 1 child, stop
    if len(node.children) > 1:
        sys.exit("NEGATION FAIL! neg node has more than 2 children")
    # recursively count how many negations in a row there are
    for child in node.children:
        if child.name == "DOUBLE_NEG":
            world.inherit_state(node)
            # wipe first NEG, solve DOUBLE_NEG, reattach NEG to DOUBLE_NEG's child
            grandchildren = child.children
            world.detach_parent(node)
            world.formula_tree.remove(node)
            solve_double_neg(child, world)
            # attach NEG node to DOUBLE NEG's child and assign appropriate state id
            # (should only ever be one grandchild, but node.children is always a list)
            for grandchild in grandchildren:
                world.node_total += 1
                make_neg(world.formula_tree, grandchild, world.node_total)


# resolve double negation
def solve_double_neg(oper, world):
    world.inherit_state(oper)
    world.detach_parent(oper)
    world.formula_tree.remove(oper)

# solve negation (only in front of atoms)
def solve_neg(oper, world):
    # if more than 1 step away from terminal node, there may be multiple negations involved
    if oper.height > 1:
        solve_multi_neg(oper, world)
        return
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
    world.inherit_state(oper)
    world.detach_parent(oper)
    world.formula_tree.remove(oper)

# resolve NOT-OR operator
def solve_neg_or(oper, world):
    world.inherit_state(oper)
    # apply negation to both child-nodes, with neg-node inserted between oper and children
    for child in oper.children:
        world.node_total += 1
        insert_neg_node(oper, child, world.formula_tree, world.node_total)
    world.detach_parent(oper)
    world.formula_tree.remove(oper)

# resolve NOT-IMPLIES operator
def solve_neg_imp(oper, world):
    # 'a does not imply b' means 'a and not-b'
    right_child = oper.children[1]
    world.node_total += 1
    insert_neg_node(oper, right_child, world.formula_tree, world.node_total)
    world.inherit_state(oper)
    world.detach_parent(oper)
    world.formula_tree.remove(oper)

# PRIORITY TIER 3
# deals with box-like operators (K or not-M)
def resolve_epist_box(oper, new_state_id, world, negation=False):
    # if not-M is being resolved, push negation on top of formula
    if negation:
        child_node = oper.children[1]
        world.node_total += 1
        insert_neg_node(oper, child_node, world.formula_tree, world.node_total)
    # assign state to the formula under epistemic operator
    world.confer_state(oper, new_state_id)
    # remove epist oper, keep the rest of the formula
    world.remove_epist_op(oper, world.formula_tree)

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
    # print(f"retrieved relations of state {home_state}: {relations}")
    # first, put a copy of current subtree into sidebar
    sidebar_copy = world.replicate_branch(oper)
    world.sidebar.extend(sidebar_copy)
    # then, resolve the original
    # otherwise there's more than 1 accessible state
    for state_id in relations:
        # do reflexive access last (states get retrieved in random order)
        if state_id == home_state:
            pass
        else:
            new_branch = world.replicate_branch(oper)
            world.formula_tree.extend(new_branch)
            local_root = new_branch[0]
            resolve_epist_box(local_root, state_id, world, negation)
    # in any case, resolve epistemic operator for the home state (accesses itself)
    resolve_epist_box(oper, home_state, world, negation)

# works with previously resolved box-like epist operators from the sidebar
def repeat_solve_K_or_neg_M(oper, new_state_id, world):
    negation = False
    if oper.name == "NEG_M":
        negation = True
    agent = oper.children[0].name
    # print(f"invoking {oper.name} from the sidebar")
    # print(f"sidebar new relation: state {oper.state} to {new_state_id} for agent {agent}")
    # copy subformula from sidebar to formula tree
    new_branch = world.replicate_branch(oper)
    world.formula_tree.extend(new_branch)
    local_root = new_branch[0]
    resolve_epist_box(local_root, new_state_id, world, negation)

# PRIORITY TIER 4 -- diamondlike operators
# resolve M (agent considers possible) operator
# or NOT-K (agent does not know) operator
def solve_M_or_neg_K(oper, world):
    home_state_id = oper.state
    agent = oper.children[0].name
    # first, check whether this diamond-like node has been resolved before on this branch.
    # if this is the fourth pass of this node, judge the branch infinite and quit solving
    repetitions = world.check_repetition(oper.id)
    # print(f"operator {oper.name} is being resolved {repetitions} times")
    if repetitions > 3:
        # print("INFINITE BRANCH DETECTED")
        return False
    # create new state in model
    world.add_state()
    new_state_id = len(world.states) - 1
    # add new accessibility relation to the model
    world.add_relation(home_state_id, new_state_id, agent)
    current_set = world.check_relations(home_state_id, agent)
    # print(f"agent {agent} relation sets: {current_set}")
    # if resolving NEG-K, insert negation
    if oper.name == "NEG_K":
        right_child = oper.children[1]
        world.node_total += 1
        insert_neg_node(oper, right_child, world.formula_tree, world.node_total)
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
    left_branch = world.replicate_branch(oper.children[0])
    right_branch = world.replicate_branch(oper.children[1])
    world.wipe_branch(world.formula_tree, oper)
    # create copy of the current model
    world_prime = world.copy_model()
        # outcome depends on rule used:
    # not-AND => not-A, not-B
    if rule == "NEG_AND":
        make_neg(left_branch, left_branch[0], world.node_total+1)
        make_neg(right_branch, right_branch[0], world.node_total+2)
        world.node_total += 2
    # OR => no negation necessary
    elif rule == "OR":
        pass
    # IMP => not-A, right
    elif rule == "IMP":
        make_neg(left_branch, left_branch[0], world.node_total+1)
        world.node_total += 1
    # BI_IMP => A + B, not-A + not-B
    elif rule == "BI_IMP":
        temp_copy = world.replicate_branch(left_branch[0])
        # temp_copy = deepcopy(left_branch)
        left_branch.extend(deepcopy(right_branch))
        # right branch contains negations of A as well as B
        make_neg(right_branch, right_branch[0], world.node_total+1)
        make_neg(temp_copy, temp_copy[0], world.node_total+2)
        world.node_total += 2
        right_branch.extend(temp_copy)
    # NEG_BI_IMP => A + not-B, not-A + B
    elif rule == "NEG_BI_IMP":
        temp_right = world.replicate_branch(right_branch[0])
        temp_left = world.replicate_branch(left_branch[0])
        make_neg(temp_left, temp_left[0], world.node_total+1)
        make_neg(temp_right, temp_right[0], world.node_total+2)
        world.node_total += 2
        left_branch.extend(temp_right)
        right_branch.extend(temp_left)
    # reinsert left branch into world-copy, right branch into original model object
    world_prime.formula_tree.extend(left_branch)
    world.formula_tree.extend(right_branch)
    # check for roots in old model
    top_nodes = world.find_roots(world.formula_tree)
    # try to solve left branch in world_prime first
    while world_prime.formula_tree:
        branch_status = solver_loop(world_prime)
        if branch_status == False:
            return False


# sort roots by priority
def priority_sort(el):
    return el.priority

# general action choice loop
def solver_loop(world):
    resolvables = world.find_roots(world.formula_tree)
    # print(f"\n new solver loop: {len(world.formula_tree)} nodes available, of them {len(resolvables)} roots")
    # print("nodes in the list:")
    # for node in world.formula_tree:
    #         print(f"{node.name}[{node.id}]")
    resolvables.sort(key=lambda x: x.priority)
    # print("\ncurrent available roots in priority order:")
    # for n in resolvables:
    #     render_branch(n)
    #     print(translate_formula(n)[0], end="\n\n")
    # if world.sidebar:
    #     sidebar_roots = world.find_roots(world.sidebar)
    #     print("sidebar:")
    #     for s in sidebar_roots:
    #         render_branch(s)
    #         print(translate_formula(s)[0], end="\n\n")
    oper_name = resolvables[0].name
    result = 0
    branch_status = None
    # print("resolving ", oper_name)
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
        branch_status = solve_M_or_neg_K(resolvables[0], world)
    elif resolvables[0].priority == 5:
        branch_status = solve_branching(resolvables[0], world)
    else:
        sys.exit("UNIMPLEMENTED OPERATOR")
    
    if result == -99:
        # print("CONTRADICTION FOUND")
        world.formula_tree.clear()
        world.sidebar.clear()
        del world
        return None
    # print("current model state:")
    # world.print_states()
    
    # if branch is open and complete (no operators left, no contradiction)
    if not world.formula_tree or branch_status == False:
        # print("OPEN AND COMPLETE BRANCH => NOT A TAUTOLOGY")
        return False



# list formula_tree stores the formula in tree-node form.
# sidebar is where we put formulas that might be expanded again later
#    if a new accessibility relation is discovered
def tableau_solver(main_world):
    # records whether the formula is a tautology
    t_status = None
    roots = main_world.find_roots(main_world.formula_tree)
    if len(roots) > 1:
        # print("ERROR more than one top connective")
        return -1
    # negate first connective for the tableau
    make_neg(main_world.formula_tree, roots[0], main_world.node_total+1)
    main_world.node_total += 1
    # set state 0 for the top connective
    roots = main_world.find_roots(main_world.formula_tree)
    for root in roots:
        root.state = 0

    # loop keeps running until either formula is proven false or it runs out of branches to try
    while t_status != False and main_world.formula_tree:
        t_status = solver_loop(main_world)
        if t_status == False:
            # print("END OF PROOF")
            return t_status
    # print("\nSOLVING COMPLETE \nend tableau solver output")
    # if formula has not been proven NOT a tautology, declare it a tautology
    if not t_status == False:
        t_status = True
        return t_status