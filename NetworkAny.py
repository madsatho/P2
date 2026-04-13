import networkx as nx
import pandas as pd
import os

class networkANY:
    def __init__(self, filename):
        self.filename = filename
        self.graph = os.path.join("networks", self.filename)
    def shortest_paths(self):
        # Load graph
        G = nx.read_edgelist(self.graph)  # nodes are strings by default

        # Compute all shortest paths
        all_lengths = dict(nx.all_pairs_shortest_path_length(G))

        # Prepare data: average shortest path length and number of neighbors
        data = []

        for node, lengths in all_lengths.items():
            avg_path = sum(lengths.values()) / (len(lengths) - 1) if len(lengths) > 1 else 0
            num_neighbors = len(list(G.neighbors(node)))
            data.append([node, avg_path, num_neighbors])

        return data

    def PageRankAndBetweenness(self):
        G = nx.read_edgelist(self.graph)
        rank = nx.pagerank(G)
        betweenness = nx.betweenness_centrality(G)
        data = self.shortest_paths()

        for row in data:
            node_id = row[0]  # first element is the node

            if node_id in rank:
                row.append(rank[node_id])
                row.append(betweenness[node_id])

        return data


    def saveData(self):
        # Convert to pandas DataFrame
        df = pd.DataFrame(self.PageRankAndBetweenness(), columns=["Node", "AverageShortestPathLength", "NumNeighbors", "Betweenness", "pagerank"])

        # Save to CSV
        df.to_csv(f"Stat_{self.filename}.csv", index=False)

        print("Saved average shortest paths and number of neighbors to CSV.")

s = networkANY(filename="network_36_T13370.txt")
s.saveData()
