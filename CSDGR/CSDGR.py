import argparse
import ProcessMetrics 
import ProcessDependency
import GraphRepresentation
import ProcessLabel
import Model
from sklearn.model_selection import train_test_split
import os


parser = argparse.ArgumentParser()

parser.add_argument('--project', type=str, default="ALL", help='need to detect project, default:ALL')
parser.add_argument('--emb_size', type=str, default="-1", help='node embedding size:-1,8,16,32,64, default:16')
parser.add_argument('--embedding_method', type=str, default="ALL", help="'metrics','neighRep','neighRep_metrics','attrRep','attrRep_metrics', default:ALL'")
parser.add_argument('--embedding_algorithm', type=str, default="ALL", help="struct:'RandNE','GLEE','Diff2Vec','NodeSketch','NetMF','BoostNE','Walklets',\
    'GraRep','DeepWalk','Node2Vec','NMFADMM','LaplacianEigenmaps', atrr:'FeatherNode','BANE','TENE','TADW','FSCNMF', default:ALL'")
parser.add_argument('--classifier_algorithm', type=str, default="ALL", help="'LR','SVM','DecisionTree','RandomForest', default:ALL")
parser.add_argument('--smell_type', type=str, default="ALL", help="'LM','FE','GC',, default:ALL")

args = parser.parse_args()

def deal_args(args):
    #all projects
    projects = ['flink-java',]
    #embedding size
    emb_sizes = [8,16,32,64]
    #all embedding method
    embedding_methods = ['metrics','neighRep','neighRep_metrics','attrRep','attrRep_metrics']
    #all Neighbourhood based node embedding algorithm
    neighbourhood_algorithms = ['RandNE','GLEE','NodeSketch','NetMF','BoostNE','Walklets',\
                                'GraRep','DeepWalk','Node2Vec','NMFADMM','LaplacianEigenmaps',\
                                'Role2Vec','Diff2Vec']#'LINE','SDNE',
    #all Attributed node embedding algorithm
    attributed_algorithms = ['FeatherNode','BANE','TENE','TADW','FSCNMF']
    #all Classifier algorithm
    classifier_algorithms = ['LR','SVM','DecisionTree','RandomForest','DL']
    #smell type
    smell_types= ['LM','FE','GC']


    if args.project != "ALL":
        projects = [args.project]
    if args.emb_size != '-1':
        emb_sizes = [int(args.emb_size)]

    if args.embedding_method == 'metrics':
        emb_sizes = [0]
        embedding_methods = [args.embedding_method]

    if args.embedding_method == 'neighRep' or args.embedding_method == 'neighRep_metrics':
        if args.embedding_algorithm != "ALL":
            embedding_methods = [args.embedding_method]
            neighbourhood_algorithms = [args.embedding_algorithm]
        else:
            embedding_methods = [args.embedding_method]
    if args.embedding_method == 'attrRep' or args.embedding_method == 'attrRep_metrics':
        if args.embedding_algorithm != "ALL":
            embedding_methods = [args.embedding_method]
            attributed_algorithms = [args.embedding_algorithm]
        else:
            embedding_methods = [args.embedding_method]
    if args.classifier_algorithm != 'ALL':
        classifier_algorithms = [args.classifier_algorithm]
    if args.smell_type != 'ALL':
        smell_types = [args.smell_type]

    return projects,emb_sizes,embedding_methods,neighbourhood_algorithms,attributed_algorithms,classifier_algorithms,smell_types






def main():

    projects,emb_sizes,embedding_methods,neighbourhood_algorithms,attributed_algorithms,classifier_algorithms,smell_types = deal_args(args)
    print(projects,emb_sizes,embedding_methods,neighbourhood_algorithms,attributed_algorithms,classifier_algorithms,smell_types)

    
    for project in projects:
        #process project jasome metric.xml
        metrics_src_path = "./JasomeMetrics/" + project + "_jasome_metrics.xml"
        metrics_path = "./Metrics/" + project + "_metrics.txt"  #处理完xml，metrics的保存路径
        jasome_indicators_path = './JaSome_Indicators.txt'  #jasome指标说明路径

        if not os.path.exists(metrics_path):
            ProcessMetrics.process_metrics(metrics_src_path,metrics_path,jasome_indicators_path)

        #process project dependency
        ast_path = "./SrcmlAst/" + project + "_ast.xml"
        #dependency = ProcessDependency.process_dependency(ast_path,metrics_path)    #返回所有依赖，[(x,x),...]用于构造图的边

        #build project graph
        graph = GraphRepresentation.build_graph(ast_path,metrics_path)

        #model predict and eval
        
        for embedding_method in embedding_methods:  #['metrics','neighRep','neighRep_metrics','attrRep','attrRep_metrics']
            embedding_algorithms = ['NULL']
            if embedding_method == 'neighRep' or embedding_method == 'neighRep_metrics':#['RandNE','GLEE','Diff2Vec','NodeSketch','NetMF','BoostNE','Walklets','GraRep','DeepWalk','Node2Vec','NMFADMM','LaplacianEigenmaps']
                embedding_algorithms = neighbourhood_algorithms
            elif embedding_method == 'attrRep' or embedding_method == 'attrRep_metrics':
                embedding_algorithms = attributed_algorithms
            else:
                pass
            
            
            for classifier_algorithm in classifier_algorithms:
                for smell_type in smell_types:
                    for embedding_algorithm in embedding_algorithms:
                        for emb_dim in emb_sizes:
                            Model.model_prediction(project,embedding_method,embedding_algorithm,emb_dim,classifier_algorithm,smell_type,graph,metrics_path,k=5)


if __name__ == "__main__":
    main()

