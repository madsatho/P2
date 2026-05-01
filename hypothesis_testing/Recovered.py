import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import os
import random


class simulation:
    def __init__(self, graph, nodes, id):
        self.graph_id =  id
        self.graph    =  graph
        self.nodes    =  list(nodes)
        self.n        =  int(0.05 * len(nodes))

    def finde_Vax_target(self, NumNeighbors=False, Betweenness=False, PageRank=False):
        stat_location=os.path.join("..", "MetaData(csv og txt)",f"Stat_{self.graph_id}.csv")
        df = pd.read_csv(stat_location)


        if NumNeighbors:
            sorted_df = df.sort_values(by="NumNeighbors", ascending=False)
        elif Betweenness:
            sorted_df = df.sort_values(by="Betweenness", ascending=False)
        elif PageRank:
            sorted_df = df.sort_values(by="PageRank", ascending=False)
        else:
            raise ValueError("Choose a method")

        top_nodes = sorted_df["Node"].tolist()

        return top_nodes

#-----------------------------------------------------------------------------------------

class SIR:
    def __init__(self, Graph, target, nodes, beta, gamma, initial_infected, vax_eff, vax_fraction):
        self.graph = Graph
        self.target = target
        self.nodes = list(nodes)
        self.beta = beta
        self.gamma = gamma
        self.initial_infected = initial_infected
        self.vax_eff = vax_eff
        self.vax_fraction = vax_fraction

    def random_infected(self, state, initial_infected):
        susceptible_nodes = [n for n in self.nodes if state[n] == "S"]
        infected = random.sample(susceptible_nodes, initial_infected)
        for node in infected:
            state[node] = "I"
        return state


    def is_infected(self, state):
        if any(node == "I" for node in state.values()):
            return True
        else:
            return False

    def SIR_sim(self,  vacc_strategy="targeted"):
        state = {node: "S" for node in self.graph.nodes()}
        n = round(self.vax_fraction * len(self.nodes))

        if vacc_strategy == "random":
            targets = set(random.sample(self.nodes, n))
        elif vacc_strategy == "targeted":
            targets = set(self.target[:n])
        else:
            targets = set()

        for node in targets:
            state[node] = "V"

        state = self.random_infected(state, self.initial_infected)

        history = []
        counter = 0

        while self.is_infected(state):
            new_state = state.copy()

            for node in self.graph.nodes():
                if state[node] == "I":
                    for neighbor in self.graph.neighbors(node):

                        if state[neighbor] == "S" and random.random() < self.beta:
                            new_state[neighbor] = "I"
                        elif state[neighbor] == "V" and random.random() < self.beta * (1 - self.vax_eff):
                            new_state[neighbor] = "I"

                    if random.random() < self.gamma:
                        new_state[node] = "R"

            state = new_state

            S = sum(1 for s in state.values() if s == "S")
            I = sum(1 for s in state.values() if s == "I")
            R = sum(1 for s in state.values() if s == "R")
            V = sum(1 for s in state.values() if s == "V")

            history.append((S, I, R, V))

            counter += 1

        return history


#-----------------------------------------------------------------------------------------------------
#"network_0_T13370.txt"

class run_SIR_Simulation:
    def __init__(self,network, beta = 0.3, gamma = 0.1, initial_infected = 1, vax_eff = 0.99, vax_fraction = 0.2):
        self.network = network
        self.path = os.path.join("..","MetaData(csv og txt)","networks", network)
        self.G = nx.read_edgelist(self.path)
        self.nodes = self.G.nodes()
        self.beta = beta
        self.gamma = gamma
        self.initial_infected = initial_infected
        self.vax_eff = vax_eff
        self.vax_fraction = vax_fraction


    def run_simulation(self, target=None, mode="targeted"):
        top = []

        for i in range(30):
            sir = SIR(Graph=self.G, target=target, nodes=self.nodes, beta=self.beta, gamma=self.gamma, initial_infected=self.initial_infected, vax_eff=self.vax_eff, vax_fraction=self.vax_fraction)

            if mode == "targeted":
                history = sir.SIR_sim(vacc_strategy="targeted")
            elif mode == "random":
                history = sir.SIR_sim(vacc_strategy="random")
            elif mode == "none":
                history = sir.SIR_sim()
            else:
                raise ValueError("Invalid mode")

            R = [state[2] for state in history]
            top.append(max(R))

            if i % 10 == 0:
                print(f"simulation {i}")

        return top

    def results(self, Save=False):
        sim = simulation(self.G, self.nodes, self.network)

        strategies = {
            "DegreeTargeted": ("targeted", sim.finde_Vax_target(NumNeighbors=True)),
            "BetweennessTargeted": ("targeted", sim.finde_Vax_target(Betweenness=True)),
            "PageRankTargeted": ("targeted", sim.finde_Vax_target(PageRank=True)),
            "RandomVaccination": ("random", []),
            "NoVaccination": ("none", [])
        }

        results = {}

        for name, (mode, target) in strategies.items():
            print(f"Running {name}")
            results[name] = self.run_simulation(target=target, mode=mode)


        df = pd.DataFrame(results)
        if Save:
            df.to_csv(f"SIR_results_{self.network}.csv", index=False)
        print(df.describe().drop("count").T)
        df.boxplot()
        plt.xticks(rotation=45, ha='right')
        plt.show()

#--------------------------------------------------------------------------------------------------

class SimSandBox:
    def __init__(self, network):
        self.network = network
        self.path = os.path.join("..","MetaData(csv og txt)","networks", network)
        self.G = nx.read_edgelist(self.path)
        self.nodes = self.G.nodes()

    def SandBox(self):
        run = run_SIR_Simulation(self.network,beta = 0.02, gamma = 0.01, initial_infected = 1, vax_eff = 0.95, vax_fraction = 0.017)
        run.results()


box = SimSandBox("network_0_T13370.txt")
box.SandBox()





