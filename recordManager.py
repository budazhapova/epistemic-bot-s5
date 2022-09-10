from model import Model
from formulaBuilder import render_branch
import json
import csv
from pathlib import Path
from anytree.exporter import DictExporter 
from anytree.importer import DictImporter
from presets import *
from stringConverter import *


# SUMMARY: this file contains code for reading and writing formulas into JSON files, as well as storing data output in CSV

# this method reads previously recorded formulas from file as json objects.
# if file doesn't yet exist, nothing happens
def retrieve_formulas(filename):
    data_list = []
    path = Path(f"{filename}.json")       # files separated  by number of connectives
    # check is file exists, then read data from it (to data_list) and print retrieved formulas
    if path.is_file():
        with open(f"{filename}.json", "r") as test_file:
            data_list = json.loads(test_file.read())
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