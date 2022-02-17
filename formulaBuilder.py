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
num_atoms = ["a", "b", "c"]
num_agents = 2



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
        # reassign priority
        formula.priority = connectives[formula.name]
        formula_tree.append(Node("DOUBLE_NEG", children=[formula], type="operator", state=None, priority=1))
        return formula_tree[-1]
    # if we get triple negation for some reason, rearrange to have double first
    # if formula.name == "DOUBLE_NEG":
    #     formula.name = formula.name.replace("DOUBLE_", "")
    #     formula_tree.append(Node("DOUBLE_NEG", children=[formula]))
    #     return
    # otherwise, assume we're negating an atom
    formula_tree.append(Node(oper, children=[formula], type="operator", state=None, priority=1))
    return formula_tree[-1]

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
def build_rnd_subformula(formula_tree, chosen):
    print("oper/conn choice: ", chosen)
    # if formula is empty or 50/50 chance to create new sub-branch
    # AND there's not too few operations left
    # TODO: do I even need random atom generation?
    # if (not formula_tree or (randint(0,9) < 3)):
    #     write_atom(formula_tree, choice(num_atoms))          # TODO: replace with reference to model later
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


# TODO: implicit/distributed knowledge operator I?

# generates a formula of 'countdown' amount of operators.
# arg 'permitted' denotes the maximum priority of allowed operators
# FIXME: remove the limit on op choice after testing!
def generate_formula(formula_tree, countdown, permitted=5):
    # list formula_tree will store the nodes containing elements (atoms, agents, operators, connectives)
    # of the formula in tree form
    # start by generating random atoms
    initial_atoms = countdown / 2
    while initial_atoms > 0:
        write_atom(formula_tree, choice(num_atoms))
        initial_atoms -= 1
    # count down the max number of operators
    while countdown > 0:
        print(countdown, " operations left")
        current_roots = find_roots(formula_tree)
        print(len(current_roots), " branches in existence")
        # if there are more unconnected formula sub-branches
        # than there are op/conns to generate,
        # restrict random choice to only binary conns
        if len(current_roots) >= countdown:
            # WORKAROUND for in-progress testing for tableau solver.
            # when limiting generated difficulty, use only tier-2 ops if tier-5 is not allowed yet
            if permitted < 5:
                selected = rnd_op_choice(2)
            else:
                selected = rnd_op_choice()      # default argument: 2 or 5
        # otherwise, choose from all available
        else:
            selected = rnd_op_choice(randint(1,permitted))
        # ensure we don't end up with one extra operator in the last round.
        # if selected is 'double neg' or 'not-smth', try again
        while countdown == 1 and "_" in selected:
            if selected == "BI_IMP": break
            # if branches need uniting
            if len(current_roots) > 1:
                # TODO: remove after testing
                if permitted < 5:
                    selected = "AND"
                else:
                    selected = choice(["AND", "OR", "IMP", "BI_IMP"])
            # if no unifying necessary
            else:
                selected = rnd_op_choice(randint(1,permitted))
        build_rnd_subformula(formula_tree, selected)
        # if chosen operator actually contains 2 op/conns, count them properly
        if "_" in selected and selected != "BI_IMP":
            countdown -= 2
        else:
            countdown -= 1
    all_branches = find_roots(formula_tree)
    if len(all_branches) > 1:
        print("SPLIT TREE!")
    # print formula tree for checking
    for elem in all_branches:
        render_branch(elem)
    print("end formula-builder output\n")
    # return formula_tree

# generate_formula(6)