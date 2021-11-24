from model import Model
from anytree import Node, RenderTree, ContStyle
from random import randint, choice, sample

#TODO: randomise formula tree building

#TODO: load requirements from file?

# all possible operators and connective in descending priority order of resolving
connectives = {
    "DOUBLE_NEG": 1,
    "NEG": 1,             # TODO: might be resolved another way?
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

# globals for now, will change once automatic generation is implemented
num_atoms = ["a", "b"]
num_agents = 2
max_length = 10      # maximum number of operators in a formula for now

# list formula_tree will store the nodes containing elements (atoms, agents, operators, connectives)
# of the formula in tree form
formula_tree = []


# makes a node with a propositional atom
def write_atom(atom):
    formula_tree.append(Node(atom))
    return formula_tree[-1]

# makes a node with an agent
# TODO: connect atom and agent with model? do we actually need it for the generator?
def write_agent(agent):
    formula_tree.append(Node(agent))
    return formula_tree[-1]

# make negation operator, given a formula
def make_neg(oper, formula):
    # if formula starts with negation, make it double
    if oper == "NEG":
        if formula.name == "NEG":
            formula.name = "DOUBLE_NEG"
            return
        # if formula starts with any other operator:
        if formula.name in ["K", "M", "AND", "OR", "IMP", "BI_IMP"]:
            formula.name = "NEG_" + formula.name
            return
        # if formula already contains negation, remove and put double negation in new node
        if "NEG_" in formula.name:
            formula.name = formula.name.replace("NEG_", "")
            formula_tree.append(Node("DOUBLE_NEG", children=[formula]))
            return
        # if we get triple negation for some reason, rearrange to have double first
        if formula.name == "DOUBLE_NEG":
            formula.name = formula.name.replace("DOUBLE_", "")
            formula_tree.append(Node("DOUBLE_NEG", children=[formula]))
            return
    # otherwise, assume we're negating an atom
    formula_tree.append(Node(oper, children=[formula]))

# make operator K or M, given existing formula and agent
def make_epist(oper, agent, formula):
    formula_tree.append(Node(oper, children=[agent, formula]))

# make binary connective (and, or, implies)
def make_bin_con(connective, left, right):
    formula_tree.append(Node(connective, children=[left, right]))


# find all top (root) nodes and choose a random one
def find_roots():
    all_roots = []
    for elem in formula_tree:
        if elem.is_root:
            all_roots.append(elem)
    return all_roots

# choose random operator/connective to build a new tree node with
# first, we get all op/cons with a randomly chosen priority
# then, we take a random op/con from that list
def rnd_op_choice():
    op_choice = []
    pr_tier = randint(1,5)
    print("priority tier: ", pr_tier)
    for op, priority in connectives.items():
        if priority == pr_tier:
            op_choice.append(op)
    return choice(op_choice)

# construct a new formula node with randomly chosen op/con
def build_rnd_subformula():
    chosen = rnd_op_choice()
    print("oper/con choise: ", chosen)
    if not formula_tree or (randint(0,9) < 2):
        write_atom(choice(num_atoms))          # TODO: replace with reference to model later
    all_roots = find_roots()
    subformula = choice(all_roots)
    # if the chosen op/conn is (double) negation
    if connectives[chosen] == 1:
        make_neg(chosen, subformula)
    # if epistemic operator is chosen
    elif connectives[chosen] == 3 or connectives[chosen] == 4:
        new_agent = write_agent(randint(1, num_agents))     # TODO: replace with reference to model later?
        make_epist(chosen, new_agent, subformula)
    else:
        # otherwise, it's a binary connective
        # write another atom if there's only one root available
        if len(all_roots) < 2:
            new_atom = write_atom(choice(num_atoms))       # TODO: don't forget to replace atoms
            all_roots.append(new_atom)
        two_branches = sample(all_roots, k=2)
        make_bin_con(chosen, two_branches[0], two_branches[1])

# renders a simplified formula tree (without path in nodes)
def render_branch(element):
    for pre, _, node in RenderTree(element):
        print("%s%s" % (pre, node.name))


# TODO: check whether children are always accessed in order of creation for implication
# TODO: make sure multiple not-connectives are counted properly
# TODO: ensure it eventually comes to a single root node in the end!
# TODO: change update counter so that it checks "not-something" oper/conns as 2 operations?



for x in range(max_length):
    print("turn ", x)
    build_rnd_subformula()
all_branches = find_roots()
for elem in all_branches:
    render_branch(elem)
print("end formula-builder output")