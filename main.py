from model import Model
from formulaBuilder import *
from tableauSolver import *
from presets import *
from random import randint

# setup for generating a formula: amount of connectives/operators, atoms, and agents
# shorter formulas have fewer variables
# returns a Model-class object with already generated formula
def make_model(formula_length):
    agents_total = 1
    if formula_length < 7:
        atoms_total = 1
    elif formula_length < 20:
        atoms_total = 2
    else:
        atoms_total = 3
        if formula_length > 60:
            agents_total = 3
        else:
            agents_total = 2
    # generate formula of given length and max operator priority
    if WORKMODE == "generate":
        main_world = Model(atoms_total, agents_total)
        generate_formula(main_world, formula_length)
    # or load a preset formula from presets
    elif WORKMODE == "load":
        main_world = Model(2, 2)
        main_world.formula_tree = load_preset(5)
        main_world.node_total = len(main_world.formula_tree)
    
    # TODO: space for checking for duplicates
    return main_world

WORKMODE = "generate"
# WORKMODE = "load"




# find root nodes (should only be one!)
roots = find_roots(main_world.formula_tree)
if len(roots) > 1:
    sys.exit("ERROR more than one top connective")
# negate first connective for the tableau
make_neg(main_world.formula_tree, roots[0], main_world.node_total+1)
main_world.node_total += 1
# set state 0 for the top connective
roots = find_roots(main_world.formula_tree)
for root in roots:
    root.state = 0

# TODO: consider an outer loop that accounts for branching?
while main_world.formula_tree:
    solver_loop(main_world)
print("\nBRANCH COMPLETE \nend tableau solver output")

# start setup: first, set variables for the amount of atoms, agents, length of formula to generate
# and generate it. returns a Model-class object (from here on: world)
formula_length = randint(1, 100)
main_world = make_model(formula_length)

# check the formula through a tableau and report the results
# returns whether the formula is a tautology (True or False)
tautology = tableau_solver(main_world)