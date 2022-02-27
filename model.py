# class Model defines possible model as explored by tableau solver
from copy import deepcopy
from anytree import PreOrderIter

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
                if state1 or state2 in set:
                    set.update({state1, state2})
    
    # sever parent-child association between nodes
    def detach_parent(self, oper_node):
        for child in oper_node.children:
            child.parent = None

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
            new_branch.append(deepcopy(node))
        return new_branch

    # removes an entire branch/subformula from the formula_tree
    def wipe_branch(self, tree, current_node):
        # if node is not terminal
        if not current_node.is_leaf:
            # recursively traverse down to the leaves
            for child in current_node.children:
                self.wipe_branch(tree, child)
        # wipe current nodes from leaves up
        # current_node.parent = None
        tree.remove(current_node)
        return

    
    # returns an exact copy of the current model
    def copy_model(self):
        new_model = deepcopy(self)
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