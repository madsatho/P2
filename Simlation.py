import networkx as nx
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
    def __init__(self, Graph, target, nodes):
        self.graph = Graph
        self.target = target
        self.nodes = list(nodes)
        self.n = int(0.05 * len(nodes))

    def random_infected(self, state, initial_infected):
        infected = random.sample(list(self.graph.nodes()), initial_infected)
        for node in infected:
            state[node] = "I"
        return state


    def is_infected(self, state):
        if any(node == "I" for node in state.values()):
            return True
        else:
            return False

    def SIR_sim(self, beta=0.3, gamma=0.1, initial_infected=1, random_infected=False, taget_infected=False):
        state = {node: "S" for node in self.graph.nodes()}

        if random_infected:
            targets = set(random.sample(list(self.nodes), self.n))
        elif taget_infected:
            targets = set(self.target)
        else:
            targets = []

        for node in targets:
            state[node] = "V"

        state = self.random_infected(state, initial_infected)

        history = []
        counter = 0

        while self.is_infected(state):
            new_state = state.copy()

            for node in self.graph.nodes():
                if state[node] == "I":
                    for neighbor in self.graph.neighbors(node):
                        if state[neighbor] == "S" and random.random() < beta:
                            new_state[neighbor] = "I"

                        if state[neighbor] == "V" and random.random() < 0.01:
                            new_state[neighbor] = "I"

                    if random.random() < gamma:
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


class run_SIR_Simulation:
    def __init__(self,network):
        self.network = network
        self.path = os.path.join("networks", network)
        self.G = nx.read_edgelist(self.path)
        self.nodes = self.G.nodes()

    def peak_sim(self,target):
        top = []

        for i in range(100):
            sir = SIR(Graph=self.G, target=target, nodes=self.nodes)
            history = sir.SIR_sim(beta=0.3, gamma=0.1, taget_infected=True)

            I = [state[1] for state in history]
            top.append(max(I))

            if i % 10 == 0:
                print(f"simulation {i}")

        return top

    def idk(self, target):
        top = []

        for i in range(100):
            sir = SIR(Graph=self.G, target=target, nodes=self.nodes)
            history = sir.SIR_sim(beta=0.3, gamma=0.1, random_infected=True)

            I = [state[1] for state in history]
            top.append(max(I))

            if i % 10 == 0:
                print(f"simulation {i}")

        return top

    def idk2(self, target):
        top = []

        for i in range(100):
            sir = SIR(Graph=self.G, target=target, nodes=self.nodes)
            history = sir.SIR_sim(beta=0.3, gamma=0.1)

            I = [state[1] for state in history]
            top.append(max(I))

            if i % 10 == 0:
                print(f"simulation {i}")

        return top

    def results(self):
        sim = simulation(self.G, self.nodes, self.network)

        targets = {
            "NumNeighbors": sim.finde_Vax_target(NumNeighbors=True),
            "Betweenness": sim.finde_Vax_target(Betweenness=True),
            "PageRank": sim.finde_Vax_target(PageRank=True),
            "NormSIM": [],
            "TestSIM": []
        }

        results = {}

        for name, vax_target in targets.items():
            print(f"Running {name}")

            if name == "NormSIM":
                results[name] = self.idk(vax_target)
            elif name == "TestSIM":
                results[name] = self.idk2(vax_target)
            else:
                results[name] = self.peak_sim(vax_target)


        df = pd.DataFrame(results)
        df.to_csv("SIR_results.csv", index=False)

run = run_SIR_Simulation("network_0_T13370.txt")
run.results()