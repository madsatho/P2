import pyalex
import networkx as nx
import matplotlib.pyplot as plt

pyalex.config.api_key = "V11Jtt2BpqUgS9jg50bbnu"

#Denne linje er langsom pga vi loader hele json filen ind og assigner den. Har ikke fundet et fix endnu 🙁
while True:
    random_work = pyalex.Works().random()
    if random_work['referenced_works_count']>=1:
        break


paper = {
    "id": random_work["id"].split('/')[-1],
    "referenced_works_count": random_work["referenced_works_count"],
    "referenced_works": random_work["referenced_works"],
}
paper["referenced_works"]=[i.split('/')[-1] for i in paper["referenced_works"]]

print(paper)

G = nx.DiGraph()

main_id = paper["id"]
G.add_node(main_id)

#Add edges from main work -> referenced works
for ref in paper.get("referenced_works", []):
    G.add_node(ref)
    G.add_edge(main_id, ref)

#Draw graph
plt.figure()
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_size=30)
plt.show()