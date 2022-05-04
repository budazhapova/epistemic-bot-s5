from ast import NodeTransformer
from anytree import Node

# preset formulas:
# 1 -- (not-a or not-b)

def load_preset(num_preset):
    preset_tree = []
    if num_preset == 1:
        nodeOr = Node("OR", type="operator", priority=5, state=None, id=5)
        preset_tree.append(nodeOr)
        nodeA2 = Node("NEG", parent=nodeOr, type="operator", priority=1, state=None, id=2)
        preset_tree.append(nodeA2)
        nodeA = Node("a", parent=nodeA2, type="atom", priority=0, state=None, id=1)
        preset_tree.append(nodeA)
        nodeB2 = Node("NEG", parent=nodeOr, type="operator", priority=1, state=None, id=3)
        preset_tree.append(nodeB2)
        nodeB = Node("b", parent=nodeB2, type="atom", priority=0, state=None, id=4)
        preset_tree.append(nodeB)
    elif num_preset == 2:
        nodeTop = Node("AND", type="operator", priority=2, state=None, id=1)
        preset_tree.append(nodeTop)
        nodeA = Node("a", parent=nodeTop, type = "atom", priority=0, state=None, id=2)
        preset_tree.append(nodeA)
        nodeAnd = Node("AND", parent=nodeTop, type="operator", priority=2, state=None, id=3)
        preset_tree.append(nodeAnd)
        nodeB = Node("b", parent=nodeAnd, type="atom", priority=0, state=None, id=4)
        preset_tree.append(nodeB)
        nodeC = Node("c", parent=nodeAnd, type="atom", priority=0, state=None, id=5)
        
    return preset_tree
