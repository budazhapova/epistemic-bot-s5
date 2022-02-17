# class Model defines possible model as explored by tableau solver
from copy import deepcopy

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
    
    # records a copy of given subformula to the model's sidebar for future use
    def copy_subformula(self, root, destination):
        root_index = len(destination)
        # destination.append(root)
        # destination.extend(root.descendants)
        destination.append(deepcopy(root))
        return root_index


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