import GraphRepresentation
from sklearn.model_selection import train_test_split
from  sklearn import metrics
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from karateclub.dataset import GraphReader
import ProcessLabel
import ProcessMetrics
from sklearn.model_selection import KFold
import numpy as np
from tensorflow import keras


def print_info(project,embedding_method,embedding_algorithm,emb_dim,smell_type,classifier_algorithm,kflod):
    print("-----------------------------------------------------------------------------------------------------------------------------------------")
    print("project:%s , embedding_method:%s , embedding_algorithm:%s, emb_size:%s , smell_type:%s , classifier_algorithm:%s , kflod:%s ."\
             % (project,embedding_method,embedding_algorithm,emb_dim,smell_type,classifier_algorithm,str(kflod)))

def get_classifier_model(classifier_algorithm,X_train, y_train):

    if classifier_algorithm == 'LR':
        downstream_model = LogisticRegression(max_iter=500).fit(X_train, y_train)
    elif classifier_algorithm == 'SVM':
        downstream_model = SVC(probability=True).fit(X_train,y_train)
    elif classifier_algorithm == 'DecisionTree':
        downstream_model = DecisionTreeClassifier().fit(X_train,y_train)
    elif classifier_algorithm == 'RandomForest':
        downstream_model = RandomForestClassifier().fit(X_train,y_train)
    elif classifier_algorithm == 'DL':
        f_size = np.shape(X_train)[1]
        print(f_size)
        input_ = keras.layers.Input(shape=((f_size,)),name="input")
        hidden1 = keras.layers.Dense(50,activation='relu')(input_)
        output_ = keras.layers.Dense(1,name="output",activation='sigmoid')(hidden1)
        deep_model = keras.Model(inputs=[input_],outputs=[output_])
        deep_model.compile(optimizer=keras.optimizers.Adam(), loss='binary_crossentropy', metrics='accuracy')
        early_stopping_cb = keras.callbacks.EarlyStopping(patience=50,restore_best_weights=True)
        deep_model.fit(X_train,y_train,batch_size=32,epochs=100,validation_split=0.2,validation_freq=1,callbacks=[early_stopping_cb])
        return deep_model
    else:
        print("classifier algorithm is not exist!")
        exit(0)
    return downstream_model

#def evaluate(y_test,y_hat,y_hat_p):
def evaluate(y_test,y_hat,):
    precision = metrics.precision_score(y_test,y_hat,zero_division=0)
    recall = metrics.recall_score(y_test,y_hat,zero_division=0)
    F1 = metrics.f1_score(y_test, y_hat,zero_division=0)
    #auc = metrics.roc_auc_score(y_test, y_hat_p,)
    #return [precision,recall,F1,auc]
    return [precision,recall,F1]


def model_prediction(project,embedding_method,embedding_algorithm,emb_dim,classifier_algorithm,smell_type,graph,metrics_path,k=5):

    print_info(project,embedding_method,embedding_algorithm,emb_dim,smell_type,classifier_algorithm,k)

    #根据embedding_method,embedding_algorithm,emb_dim返回不同的训练X
    X = GraphRepresentation.node_represetation(embedding_method,embedding_algorithm,emb_dim,smell_type,metrics_path,graph)
    y = ProcessLabel.process_label(smell_type,project,metrics_path)

    #K折交叉检验
    result = []
    kfold = KFold(n_splits=k, shuffle=True,)
    for train_index,test_index in kfold.split(X):
        X_train,y_train = X[train_index],y[train_index]
        X_test,y_test = X[test_index],y[test_index]

        downstream_model = get_classifier_model(classifier_algorithm,X_train,y_train)
        #if classifier_algorithm !='DL':
        #y_hat_p = downstream_model.predict_proba(X_test)[:, 1]
        y_hat = downstream_model.predict(X_test)
        if classifier_algorithm =='DL':
            y_hat = np.reshape(y_hat,(1,-1))[0]
        #print("---------------y_hat:",np.shape(y_hat))
        #print("---------------y_:",np.reshape(y_hat,(1,-1)))
        #try:
            #result.append(evaluate(y_test,y_hat,y_hat_p))
        result.append(evaluate(y_test,y_hat,))
        #except:
            #pass
    '''
    if embedding_method == 'metrics':
        precision,recall,F1,auc = np.mean(result,axis=0)
    else:
        precision,recall,F1,auc = np.max(result,axis=0)
    '''
    #precision,recall,F1,auc = np.mean(result,axis=0)
    print("result:",result)
    precision,recall,F1 = np.mean(result,axis=0)
    print('precision: {:.4f}'.format(precision))
    print('recall: {:.4f}'.format(recall))
    print('F1: {:.4f}'.format(F1))
    #print('AUC: {:.4f}'.format(auc))



    
def metrics_prediction(classifier_algorithm,X,y):
    #X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    #K折交叉检验
    result = []
    kfold = KFold(n_splits=5, shuffle=True,)
    for train_index,test_index in kfold.split(X):
        X_train,y_train = X[train_index],y[train_index]
        X_test,y_test = X[test_index],y[test_index]
        downstream_model = get_classifier_model(classifier_algorithm,X_train,y_train)

        y_hat_p = downstream_model.predict_proba(X_test)[:, 1]
        y_hat = downstream_model.predict(X_test)
        result.append(evaluate(y_test,y_hat,y_hat_p))

    precision,recall,F1,auc = np.mean(result,axis=0)

    print('precision: {:.4f}'.format(precision))
    print('recall: {:.4f}'.format(recall))
    print('F1: {:.4f}'.format(F1))
    print('AUC: {:.4f}'.format(auc))

    


def main():
    
    graph = GraphRepresentation.graph_build()
    features = ProcessMetrics.get_feature()
    #X = GraphRepresentation.get_SINE_embedding(graph,features)
    #X = GraphRepresentation.get_FeatherNode_embedding(graph,features)
    #X = GraphRepresentation.get_NetMF_embedding(graph)

    #X = GraphRepresentation.get_Neighbourhood_based_node_embedding('DeepWalk',graph,emb_dim=32)
    X = GraphRepresentation.get_node_embedding_with_feature("FeatherNode",graph,features,)
    y = ProcessLabel.process_label('lm')
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)



    '''LR
    #downstream_model = LogisticRegression(random_state=0).fit(X_train, y_train)
    #y_hat = downstream_model.predict_proba(X_test)[:, 1]
    #y_ = downstream_model.predict(X_test)
    '''

    '''SVM
    downstream_model = SVC(probability=True).fit(X_train,y_train)
    y_hat_p = downstream_model.predict_proba(X_test)[:, 1]
    y_hat = downstream_model.predict(X_test)
    '''

    '''DecisionTree
    downstream_model = DecisionTreeClassifier().fit(X_train,y_train)
    y_hat = downstream_model.predict_proba(X_test)[:, 1]
    y_ = downstream_model.predict(X_test)
    '''

    #'''RandomForest
    downstream_model = RandomForestClassifier().fit(X_train,y_train)
    y_hat_p = downstream_model.predict_proba(X_test)[:, 1]
    y_hat = downstream_model.predict(X_test)
    #'''

    precision = metrics.precision_score(y_test,y_hat)
    print('precision: {:.4f}'.format(precision))

    recall = metrics.recall_score(y_test,y_hat)
    print('recall: {:.4f}'.format(recall))

    F1 = metrics.f1_score(y_test, y_hat)
    print('F1: {:.4f}'.format(F1))

    auc = metrics.roc_auc_score(y_test, y_hat_p)
    print('AUC: {:.4f}'.format(auc))


if __name__ == "__main__":
    main()