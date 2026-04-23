import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import random


class simulation:
    def __init__(self, graph, nodes, id):
        self.graph_id = id
        self.graph    = graph
        self.nodes    = list(nodes)
        self.n        = int(0.05 * len(nodes))

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

        return sorted_df.head(n)["Node"].tolist()


#-----------------------------------------------------------------------------------------

class SIR:
    def __init__(self, Graph, target, nodes, beta=0.3, gamma=0.1, initial_infected=1, vax_eff=0.999, vax_fraction=0.05):
        self.graph            = Graph
        self.target           = target
        self.nodes            = list(nodes)
        self.beta             = beta
        self.gamma            = gamma
        self.initial_infected = initial_infected
        self.vax_eff          = vax_eff
        self.vax_fraction     = vax_fraction

    def random_infected(self, state, initial_infected):
        susceptible_nodes = [n for n in self.nodes if state[n] == "S"]
        infected = random.sample(susceptible_nodes, initial_infected)
        for node in infected:
            state[node] = "I"
        return state

    def is_infected(self, state):
        return any(v == "I" for v in state.values())

    def SIR_sim(self, vacc_strategy="targeted"):
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
        while self.is_infected(state):
            new_state = state.copy()

            for node in self.graph.nodes():
                if state[node] == "I":
                    for neighbor in self.graph.neighbors(node):
                        if state[neighbor] == "S" and random.random() < self.beta:
                            new_state[neighbor] = "I"
                        if state[neighbor] == "V" and random.random() < (1 - self.vax_eff):
                            new_state[neighbor] = "I"
                    if random.random() < self.gamma:
                        new_state[node] = "R"

            state = new_state
            S = sum(1 for s in state.values() if s == "S")
            I = sum(1 for s in state.values() if s == "I")
            R = sum(1 for s in state.values() if s == "R")
            V = sum(1 for s in state.values() if s == "V")
            history.append((S, I, R, V))

        return history


#-----------------------------------------------------------------------------------------------------

class run_SIR_Simulation:
    def __init__(self, network, beta=0.3, gamma=0.1, initial_infected=1, vax_eff=0.999, vax_fraction=0.05):
        self.network          = network
        self.path             = network
        self.G                = nx.read_edgelist(self.path)
        self.nodes            = self.G.nodes()
        self.beta             = beta
        self.gamma            = gamma
        self.initial_infected = initial_infected
        self.vax_eff          = vax_eff
        self.vax_fraction     = vax_fraction

    def run_simulation(self, target=None, mode="targeted"):
        top = []
        for i in range(30):
            sir = SIR(Graph=self.G, target=target, nodes=self.nodes, beta=self.beta,
                      gamma=self.gamma, initial_infected=self.initial_infected)

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
                print(f"  simulation {i}")

        return top

    def results(self, Save=False):
        graph_id = os.path.splitext(os.path.basename(self.network))[0]
        sim = simulation(self.G, self.nodes, graph_id)

        strategies = {
            "DegreeTargeted":      ("targeted", sim.finde_Vax_target(NumNeighbors=True)),
            "BetweennessTargeted": ("targeted", sim.finde_Vax_target(Betweenness=True)),
            "PageRankTargeted":    ("targeted", sim.finde_Vax_target(PageRank=True)),
            "RandomVaccination":   ("random", []),
            "NoVaccination":       ("none", [])
        }

        results = {}
        for name, (mode, target) in strategies.items():
            print(f"Running {name}")
            results[name] = self.run_simulation(target=target, mode=mode)

        df = pd.DataFrame(results)
        if Save:
            df.to_csv(f"SIR_results_{graph_id}.csv", index=False)
        print(df.describe().drop("count").T)
        df.boxplot()
        plt.savefig(r"C:\Users\madsh\P2\boxplot.png")
        plt.show()

    def results_over_gamma(self, gamma_values=None, Save=False):
        if gamma_values is None:
            gamma_values = np.array([0.01, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50])
            #Hvilke gamma værdier der skal testes, overvej at fjern 0.01 da den tager meget lang tid.

        strategies = ["DegreeTargeted", "BetweennessTargeted", "PageRankTargeted", "RandomVaccination", "NoVaccination"]
        all_results = {s: [] for s in strategies}

        graph_id = os.path.splitext(os.path.basename(self.network))[0]
        sim = simulation(self.G, self.nodes, graph_id)

        targets = {
            "DegreeTargeted":      sim.finde_Vax_target(NumNeighbors=True),
            "BetweennessTargeted": sim.finde_Vax_target(Betweenness=True),
            "PageRankTargeted":    sim.finde_Vax_target(PageRank=True),
            "RandomVaccination":   [],
            "NoVaccination":       []
        }
        modes = {
            "DegreeTargeted":      "targeted",
            "BetweennessTargeted": "targeted",
            "PageRankTargeted":    "targeted",
            "RandomVaccination":   "random",
            "NoVaccination":       "none"
        }

        for gamma in gamma_values:
            #For loop, som kører alle gamma værdier
            print(f"Running gamma={gamma:.2f}")
            self.gamma = gamma
            for name in strategies:
                top = self.run_simulation(target=targets[name], mode=modes[name])
                all_results[name].append(np.mean(top))

        fig, ax = plt.subplots(figsize=(10, 6))
        for name in strategies:
            ax.plot(gamma_values, all_results[name], marker="o", label=name)

        #Opstilling af grafen
        ax.set_xlabel("Gamma (recovery rate)")
        ax.set_ylabel("Mean peak infections")
        ax.set_title("Effect of gamma on peak infections by vaccination strategy")
        ax.legend()
        ax.grid(True)
        plt.tight_layout()
        plt.savefig(r"C:\Users\madsh\P2\gamma_sweep.png")
        if Save:
            plt.savefig("gamma_sweep.png")
        plt.show()


#--------------------------------------------------------------------------------------------------

class SimSandBox:
    def __init__(self, network):
        self.network = network
        self.G       = nx.read_edgelist(self.network)
        self.nodes   = self.G.nodes()

    def SandBox(self):
        run = run_SIR_Simulation(self.network, gamma=0.05, initial_infected=10, beta=0.10)
        run.results()

    def SandBoxGamma(self):
        run = run_SIR_Simulation(self.network, initial_infected=10, beta=0.10)
        run.results_over_gamma()


box = SimSandBox(r"C:\Users\madsh\P2\network_0_T13370.txt")
box.SandBoxGamma()