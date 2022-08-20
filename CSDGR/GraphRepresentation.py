import ProcessDependency
import ProcessMetrics
import networkx as nx
import karateclub
import numpy as np

def build_graph(ast_path,metrics_path):
    nodes = ProcessMetrics.get_node_id(metrics_path)
    edges = ProcessDependency.process_dependency(ast_path,metrics_path)
    
    graph = nx.Graph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)

    return graph

def choose_model_without_feature(algorithm,emb_dim):
    #Neighbourhood_based_node_embedding
    if algorithm == 'RandNE':
        model = karateclub.RandNE(dimensions=emb_dim)
    elif algorithm == 'GLEE':
        model = karateclub.GLEE(dimensions=emb_dim)
    elif algorithm == 'Diff2Vec':
        model = karateclub.Diff2Vec(dimensions=emb_dim)
    elif algorithm == 'NodeSketch':
        model = karateclub.NodeSketch(dimensions=emb_dim)
    elif algorithm == 'NetMF':
        model = karateclub.NetMF(dimensions=emb_dim)
    elif algorithm == 'BoostNE':
        model = karateclub.BoostNE(dimensions=emb_dim)
    elif algorithm == 'Walklets':
        model = karateclub.Walklets(dimensions=emb_dim)
    elif algorithm == 'GraRep':
        model = karateclub.GraRep(dimensions=emb_dim)
    elif algorithm == 'DeepWalk':
        model = karateclub.DeepWalk(dimensions=emb_dim)
    elif algorithm == 'Node2Vec':
        model = karateclub.Node2Vec(dimensions=emb_dim)
    elif algorithm == 'NMFADMM':
        model = karateclub.NMFADMM(dimensions=emb_dim)
    elif algorithm == 'LaplacianEigenmaps':
        model = karateclub.LaplacianEigenmaps(dimensions=emb_dim)

    #Structural node embedding
    elif algorithm == 'Role2Vec':
        model = karateclub.Role2Vec(dimensions=emb_dim)
    else:
        print("embedding algorithm is not exist!")
        exit(0)
    return model

def get_node_embedding_without_feature(algorithm,graph,emb_dim):
    model = choose_model_without_feature(algorithm,emb_dim)
    model.fit(graph)
    X = model.get_embedding()
    X = np.array(X)
    return X

#---------------------------------------------------------------------------------
#------------Attributed node embedding-----------------------
def choose_model_with_feature(algorithm,emb_dim):
    if algorithm == 'FeatherNode':
        model = karateclub.FeatherNode(reduction_dimensions=emb_dim)
    elif algorithm == "BANE":
        model = karateclub.BANE(dimensions=emb_dim)
    elif algorithm == "TENE":
        model = karateclub.TENE(dimensions=emb_dim)
    elif algorithm == "TADW":
        model = karateclub.TADW(dimensions=emb_dim)
    elif algorithm == "FSCNMF":
        model = karateclub.FSCNMF(dimensions=emb_dim)
    else:
        print("embedding algorithm is not exist!")
        exit(0)
    return model     



def get_node_embedding_with_feature(algorithm,graph,features,emb_dim):
    model = choose_model_with_feature(algorithm,emb_dim)
    model.fit(graph,features)
    X = model.get_embedding()
    X = np.array(X)
    return X

def concat(X1,X2):
    X = np.hstack((X1,X2))
    return X

def node_represetation(embedding_method,embedding_algorithm,emb_dim,smell_type,metrics_path,graph):
    #['metrics','neighRep','neighRep_metrics','attrRep','attrRep_metrics']
    #get node attribute
    attributes = ProcessMetrics.get_attribute(metrics_path)
    X = []
    if embedding_method == 'metrics':   #直接采用metrics进行分类训练预测
        X = attributes
    elif embedding_method == 'neighRep':
        X = get_node_embedding_without_feature(embedding_algorithm,graph,emb_dim)
    elif embedding_method == 'neighRep_metrics':    #neighRep + metrics
        X = concat(attributes,get_node_embedding_without_feature(embedding_algorithm,graph,emb_dim))
    elif embedding_method == 'attrRep':
        X = get_node_embedding_with_feature(embedding_algorithm,graph,attributes,emb_dim)
    elif embedding_method == 'attrRep_metrics':
        X = concat(attributes,get_node_embedding_with_feature(embedding_algorithm,graph,attributes,emb_dim))
    X_index = ProcessMetrics.get_X_index(smell_type,metrics_path)
    X = np.array(X[X_index])
    return X


def main():
    project = 'flink-java'
    ast_path = "./SrcmlAst" + project + "_ast.xml"
    metrics_path = "./Metrics/" + project + "_metrics.txt"

    graph = build_graph(ast_path,metrics_path)
    features = ProcessMetrics.get_feature(metrics_path)
    x = get_node_embedding_without_feature('Node2Vec',graph)
    #graph = nx.newman_watts_strogatz_graph(100, 20, 0.05)
    #x = get_RandNE_embedding(graph)
    #x = get_NetMF_embedding(graph)
    print(x)

if __name__ == "__main__":
    main()



