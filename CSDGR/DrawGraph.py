import matplotlib.pyplot as plt
import networkx as nx
import GraphRepresentation

project = 'flink-java'
ast_path = "./SrcmlAst/" + project + "_ast.xml"
metrics_path = "./Metrics/" + project + "_metrics.txt"

G = GraphRepresentation.build_graph(ast_path,metrics_path)
pos = nx.spring_layout(G)
#colors = range(1,20)
options = {
    "node_color": "#A0CBE2",
    "edge_color": "#A0CBE2",
    "width": 2,
    "edge_cmap": plt.cm.Blues,
    "with_labels": False,
}
nx.draw(G, pos, **options)
plt.show()