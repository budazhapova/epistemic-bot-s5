import json
from anytree.importer import JsonImporter
from formulaBuilder import render_branch
from stringConverter import *

newfile = open("test_file.json", "r")
# j_object = json.load(newfile)
newdata = newfile.read()
print(type(newdata))

importer = JsonImporter()
# newdata = importer.read(newfile)
root = importer.import_(newdata)
render_branch(root)

newfile.close()