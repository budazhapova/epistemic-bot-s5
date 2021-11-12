import model
from anytree import Node, RenderTree, ContStyle

#TODO: randomise formula tree building

#TODO: load requirements from file?

# TODO: define operators/connectives as enums??

num_atoms = 1
num_agents = 1

# possible types of operators/connectives:
# `or`,'and', `neg` for "not"
# 'K', 'M', 'imp' for "implies"
# 'neg (whatever)' for "not-operator/connective"
# TODO: write enums for ^!

# list formula_tree will store the nodes containing elements (atoms, agents, operators, connectives)
# of the formula in tree form
formula_tree = []

# TODO: judge if I actually need it
# makes a node with a propositional atom
def write_atom(atom):
    formula_tree.append(Node(atom))
    print(formula_tree)

# makes a node with an agent
# TODO: connect atom and agent with model?
def write_agent(agent):
    formula_tree.append(Node(agent))
    print(formula_tree)

# make negation operator, given a formula
def make_neg(formula):
    formula_tree.append(Node("neg", children=[formula]))
    # print(formula_tree)

# make operator K or M, given existing formula and agent
def make_epist(oper, agent, formula):
    formula_tree.append(Node(oper, children=[agent, formula]))
    # print(formula_tree)

# make negation of epistemic operator
def make_neg_epist(oper, agent, formula):
    formula_tree.append(Node("neg " + oper, children=[agent, formula]))

# make binary connective (and, or, implies)
def make_bin(connective, left, right):
    formula_tree.append(Node(connective, children=[left, right]))
    # print(formula_tree)

# make negation of binary (not-stuff)
def make_neg_bin(connective, left, right):
    formula_tree.append(Node("neg " + connective, children=[left, right]))
    # print(formula_tree)

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
make_neg_bin("and", formula_tree[-2], formula_tree[-1])
write_agent("2")
make_neg_epist("M", formula_tree[-1], formula_tree[-2])
for elem in formula_tree:
    if elem.is_root:
        render_branch(elem)
print("end formula-builder output")