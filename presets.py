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
    elif num_preset == 3:
        nodeBiImp = Node("BI_IMP", type="operator", priority=2, state=None, id=1)
        preset_tree.append(nodeBiImp)
        nodeA = Node("a", parent=nodeBiImp, type = "atom", priority=0, state=None, id=2)
        preset_tree.append(nodeA)
        nodeB = Node("b", parent=nodeBiImp, type="atom", priority=0, state=None, id=3)
        preset_tree.append(nodeB)
    # with epistemic operators:
    elif num_preset == 4:
        nodeBiImp = Node("BI_IMP", type="operator", priority=5, state=None, id=1)
        preset_tree.append(nodeBiImp)
        nodeK = Node("K", parent=nodeBiImp, type="operator", priority=3, state=None, id=2)
        preset_tree.append(nodeK)
        preset_tree.append(Node(1, parent=nodeK, type="agent", state=None, priority=0, id=3))
        nodeM1 = Node("M", parent=nodeK, type="operator", priority=4, state=None, id=4)
        preset_tree.append(nodeM1)
        preset_tree.append(Node(1, parent=nodeM1, type="agent", state=None, priority=0, id=5))
        nodeA = Node("a", parent=nodeM1, type = "atom", priority=0, state=None, id=6)
        preset_tree.append(nodeA)

        nodeM2 = Node("M", parent=nodeBiImp, type="operator", priority=4, state=None, id=7)
        preset_tree.append(nodeM2)
        preset_tree.append(Node(1, parent=nodeM2, type="agent", state=None, priority=0, id=8))
        nodeM3 =  Node("M", parent=nodeM2, type="operator", priority=4, state=None, id=9)
        preset_tree.append(nodeM3)
        preset_tree.append(Node(1, parent=nodeM3, type="agent", state=None, priority=0, id=10))
        nodeA2 = Node("a", parent=nodeM3, type ="atom", priority=0, state=None, id=11)
    elif num_preset == 5:
        nodeImp = Node("IMP", type="operator", priority=5, state=None, id=1)
        preset_tree.append(nodeImp)
        nodeK1 = Node("K", parent=nodeImp, type="operator", priority=3, state=None, id=2)
        preset_tree.append(nodeK1)
        preset_tree.append(Node(1, parent=nodeK1, type="agent", state=None, priority=0, id=3))
        nodeOr1 = Node("OR", parent=nodeK1, type="operator", priority=5, state=None, id=4)
        preset_tree.append(nodeOr1)
        nodeK2 = Node("K", parent=nodeOr1, type="operator", priority=3, state=None, id=5)
        preset_tree.append(nodeK2)
        preset_tree.append(Node(2, parent=nodeK2, type="agent", state=None, priority=0, id=6))
        nodeA1 = Node("a", parent=nodeK2, type ="atom", priority=0, state=None, id=7)
        preset_tree.append(nodeA1)
        nodeK3 = Node("K", parent=nodeOr1, type="operator", priority=3, state=None, id=8)
        preset_tree.append(nodeK3)
        preset_tree.append(Node(2, parent=nodeK3, type="agent", state=None, priority=0, id=9))
        nodeB1 = Node("b", parent=nodeK3, type ="atom", priority=0, state=None, id=10)
        preset_tree.append(nodeB1)

        nodeK4 = Node("K", parent=nodeImp, type="operator", priority=3, state=None, id=11)
        preset_tree.append(nodeK4)
        preset_tree.append(Node(1, parent=nodeK4, type="agent", state=None, priority=0, id=12))
        nodeOr2 = Node("OR", parent=nodeK4, type="operator", priority=5, state=None, id=13)
        preset_tree.append(nodeOr2)
        nodeA2 = Node("a", parent=nodeOr2, type ="atom", priority=0, state=None, id=14)
        preset_tree.append(nodeA2)
        nodeB2 = Node("b", parent=nodeOr2, type ="atom", priority=0, state=None, id=15)
        preset_tree.append(nodeB2)

    return preset_tree
