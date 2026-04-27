import networkx as nx
import matplotlib.pyplot as plt
import random
import os

class SIR:
    def __init__(self,number):
        self.Number = number


    def random_infected(self, G, state, initial_infected):
        infected = random.sample(list(G.nodes()), initial_infected)
        for node in infected:
            state[node] = "I"
        return state

    def infected(self, state):
        state[self.Number] = "I"
        return state

    def is_infected(self, state):
        if any(node == "I" for node in state.values()):
            return True
        elif all(node == "I" for node in state.values()):
            return False
        elif all(s != "I" for s in state.values()):
            return False
        else:
            return False

    def sir_simulation(self, G, beta=0.3, gamma=0.1, initial_infected=1, random_infected=False, infected=False):
        state = {node: "S" for node in G.nodes()}

        if random_infected:
            state = self.random_infected(G, state, initial_infected)
        elif infected:
            state = self.infected(state)

        history = []
        counter = 0

        while self.is_infected(state):
            new_state = state.copy()

            for node in G.nodes():
                if state[node] == "I":
                    for neighbor in G.neighbors(node):
                        if state[neighbor] == "S" and random.random() < beta:
                            new_state[neighbor] = "I"

                    if random.random() < gamma:
                        new_state[node] = "R"

            state = new_state

            S = sum(1 for s in state.values() if s == "S")
            I = sum(1 for s in state.values() if s == "I")
            R = sum(1 for s in state.values() if s == "R")
            history.append((S, I, R))
            counter += 1

        return history

def plotSIR(S, I, R):
    plt.plot(S, label="Susceptible")
    plt.plot(I, label="Infected")
    plt.plot(R, label="Recovered")
    plt.legend()
    plt.show()

path = os.path.join("networks", "network_0_T14423.txt")
G = nx.read_edgelist(path)

sir = SIR(number=0)

history = sir.sir_simulation(G, random_infected=True,initial_infected=1)
S, I, R = zip(*history)

plotSIR(S, I, R)