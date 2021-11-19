from model import Model
from anytree import Node, RenderTree, ContStyle
from random import randint, choice

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
    "NEG_BI_IMG": 5
}

# globals for now, will change once automatic generation is implemented
num_atoms = 2
num_agents = 2
max_length = 3

# list formula_tree will store the nodes containing elements (atoms, agents, operators, connectives)
# of the formula in tree form
formula_tree = []


# makes a node with a propositional atom
def write_atom(atom):
    formula_tree.append(Node(atom))
    print(formula_tree)

# makes a node with an agent
# TODO: connect atom and agent with model? do we actually need it for the generator?
def write_agent(agent):
    formula_tree.append(Node(agent))
    print(formula_tree)

# make negation operator, given a formula
def make_neg(formula):
    formula_tree.append(Node("NEG", children=[formula]))
    # print(formula_tree)

# make operator K or M, given existing formula and agent
def make_epist(oper, agent, formula):
    formula_tree.append(Node(oper, children=[agent, formula]))
    # print(formula_tree)

# make negation of epistemic operator
def make_neg_epist(oper, agent, formula):
    formula_tree.append(Node("NEG_" + oper, children=[agent, formula]))

# make binary connective (and, or, implies)
def make_bin_con(connective, left, right):
    formula_tree.append(Node(connective, children=[left, right]))
    # print(formula_tree)

# TODO: are separate functions for negation necessary?
# make negation of binary (not-stuff)
def make_neg_bin(connective, left, right):
    formula_tree.append(Node("NEG_" + connective, children=[left, right]))
    # print(formula_tree)

# choose random operator/connective to build a new tree node with
# first, we get all op/cons with a randomly chosen priority
# then, we take a random op/con from that list
def random_op_choice():
    op_choice = []
    pr_tier = randint(1,5)
    for op, priority in connectives.items():
        if priority == pr_tier:
            op_choice.append(op)
    return choice(op_choice)

# construct a new formula node with randomly chosen op/con
def build_rnd_subformula():
    chosen = random_op_choice
    if not formula_tree or (randint(0,9) < 3):
        write_atom(choice(["a", "b"]))          # TODO: replace with reference to model later
    # if the chosen op/conn is (double) negation
    if connectives[chosen] == 1:
        # modify and call write_neg
    elif connectives[chosen] == 3 or connectives[chosen] == 4:
        # modify and call make_epist
    else:
        # otherwise, it's a binary connective


# renders a simplified formula tree (without path in nodes)
def render_branch(element):
    for pre, _, node in RenderTree(element):
        print("%s%s" % (pre, node.name))


# TODO: check whether children are always accessed in order of creation for implication
# TODO: make sure multiple not-connectives are counted properly


write_atom("p")
make_neg(formula_tree[-1])
write_agent("1")
make_epist("K", formula_tree[-1], formula_tree[-2])
write_atom("a")
write_atom("b")
make_bin_con("AND", formula_tree[-2], formula_tree[-1])
write_agent("2")
make_neg_epist("M", formula_tree[-1], formula_tree[-2])
make_neg_bin("OR", formula_tree[3], formula_tree[-1])
for elem in formula_tree:
    # if elem.name in connectives:
    #     print(f"Node name '{elem.name}', priority {connectives[elem.name]}")
    if elem.is_root:
        render_branch(elem)
print("end formula-builder output")