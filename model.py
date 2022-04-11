# class Model defines possible model as explored by tableau solver
from copy import deepcopy
from anytree import Node, PreOrderIter

class Model:
    # number of atoms (letters) and agents (digits) is passed when instance is created
    def __init__(self, num_atoms, num_agents, num_states = 1):
        self.atoms = [chr(ord('a') + i) for i in range(num_atoms)]
        self.states = list(range(num_states))
        # initialize every state with list of atoms and their truth valuations
        for state in self.states:
            self.states[state] = dict.fromkeys(self.atoms, None)
        # agents from 0 to num_agents (upper bound of range is exclusive)
        # agent 0 is empty padding to ensure index matches agent id
        self.agents = list(range(num_agents+1))
        self.formula_tree = []
        self.sidebar = []
        self.node_total = 0

    # TODO: remove if proves unneeded
    # start with letter 'a' and add new atoms alphabetically as needed
    def add_atom(self):
        self.atoms.append(chr(ord('a') + len(self.atoms)))

    # add a new state to the list and populate it with existing atoms (no truth values yet)
    def add_state(self):
        new_state = dict.fromkeys(self.atoms, None)
        self.states.append(new_state)
    
    # check atom's truth value in a given state
    def access_atom(self, atom, valuation, state_id):
        # print("state ", state_id, ": ", self.states[state_id])
        # if no value set, record truth valuation
        if self.states[state_id].get(atom) == None:
            self.states[state_id].update({atom: valuation})
            return True
        # if new truth value differs from old, report contradiction
        elif self.states[state_id].get(atom) != valuation:
            return False


    # TODO: remove if not needed or adjust
    # add a new agent with an empty list of accessibility relations
    def initialize_agent(self):
        self.agents.append(list(None))
        
    # checks whether this state-agent combo has any accessibility relations
    def check_relations(self, state, agent):
        # if no accessbility relations recorded yet
        if not isinstance(self.agents[agent], list):
            return None
        # else look in that agent's sets and return known relations
        else:
            for set in self.agents[agent]:
                if state in set:
                    return set
    
    # adds new accessibility relation to the set
    def add_relation(self, state1, state2, agent):
        # if no relations recorded for this agent, add a new set into list
        if not isinstance(self.agents[agent], list):
            self.agents[agent] = []
            self.agents[agent].append({state1, state2})
            print(f"agent {agent} relation recorded: {self.agents[agent]}")
            return
        # otherwise, search within existing sets
        else:
            for set in self.agents[agent]:
                if state1 in set or state2 in set:
                    set.update({state1, state2})
            return
    
    # sever parent-child association between nodes
    def detach_parent(self, oper_node):
        for child in oper_node.children:
            child.parent = None
            if child.is_root:
                print(f"parent {oper_node.name} successfully detached from child {child.name}")
            else:
                print(f"FAILURE DETACHING FROM for node {child.name}")

    # remove a node from the middle of branch and knit the edges
    def remove_branch_node(self, parent_node, middle_node, formula_tree):
        state_id = parent_node.state
        successor = middle_node.children[0]
        # pass state to child node
        self.confer_state(successor, state_id)
        # change branch structure
        middle_node.parent = None
        successor.parent = parent_node
        # erase the middle node
        formula_tree.remove(middle_node)

    # pass parent's state identifier to children (we stay in the same state)
    def inherit_state(self, oper):
        for child in oper.children:
            child.state = oper.state

    # set children's state to new_state
    def confer_state(self, oper, new_state):
        for child in oper.children:
            child.state = new_state

    # FIXME: should I put the state-assigning back here?
    # remove epistemic operator nodes from tree
    def remove_epist_op(self, epist_op, formula_tree):
        for child in epist_op.children:
            if child.type == "agent":
                formula_tree.remove(child)
            else:
                child.parent = None
        formula_tree.remove(epist_op)

    # records a copy of given subformula to the model's sidebar for future use, returns root index
    def copy_subformula(self, root, destination):
        root_index = len(destination)
        # destination.append(root)
        # destination.extend(root.descendants)
        # FIXME: see if append or extend works better
        destination.append(deepcopy(root))
        return root_index
    
    # copies a branch of formula node by node and return the resulting list
    def replicate_branch(self, root):
        new_branch = []
        for node in PreOrderIter(root):
            # copy all node attributes without referencing original-tree nodes
            newnode = Node(node.name, type=node.type, state=node.state, priority=node.priority, id=node.id)
            # replicate parent-child relations in the new copy
            parent_id = node.parent.id
            for replica in new_branch:
                if replica.id == parent_id:
                    newnode.parent = replica
            new_branch.append(newnode)
            # FIXME: is likely unnecessary; remove later?
            # if root-node has parents, detach it
            # if node == root and not root.is_root:
            #     new_branch[-1].parent = None
        if len(new_branch) < 1:
            print("copying branch failed!")
        else:
            print(f"branch copied with {len(new_branch)} nodes")
        return new_branch

    # removes an entire branch/subformula from the formula_tree
    def wipe_branch(self, tree, current_node):
        # if node is not terminal
        if not current_node.is_leaf:
            # recursively traverse down to the leaves
            print(f"traversing node {current_node.name}")
            for child in current_node.children:
                self.wipe_branch(tree, child)
        # wipe current nodes from leaves up
        # current_node.parent = None
        print(f"wiping node {current_node.name}")
        if current_node in tree:
            print(f"{current_node.name} wiped from list")
            tree.remove(current_node)
        else:
            print(f"{current_node.name} not found in tree/list")
            del current_node
        return

    
    # returns an exact copy of the current model
    def copy_model(self, roots_main, roots_sidebar):
        new_model = Model(len(self.atoms), len(self.agents), len(self.states))
        new_model = deepcopy(self)
        if len(roots_main) < 1:
            print("NO ROOTS PASSED DURING COPYING of pre-attach model")
        for n in roots_main:
            new_branch = self.replicate_branch(n)
            new_model.formula_tree.extend(new_branch)
            print(f"new model copy has {len(new_model.formula_tree)} nodes")
        # new_model.formula_tree = deepcopy(self.formula_tree)
        for s in roots_sidebar:
            branch_copy = self.replicate_branch(s)
            new_model.sidebar.extend(branch_copy)
        # new_model.sidebar = deepcopy(self.sidebar)
        new_model.states = deepcopy(self.states)
        if not new_model:
            print("model object copying failed!")
        else:
            print(f"copied model consists of: {len(new_model.formula_tree)} tree nodes and {len(new_model.states)} states")
        return new_model


    def print_atoms(self):
        for atom in self.atoms:
            print(atom)

    def print_states(self):
        for state in self.states:
            print(f"state {self.states.index(state)}: {state}")



# model = Model(2, 3, 2)
# for x in range(5):
#    model.add_atom()
# model.initialize_state()
# model.print_atoms()
# model.print_states()
# print("end model file output")