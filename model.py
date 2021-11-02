class Model:
    def __init__(self, atoms, states, agents):
        self.atoms = list()
        self.states = list()
        self.agents = list()

    # start with letter 'a' and add new atoms alphabetically as needed
    def add_atom(self):
        self.atoms.append(chr(ord('a') + len(self.atoms)))

    # add a new state to the list and populate it with existing atoms (no truth values yet)
    def initialize_state(self):
        self.states.append(dict.fromkeys(self.atoms))

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



model = Model(None, None, None)
for x in range(5):
    model.add_atom()
model.initialize_state()
model.print_atoms()
model.print_states()