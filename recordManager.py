from model import Model
from formulaBuilder import render_branch
import json
import csv
from pathlib import Path
from anytree.exporter import DictExporter 
from anytree.importer import DictImporter
from presets import *
from stringConverter import *

# WORKMODE = "generate"
# # WORKMODE = "load"
# formula_length = 7

# if WORKMODE == "load":
#     formula_length = 7
#     main_world = Model(2, 2)
#     main_world.formula_tree = load_preset(5)
#     main_world.node_total = len(main_world.formula_tree)
# elif WORKMODE == "generate":
#     main_world = Model(2, 2)
#     generate_formula(main_world, formula_length)


# this method reads previously recorded formulas from file as json objects.
# if file doesn't yet exist, nothing happens
def retrieve_formulas(filename):
    data_list = []
    # importer = DictImporter()
    path = Path(f"{filename}.json")       # files separated  by number of connectives
    # check is file exists, then read data from it (to data_list) and print retrieved formulas
    if path.is_file():
        with open(f"{filename}.json", "r") as test_file:
            data_list = json.loads(test_file.read())
            # print("loaded data type: ", type(data_list))
            # print("1st element type: ", type(data_list[0]))
            # converts data from json to tree and prints it
            # for elem in data_list:
            #     root = importer.import_(elem)
            #     render_branch(root)
            #     print(translate_formula(root), end="\n\n")
                # print(elem)
            # if not data_list:
            #     print("NO DATA RETRIEVED")
    return data_list

# converts retrieved json object to anytree-type tree and prints
def json_to_tree(json_obj_formula):
    importer = DictImporter()
    root = importer.import_(json_obj_formula)
    # render_branch(root)
    # print(translate_formula(root)[0], end="\n\n")
    return root

#TODO: WRITING OTHER RESULTS: time, memory, length, and depth
# print newly generated formula and append it to data_list
# for r in roots:
#     render_branch(r)
#     print(translate_formula(r), end="\n\n")
#     new_data = exporter.export(r)
#     data_list.append(new_data)

# overwrite the old file with new formula appended to the end
def write_formulas(filename, new_formula, data_list):
    if new_formula:
        exporter = DictExporter()
        new_data = exporter.export(new_formula)
        data_list.append(new_data)
    with open(f"{filename}.json", "w") as test_file:
        jobj = json.dumps(data_list)
        # print(type(jobj))
        test_file.write(jobj)

# record data for analysis into a csv file
def record_data_to_csv(filename, new_row):
    path = Path(f"{filename}.csv")
    # if file doesn't exist, write header before enterine new row of data
    file_exists = path.is_file()
    with open(f"{filename}.csv", "a", newline="") as data_file:
        header = ["length", "depth", "tautology", "CPU time (sec)", "peak memory (bytes)"]
        writer = csv.writer(data_file)
        # if file had not existed before, first write the header on top
        if not file_exists:
            writer.writerow(header)
        writer.writerow(new_row)