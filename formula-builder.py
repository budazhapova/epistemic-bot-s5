import model
from anytree import Node, RenderTree, ContStyle

#TODO: randomise formula tree building

#TODO: load requirements from file?

num_atoms = 1
num_agents = 1

# possible types of operators/connectives:
# | for `or`, & for 'and', ~ for `not`
# K, M, ^ for `implies`

# dict formula_tree will store the numbered nodes so that they can't be confused with one another
keynum = 0
formula_tree = {}

# TODO: judge if I actually need it
def write_atom(atom):
    leaf = Node(atom)

def make_neg(formula, keynum):
    #globals()[f"node{keynum}"] = Node("neg")
    #globals()[f"node{keynum+1}"] = Node(formula, parent=globals()[f"node{keynum}"])
    # formula_tree.update({keynum: Node("neg")})
    # formula_tree.update({keynum + 1: Node(formula, parent=formula_tree[keynum])})
    formula_tree[keynum] = Node("neg")
    formula_tree[keynum+1] = Node(formula, parent=formula_tree[keynum])
    keynum += 2




make_neg("p", keynum)
#print(node0)
#print(node1)
#print(RenderTree(node1))
#print(node0.children)
print(formula_tree)
print(RenderTree(formula_tree[0], style=ContStyle()))
#keynum = 0
#formula_tree.clear()
print("end formula-builder output")