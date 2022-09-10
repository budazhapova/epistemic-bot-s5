from model import Model
from anytree import Node, RenderTree, ContStyle
from random import randint, choice, sample
from stringConverter import translate_formula

# SUMMARY: generate_formula takes world (a Model-class object) and desired formula length as arguments
#   and constructs an epistemic logic formula

# all possible operators and connective in descending priority order of resolving
connectives = {
    "DOUBLE_NEG": 1,
    "NEG": 1,
    "AND": 2,
    "NEG_OR": 2,
    "NEG_IMP": 2,
    "K": 3,
    "NEG_M": 3,
    "NEG_K": 4,
    "M": 4,
    "OR": 5,
    "NEG_AND": 5,
    "IMP": 5,
    "BI_IMP": 5,
    "NEG_BI_IMP": 5
}



# makes a node with a propositional atom
def write_atom(world, atom):
    world.formula_tree.append(Node(atom, type="atom", state=None, priority=0, id=world.node_total+1))
    world.node_total += 1
    return world.formula_tree[-1]

# makes a node with an agent
def write_agent(world, agent):
    world.formula_tree.append(Node(agent, type="agent", state=None, priority=0, id=world.node_total+1))
    world.node_total += 1
    return world.formula_tree[-1]

# make negation operator, given a formula
def make_neg(formula_tree, formula, new_id):
    state_id = formula.state
    # if formula starts with negation, make it double
    if formula.name == "NEG":
        formula.name = "DOUBLE_NEG"
        return 0
    # if formula starts with any other operator:
    if formula.name in ["K", "M", "AND", "OR", "IMP", "BI_IMP"]:
        formula.name = "NEG_" + formula.name
        # reassign priority tier
        formula.priority = connectives[formula.name]
        return 0
    # if formula already contains negation, remove and put double negation in new node
    if "NEG_" in formula.name:
        formula.name = formula.name.replace("NEG_", "")
        # reassign priority and state (if node has state identifier)
        formula.priority = connectives[formula.name]
        formula_tree.append(Node("DOUBLE_NEG", children=[formula], type="operator", state=state_id, priority=1, id=new_id))
        return formula_tree[-1]
    # otherwise, assume we're negating an atom
    formula_tree.append(Node("NEG", children=[formula], type="operator", state=state_id, priority=1, id=new_id))
    return formula_tree[-1]

# insert new negation node between parent and child
def insert_neg_node(parent_node, child_node, formula_tree, new_id):
    neg_node = make_neg(formula_tree, child_node, new_id)
    if neg_node != 0:
        neg_node.parent = parent_node
        child_node.parent = neg_node

# make operator K or M (or their negations), given existing formula and agent
def make_epist(formula_tree, oper, agent, formula, new_id):
    formula_tree.append(Node(oper, children=[agent, formula], type="operator", state=None, priority=connectives[oper], id=new_id))

# make binary connective (and, or, implies, and negations of them)
def make_bin_con(formula_tree, connective, left, right, new_id):
    formula_tree.append(Node(connective, children=[left, right], type="operator", state=None, priority=connectives[connective], id=new_id))



# choose a random operator/connective from a given priority tier.
# binary connectives only is the default mode (i.e., if called with no argument).
# compiles a list of all op/cons with a given chosen priority
# and returns a random op/con from that list
def rnd_op_choice(pr_tier=choice([2,5])):
    print("priority tier: ", pr_tier)
    # I exclude double negation because there are many ways to arrive at it already
    if pr_tier == 1:
        selected = "NEG"
        return selected
    op_choice = []
    for op, priority in connectives.items():
        if priority == pr_tier:
            op_choice.append(op)
    selected = choice(op_choice)
    # print("oper/conn selected: ", selected)
    return selected

# construct a new formula node with randomly chosen op/con
def build_rnd_subformula(world, chosen):
    print("oper/conn choice: ", chosen)
    all_roots = world.find_roots(world.formula_tree)
    subformula = choice(all_roots)
    # if the chosen op/conn is negation
    if connectives[chosen] == 1:
        make_neg(world.formula_tree, subformula, world.node_total+1)
        world.node_total += 1
    # if epistemic operator is chosen
    elif connectives[chosen] == 3 or connectives[chosen] == 4:
        new_agent = write_agent(world, randint(1, world.num_agents))
        make_epist(world.formula_tree, chosen, new_agent, subformula, world.node_total+1)
        world.node_total += 1
    else:
        # otherwise, it's a binary connective.
        # choose two random branches to link
        two_branches = sample(all_roots, k=2)
        make_bin_con(world.formula_tree, chosen, two_branches[0], two_branches[1], world.node_total+1)
        world.node_total += 1

# renders a simplified formula tree (without path in nodes)
def render_branch(element):
    for pre, _, node in RenderTree(element):
        print("%s%s[%s]/%s (%s)" % (pre, node.name, node.id, node.state, node.priority))



# generates a formula of 'countdown' length.
# every atom and operator (except for agents) adds length of 1.
def generate_formula(world, countdown):
    # list formula_tree will store the nodes containing elements (atoms, agents, operators, connectives)
    # of the formula in tree form
    # start by generating random atoms
    if countdown < 5:
        initial_atoms = countdown / 2
    else:
        # variable number of atoms involved: between 1/4 and 2/3 of total formula length
        initial_atoms = randint(int(countdown/4), int(countdown*2/3))
    while initial_atoms > 0:
        write_atom(world, choice(world.atoms))
        initial_atoms -= 1
        countdown -= 1
    # count down the remaining formula length
    while countdown > 0:
        print(countdown, " operations left")
        current_roots = world.find_roots(world.formula_tree)
        print(len(current_roots), " branches in existence")
        # if there's only one root, choose only unary connectives
        if len(current_roots) == 1:
            # if single operator left, choose one
            if countdown == 1:
                selected = choice(["NEG", "K", "M"])
            # otherwise, can use negated operators as well
            else:
                selected = choice(["NEG", "K", "NEG_K", "M", "NEG_M"])
        # if there are more branches than remaining connectives,
        # restrict random choice to only (non-negated) binary connectives
        elif len(current_roots) > countdown:
            selected = choice(["AND", "OR", "IMP", "BI_IMP"])
        # otherwise, choose from all available
        else:
            # FIXME: removed the limited operator selection, test working
            # selected = rnd_op_choice(choice([1,2,5]))
            selected = rnd_op_choice(randint(1,5))
        build_rnd_subformula(world, selected)
        # if chosen operator contains negation, adjust count
        if "_" in selected and selected != "BI_IMP":
            countdown -= 2
        else:
            countdown -= 1
    all_branches = world.find_roots(world.formula_tree)
    if len(all_branches) > 1:
        print("SPLIT TREE!")
    # print formula tree for checking
    for elem in all_branches:
        render_branch(elem)
    print("end formula-builder output\n")

    line_format = translate_formula(all_branches[0])
    print(line_format)