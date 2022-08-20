import numpy as np
import re
import ProcessMetrics


def build_name_id_metrics_map(metrics_path):
    name_id_metrics_map = {}
    with open(metrics_path, "r") as f:
        for line in f.readlines():
            line = line.strip('\n').split("\t")
            node_id = line[0]   #节点id
            node_name = line[2]
            node_metrics = list(map(eval,line[3].split(",")))#将字符串转为数字型
            name_id_metrics_map[node_name] = [node_id,node_metrics]
    return name_id_metrics_map

def process_feature_envy(fe_path,metrics_path):
    fe_method = []
    feature_envy_label = []
    with open(fe_path,"r") as f:
        for line in f.readlines():
            line = line.strip('\n').split("\t")  #去掉每行换行符并进行切分
            method_name = re.findall(r'(.*)\(',line[1])[0]
            if method_name not in fe_method:
                fe_method.append(method_name)

    with open(metrics_path, "r") as f:
        for line in f.readlines():
            line = line.strip('\n').split("\t")
            node_name = line[2]

            if node_name in fe_method:
                feature_envy_label.append(1)
            else:
                feature_envy_label.append(0)
    feature_envy_label = np.array(feature_envy_label)
    return feature_envy_label


def process_god_class(gc_path,metrics_path):
    gc_class = []
    god_class_label = []
    with open(gc_path,"r") as f:
        for line in f.readlines():
            line = line.strip('\n').split("\t")  #去掉每行换行符并进行切分
            class_name = line[0]
            if class_name not in gc_class:
                gc_class.append(class_name)

    with open(metrics_path, "r") as f:
        for line in f.readlines():
            line = line.strip('\n').split("\t")
            node_name = line[2]
            
            if node_name in gc_class:
                god_class_label.append(1)
            else:
                god_class_label.append(0)
    god_class_label = np.array(god_class_label)
    return god_class_label

def process_long_method(lm_path,metrics_path):
    lm_method = []
    long_method_label = []
    with open(lm_path,"r") as f:
        for line in f.readlines():
            line = line.strip('\n').split("\t")  #去掉每行换行符并进行切分
            class_name = line[0]
            method_name = class_name + "::" + re.findall(r' (\w+)\(',line[1])[0]
            if method_name not in lm_method:
                lm_method.append(method_name)

    with open(metrics_path, "r") as f:
        for line in f.readlines():
            line = line.strip('\n').split("\t")
            node_name = line[2]
            if node_name in lm_method:
                long_method_label.append(1)
            else:
                long_method_label.append(0)
    long_method_label = np.array(long_method_label)
    return long_method_label

def get_smell_path(project,smell_type):
    if smell_type == 'LM':
        smell_path = "./LongMethod/" + project + "_lm.txt"
        return smell_path
    elif smell_type == 'FE':
        return "./FeatureEnvy/" + project + "_fe.txt"
    elif smell_type == 'GC':
        return "./GodClass/" + project + "_gc.txt"
    else:
        print("not found smell path")
        exit(0)

def process_label(smell_type,project,metrics_path):
    smell_path = get_smell_path(project,smell_type)
    if smell_type == 'LM':
        method_id_index = ProcessMetrics.get_method_id_index(metrics_path)
        return process_long_method(smell_path,metrics_path)[method_id_index]
    elif smell_type == 'GC':
        class_id_index = ProcessMetrics.get_class_id_index(metrics_path)
        return process_god_class(smell_path,metrics_path)[class_id_index]
    elif smell_type == 'FE':
        method_id_index = ProcessMetrics.get_method_id_index(metrics_path)
        return process_feature_envy(smell_path,metrics_path)[method_id_index]
    else:
        print("lable type is not exist!")
        exit(0)
    

def main():
    #print("long method label:",process_label('lm'))
    #print("god class label:",process_label('gc'))
    #print("feature envy label:",process_label('fe'))
    pass


if __name__ == "__main__":
    main()