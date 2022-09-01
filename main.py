from model import Model
from formulaBuilder import generate_formula
from tableauSolver import *
from presets import *
from recordManager import retrieve_formulas, json_to_tree, write_formulas, record_data_to_csv
from formulaMatcher import compare_formulas
from random import randint
import time
import tracemalloc
import sys      # TODO: remove when not needed

# setup for generating a formula: amount of connectives/operators, atoms, and agents
# shorter formulas have fewer variables
# returns a Model-class object with already generated formula
def make_model(formula_length, WORKMODE):
    agents_total = 1
    if formula_length < 5:
        atoms_total = 1
    elif formula_length < 10:
        atoms_total = 2
    elif formula_length < 20:
        atoms_total = 2
        agents_total = 2
    else:
        atoms_total = 3
        if formula_length > 40:
            agents_total = 3
        else:
            agents_total = 2
    # generate formula of given length and max operator priority
    if WORKMODE == "generate":
        main_world = Model(atoms_total, agents_total)
        generate_formula(main_world, formula_length)
    # or load a preset formula from presets
    elif WORKMODE == "load":
        # CHANGE ATOMS/AGENTS FOR EVERY PRESET
        main_world = Model(2, 2)
        main_world.formula_tree = load_preset(8)
        main_world.node_total = len(main_world.formula_tree)
    
    return main_world




# start setup: first, set variables for the amount of atoms, agents, length of formula to generate
# and generate it. returns a Model-class object (from here on: world)
# outcomes: 0 - formula already exists
#           1 - formula is new and was evaluated
#           2 - formula is new and a tautology
#           -1 - formula was generated improperly and can't be evaluated
def main_function(WORKMODE, formula_length=randint(3, 150)):
    # formula_length = randint(3, 15)
    # FIXME: put call in this file, enable randomness back after data gathering
    if WORKMODE == "load":
        formula_length = 7      # CHANGES DEPENDING ON PRESET
    # FIXME: correct max length back to (150?) after testing
    main_world = make_model(formula_length, WORKMODE)
    proof_world = main_world.copy_model()

    # here the we compare newly generated formula to those already on file
    all_roots = main_world.find_roots(main_world.formula_tree)
    new_root = all_roots[0]
    # calculate depth of the model
    main_world.estimate_depth(new_root)
    # retrieve already recorded formulas from appropriate file
    data_list = retrieve_formulas(formula_length)
    # for every recorded formula, convert back to tree form and compare to the new formula
    if data_list:
        print("COMPARING TO FILE")
        for json_obj in data_list:
            old_formula = json_to_tree(json_obj)
            formula_match = compare_formulas(old_formula, new_root)
            print(f"Exact match to new formula: {formula_match}")
            # if such formula has already been generated, abort
            if formula_match == True:
                print(translate_formula(new_root))
                print("\nFORMULA ALREADY EXISTS")
                return 0
                # sys.exit("\nFORMULA ALREADY EXISTS")


    # start tracking time and RAM usage of the tableau solver
    start_time = time.process_time()
    tracemalloc.start()

    # check the formula through a tableau and report the results
    # returns whether the formula is a tautology (True or False)
    tautology = tableau_solver(proof_world)
    solving_time = time.process_time() - start_time
    current_memory, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    # if formula is not a valid one, do not record anything
    if tautology == -1:
        return -1

    # orig_roots = main_world.find_roots(main_world.formula_tree)
    print("\nTAUTOLOGY = ", tautology)
    print(translate_formula(new_root))
    print(f"Tableau of length {formula_length} and depth {main_world.model_depth} solved in {solving_time} seconds (CPU time) and {peak_memory} bytes peak memory")

    # write generated formula to appropriate file
    write_formulas(formula_length, new_root, data_list)
    # if new formula was proven a tautology, record it in a separate file
    if tautology == True:
        tautology_list = retrieve_formulas("tautologies")
        for obj in tautology_list:
            old_tautology = json_to_tree(obj)
            formula_match = compare_formulas(old_tautology, new_root)
            if formula_match == True:
                break
        if formula_match == False:
            write_formulas("tautologies", new_root, tautology_list)

    # ["length", "depth", "tautology", "CPU time (sec)", "memory (bytes)"]
    row = [formula_length, main_world.model_depth, tautology, solving_time, peak_memory]
    record_data_to_csv("testdata", row)
    if tautology == True:
        return 2
    else:
        return 1


WORKMODE = "generate"
# WORKMODE = "load"

# FIXME: put randomness back to 150 max later
# main_function("generate", randint(3,15))