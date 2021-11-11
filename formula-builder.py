import model
from anytree import Node, RenderTree, ContStyle

#TODO: randomise formula tree building

#TODO: load requirements from file?

# TODO: define operators/connectives as enums??

num_atoms = 1
num_agents = 1

# possible types of operators/connectives:
# | for `or`, & for 'and', ~ for `not`
# K, M, ^ for `implies`

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
    formula.parent = formula_tree[-1]
    print(formula_tree)

# make operator K or M, given existing formula and agent
def make_epist(oper, formula, agent):
    formula_tree.append(Node(oper, children=[agent, formula]))
    agent.parent = formula_tree[-1]
    formula.parent = formula_tree[-1]
    print(formula_tree)

# TODO: functions for and/or/imp, as well as not-everything
# TODO: check whether children are always accessed in order of creation for implication


write_atom("p")
make_neg(formula_tree[-1])
write_agent("1")
make_epist("K", formula_tree[-2], formula_tree[-1])
for elem in formula_tree:
    if elem.is_root:
        print(RenderTree(elem, style=ContStyle()))
print("end formula-builder output")