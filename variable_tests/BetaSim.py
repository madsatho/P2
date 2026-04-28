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
        df = pd.read_csv(f"Stat_{self.graph_id}.csv")

        n = int(0.05 * len(self.nodes))

        if NumNeighbors:
            sorted_df = df.sort_values(by="NumNeighbors", ascending=False)
        elif Betweenness:
            sorted_df = df.sort_values(by="Betweenness", ascending=False)
        elif PageRank:
            sorted_df = df.sort_values(by="PageRank", ascending=False)
        else:
            raise ValueError("Choose a method")

        top_nodes = sorted_df.head(n)["Node"].tolist()

        return top_nodes

#-----------------------------------------------------------------------------------------

class SIR:
    def __init__(self, Graph, target, nodes, beta = 0.3, gamma = 0.1, initial_infected = 1, vax_eff = 0.999, vax_fraction = 0.05):
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
        n = int(self.vax_fraction * len(self.nodes))

        if vacc_strategy == "random":
            targets = set(random.sample(self.nodes, n))
        elif vacc_strategy == "targeted":
            targets = set(self.target)
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

                        if state[neighbor] == "V" and random.random() < (1-self.vax_eff):
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
    def __init__(self,network, beta = 0.3, gamma = 0.1, initial_infected = 1, vax_eff = 0.999, vax_fraction = 0.05):
        self.network = network
        self.path = os.path.join("networks", network)
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
            sir = SIR(Graph=self.G, target=target, nodes=self.nodes, beta=self.beta, gamma=self.gamma, initial_infected=self.initial_infected)

            if mode == "targeted":
                history = sir.SIR_sim(vacc_strategy="targeted")
            elif mode == "random":
                history = sir.SIR_sim(vacc_strategy="random")
            elif mode == "none":
                history = sir.SIR_sim()
            else:
                raise ValueError("Invalid mode")

            I = [state[1] for state in history]
            top.append(max(I))

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
        results = {k: sum(v) / len(v) for k, v in results.items()}
        return results

        #df = pd.DataFrame(results)
        #if Save:
            #df.to_csv(f"SIR_results_{self.network}.csv", index=False)
        #print(df.describe().drop("count").T)
        #df.boxplot()
        #plt.show()

#--------------------------------------------------------------------------------------------------

class SimSandBox:
    def __init__(self, network):
        self.network = network
        self.path = os.path.join("networks", network)
        self.G = nx.read_edgelist(self.path)
        self.nodes = self.G.nodes()

    def SandBox(self):
        x=0
        run = run_SIR_Simulation(self.network, beta=0, gamma=0.2, initial_infected=5, vax_eff=0.95, vax_fraction=0.05)
        beta_dict = {k: [v] for k, v in run.results().items()}
        for i in range(10):
            x += 0.05
            run = run_SIR_Simulation(self.network, beta=x, gamma=0.2, initial_infected=5, vax_eff=0.95,vax_fraction=0.05)
            new_results = run.results()

            for k in beta_dict:
                beta_dict[k].append(new_results[k])
        return beta_dict
box = SimSandBox("network_0_T13370.txt")
test=box.SandBox()
print(test)


betas = [0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45,0.5]

for strategy, values in test.items():
    plt.plot(betas, values, label=strategy)

plt.legend()
plt.xlabel("Beta")
plt.ylabel("Mean peak infections")
plt.show()