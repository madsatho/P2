# P2

This project investigated how centrality algorithms can minimize disease spread by identifying and vaccinating super-spreaders in a simulated network. Based on an author collaboration network constructed via the OpenAlex API, disease dynamics were modelled using a SVIR model, which extends the classical SIR model with a vaccinated state. 

Three centrality measures were examined as vaccination strategies: degree centrality, betweenness centrality, and PageRank. The results show that centrality-based vaccination statistically significantly reduces both peak infection and epidemic duration compared to random vaccination and no vaccination. PageRank and betweenness centrality are statistically equivalent as strategies. 

The project concludes that targeted vaccination of the most central nodes in the network is an effective method for limiting disease spread, but that the model has limitations, including a static network and a lack of consideration for individual mortality risk.
