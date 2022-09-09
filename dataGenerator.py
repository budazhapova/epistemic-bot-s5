from main import main_function
from recordManager import retrieve_formulas, json_to_tree

formula_length = 15
duds = 0
new_formulas = 0
duplicates = 0
tautologies = 0
counter = 0

for i in range(200):
    outcome = main_function("generate", formula_length)
    while outcome == -1:
        outcome = main_function("generate", formula_length)
        duds += 1
    if outcome == 0:
        main_function("generate", formula_length)
        duplicates += 1
    else:
        if outcome == 2:
            tautologies += 1
        new_formulas += 1

# print("\n\nFORMULAS FROM FILE\n")
json_data = retrieve_formulas(formula_length)
for obj in json_data:
    counter += 1
    # print(counter)
    json_to_tree(obj)
# print(f"\nBATCH RESULTS:\nNEW FORMULAS GENERATED - {new_formulas}\nof which {tautologies} are tautologies\nDUPLICATES - {duplicates}\nDUDS - {duds}")