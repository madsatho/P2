import pandas as pd
import os
import json
from itertools import combinations
import requests
import networkx as nx


class DataCollector:
    def __init__(self, topcis):
        self.topcis = topcis
        self.folder = f"Works_ids_json_{topcis}"

    def getData(self):
        df = pd.read_csv("MetaData.csv")
        cursor = "*"

        mask = df["id"] == self.topcis
        page = df.loc[mask, "pages"].values[0] + 1

        url = "https://api.openalex.org/works"
        os.makedirs(self.folder, exist_ok=True)

        try:
            while True:
                file_path = os.path.join(
                    self.folder,
                    f"works_ids_page_{page}_{str(self.topcis)}.json"
                )


                if os.path.exists(file_path):
                    print(f"Page {page} already exists. Skipping...")
                    page += 1
                    continue

                params = {
                    "filter": f"topics.id:{self.topcis}",  # filtrer på specifikt topic ID
                    "per-page": 200,  # max antal resultater per side
                    "cursor": cursor,  # cursor til næste side
                }

                try:
                    # send GET request til API
                    r = requests.get(url, params=params, timeout=10)
                    data = r.json()  # parse JSON response
                except Exception as e:
                    # hvis request fejler, prøv igen
                    print(f"Request failed: {e}. Retrying...")
                    continue

                # tjek om response indeholder forventede data
                if "results" not in data:
                    print("API error:", data)
                    break

                records = []

                # gennemgå alle works i response
                for work in data["results"]:
                    records.append({
                        "id": work.get("id"),  # work ID
                        "title": work.get("display_name"),  # titel
                        "authors": [
                            {
                                "name": a["author"]["display_name"],  # forfatternavn
                                "id": a["author"]["id"]  # forfatter ID
                            }
                            for a in work.get("authorships", [])  # liste af forfattere
                        ],
                    })

                # gem data til JSON-fil
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(records, f, indent=2, ensure_ascii=False)

                print(f"Saved page {page} ({len(records)} records)")


                cursor = data["meta"].get("next_cursor")
                if not cursor:
                    print("No more pages left.")
                    break

                page += 1

        except KeyboardInterrupt:
            print("\nStopped manually by user")

        finally:
            df = pd.read_csv("MetaData.csv")
            mask = df["id"] == self.topcis
            df.loc[mask, "pages"] = page
            df.to_csv("MetaData.csv", index=False)
            self.edge_list()

            print("Saving data...")

    def edge_list(self):
        folder_path = f"Works_ids_json_{self.topcis}"

        combined = []

        for filename in os.listdir(folder_path):
            if filename.endswith(".json"):
                path = os.path.join(folder_path, filename)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            combined.extend(data)
                except Exception as e:
                    print(f"Error reading {filename}: {e}")

        seen = set()

        def get_id(a):
            if isinstance(a, dict):
                val = a.get("id")
                if isinstance(val, str):
                    return val.split("/")[-1]
                return None

        with open(f"edges_{self.topcis}.txt", "w", encoding="utf-8") as out:
            for item in combined:
                authors = item.get("authors", [])

                for a1, a2 in combinations(authors, 2):
                    id1 = get_id(a1)
                    id2 = get_id(a2)

                    if not id1 or not id2 or id1 == id2:
                        continue

                    edge = tuple(sorted((id1, id2)))

                    if edge not in seen:
                        seen.add(edge)
                        out.write(f"{edge[0]},{edge[1]}\n")

    def netwokCreator(self):
        input_file = f"edges_{self.topcis}.txt"
        output_dir = "networks"
        os.makedirs(output_dir, exist_ok=True)

        G = nx.Graph()

        with open(input_file, "r") as f:
            for line in f:
                parts = line.strip().split()

                for part in parts:
                    if "," not in part:
                        continue

                    u, v = part.split(",", 1)
                    u = u.strip()
                    v = v.strip()

                    if u and v:
                        G.add_edge(u, v)

        print(f"Loaded {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")

        components = sorted(nx.connected_components(G), key=len, reverse=True)
        top_components = components[:50]

        results = []

        for i, comp in enumerate(top_components):
            subgraph = G.subgraph(comp)

            filename = os.path.join(output_dir, f"network_{i}_{self.topcis}.txt")

            with open(filename, "w") as f:
                for u, v in subgraph.edges():
                    f.write(f"{u} {v}\n")

            num_nodes = subgraph.number_of_nodes()
            num_edges = subgraph.number_of_edges()
            density = nx.density(subgraph)

            results.append({
                "title": f"network_{i}_{self.topcis}.txt",
                "Nodes": num_nodes,
                "Edges": num_edges,
                "density": density
            })

        df = pd.DataFrame(results)
        csv_path = os.path.join(f"network_summary_{self.topcis}.csv")
        df.to_csv(csv_path, index=False)


    def any(self,edge=False):
        self.getData()
        if edge:
            self.edge_list()

df = pd.read_csv("MetaData.csv")
topic = df["id"][1]
d = DataCollector(topic)
d.getData()