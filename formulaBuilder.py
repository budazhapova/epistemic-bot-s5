from model import Model
from anytree import Node, RenderTree, ContStyle
from random import randint, choice, sample

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
max_length = 5      # maximum number of operators in a formula for now



# TODO: should atoms/agents have priority tier? check with resolving negations in tableau
# makes a node with a propositional atom
def write_atom(formula_tree, atom):
    formula_tree.append(Node(atom, type="atom", state=None, priority=0))
    return formula_tree[-1]

# makes a node with an agent
# TODO: connect atom and agent with model? do we actually need it for the generator?
def write_agent(formula_tree, agent):
    formula_tree.append(Node(agent, type="agent", state=None, priority=0))
    return formula_tree[-1]

# make negation operator, given a formula
def make_neg(formula_tree, oper, formula):
    # if formula starts with negation, make it double
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
        formula_tree.append(Node("DOUBLE_NEG", children=[formula], type="operator", state=None, priority=1))
        return
    # if we get triple negation for some reason, rearrange to have double first
    # if formula.name == "DOUBLE_NEG":
    #     formula.name = formula.name.replace("DOUBLE_", "")
    #     formula_tree.append(Node("DOUBLE_NEG", children=[formula]))
    #     return
    # otherwise, assume we're negating an atom
    formula_tree.append(Node(oper, children=[formula], type="operator", state=None, priority=1))

# make operator K or M (or their negations), given existing formula and agent
def make_epist(formula_tree, oper, agent, formula):
    formula_tree.append(Node(oper, children=[agent, formula], type="operator", state=None, priority=connectives[oper]))

# make binary connective (and, or, implies, and negations of them)
def make_bin_con(formula_tree, connective, left, right):
    formula_tree.append(Node(connective, children=[left, right], type="operator", state=None, priority=connectives[connective]))


# find all top (root) nodes and return a list of them
def find_roots(formula_tree):
    all_roots = []
    for elem in formula_tree:
        if elem.is_root:
            all_roots.append(elem)
    return all_roots


# choose a random operator/connective from a given priority tier
# binary connectives only is the default value (i.e., if called with no argument).
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
    print("oper/conn selected: ", selected)
    return selected

# construct a new formula node with randomly chosen op/con
def build_rnd_subformula(formula_tree, chosen, countdown):
    print("oper/conn choice: ", chosen)
    # if formula is empty or 50/50 chance to create new sub-branch
    # AND there's not too few operations left
    # TODO: is this probability alright?
    if (not formula_tree or (randint(0,9) < 5)) and countdown >= (max_length/3):
        write_atom(formula_tree, choice(num_atoms))          # TODO: replace with reference to model later
    all_roots = find_roots(formula_tree)
    subformula = choice(all_roots)
    # if the chosen op/conn is negation
    if connectives[chosen] == 1:
        make_neg(formula_tree, chosen, subformula)
    # if epistemic operator is chosen
    elif connectives[chosen] == 3 or connectives[chosen] == 4:
        new_agent = write_agent(formula_tree, randint(1, num_agents))     # TODO: replace with reference to model later?
        make_epist(formula_tree, chosen, new_agent, subformula)
    else:
        # otherwise, it's a binary connective
        # write another atom if there's only one root available
        if len(all_roots) < 2:
            new_atom = write_atom(formula_tree, choice(num_atoms))       # TODO: don't forget to replace atoms
            all_roots.append(new_atom)
        two_branches = sample(all_roots, k=2)
        make_bin_con(formula_tree, chosen, two_branches[0], two_branches[1])

# renders a simplified formula tree (without path in nodes)
def render_branch(element):
    for pre, _, node in RenderTree(element):
        print("%s%s/%s" % (pre, node.name, node.state))


# TODO: check whether children are always accessed in order of creation for implication
# TODO: make sure multiple not-connectives are counted properly
# TODO: change update counter so that it checks "not-something" oper/conns as 2 operations?

# generates a formula of (approx.) 'countdown' number of operators
def generate_formula(countdown):
    # list formula_tree will store the nodes containing elements (atoms, agents, operators, connectives)
    # of the formula in tree form
    formula_tree = []
    # count down the max number of operators (is funky about negation!)
    while countdown > 0:
        print(countdown, " operations left")
        current_roots = find_roots(formula_tree)
        print(len(current_roots), " branches in existence")
        # if there are more unconnected formula sub-branches
        # than there are op/conns to generate,
        # restrict random choice to only binary conns
        if len(current_roots) >= countdown:
            selected = rnd_op_choice()
        # otherwise, choose from all available
        else:
            selected = rnd_op_choice(randint(1,5))
        build_rnd_subformula(formula_tree, selected, countdown)
        countdown -= 1
    all_branches = find_roots(formula_tree)
    # print formula tree for checking
    for elem in all_branches:
        render_branch(elem)
    print("end formula-builder output\n")
    return formula_tree


# generate_formula(max_length)