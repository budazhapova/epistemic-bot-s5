class Model:
    # number of atoms (letters) and agents (digits) is passed when instance is created
    def __init__(self, num_atoms, num_agents, num_states = 1):
        self.atoms = [chr(ord('a') + i) for i in range(num_atoms)]
        self.states = list(range(num_states))
        # initialize every state with list of atoms and their truth valuations
        for state in self.states:
            self.states[state] = dict.fromkeys(self.atoms, None)
        self.agents = list(range(num_agents))

    # TODO: remove if proves unneeded
    # start with letter 'a' and add new atoms alphabetically as needed
    def add_atom(self):
        self.atoms.append(chr(ord('a') + len(self.atoms)))

    # add a new state to the list and populate it with existing atoms (no truth values yet)
    # def initialize_state(self):
    #     for state in self.states:
    #         self.states[state] = dict.fromkeys(self.atoms, None)
    
    # check atom's truth value in a given state
    def access_atom(self, atom, valuation, state_id):
        print("state ", state_id, ": ", self.states[state_id])
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
        
    # add accessibility relation to an numbered agent's list
    # `state2' gets added to the list `state1` is on, otherwise both get added
    def add_relation(self, state1, state2, agent):
        for relation in self.agents[agent]:
            if state1 in relation:
                relation.append(state2)
                break
        else:
            self.agents[agent].append([state1, state2])

    def print_atoms(self):
        for atom in self.atoms:
            print(atom)

    def print_states(self):
        for state in self.states:
            print(state)



model = Model(2, 3, 2)
# for x in range(5):
#    model.add_atom()
# model.initialize_state()
model.print_atoms()
model.print_states()
print("end model file output")