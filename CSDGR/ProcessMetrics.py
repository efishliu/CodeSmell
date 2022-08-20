from lxml import etree
import re
from sklearn import preprocessing
from tqdm import tqdm
import numpy as np

#将数组转换为字符串,用sep隔开
def arr_to_string(arr,sep=','):
    s = ""
    for v in arr:
        s += str(v)
        s += sep
    s = s[:-1]
    return s

#将代码的测试指标写入path
#(节点id 节点类型 节点名 节点测试指标 节点源文件路径)
def write_metrics(path,node_id,node_type,node_name,node_metrics,source_file):
    f = open(path,"a+",encoding="utf-8")
    f.write(str(node_id))
    f.write("\t")
    f.write(node_type)
    f.write("\t")
    f.write(node_name)
    f.write("\t")
    f.write(node_metrics)
    f.write("\t")
    f.write(source_file)
    f.write("\n")
    f.close()

    
#初始化测试指标
def process_init_metrics(init_indicator_path):
    init_metrics = {}
    with open(init_indicator_path,"r") as f:
        for line in f.readlines():
            line = line.split("\t") #每行进行划分
            metric_type = line[0]   #该指标的类型:P(package),C(class),M(method)
            metric_name = line[1]   #该指标的简写
            metric = metric_type + "_" + metric_name    #将指标改写为:type_name形式进行区分
            init_metrics[metric] = 0  #初始化所有指标为0
    return init_metrics

def process_metrics_name(node_type,metrics_name_list):
    #将指标改写为:type_name形式
    #如将package下的LOC改为P_LOC
    for i in range(len(metrics_name_list)):
        metrics_name_list[i] = node_type + "_" + metrics_name_list[i]
    return metrics_name_list

def update_metrics(node_metrics,jasome_indicators_path,metrics_name,metrics_values):
    init_metrics = process_init_metrics(jasome_indicators_path)
    #更新测试指标
    for i in range(len(metrics_name)):
        if metrics_name[i] in init_metrics:
            node_metrics[metrics_name[i]] = metrics_values[i]

def write_metrics(dst_path,node_id,node_type,node_name,node_metrics,source_file):
    with open(dst_path,"a+",encoding="utf-8") as f:
        f.write(str(node_id))
        f.write("\t")
        f.write(node_type)
        f.write("\t")
        f.write(node_name)
        f.write("\t")
        f.write(node_metrics)
        f.write("\t")
        f.write(source_file)
        f.write("\n")

def process_metrics(src_path,dst_path,jasome_indicators_path):
    #节点名与id之间的转换映射
    id_name_map = {}
    name_id_map = {}

    #初始化指标
    init_metrics = process_init_metrics(jasome_indicators_path)

    node_id = 0
    metrics = etree.parse(src_path)#解析xml

    #package
    package_list = metrics.xpath("/Project/Packages/Package")#所有package结点
    print("process metrics:\n")
    for p in tqdm(package_list):
       #print("_________checkpoint1_________")
        package_metrics = init_metrics.copy()
        package_name = p.xpath("./@name")[0]    #包名
        package_metrics_name = p.xpath("./Metrics/Metric/@name")    #包的所有指标名
        package_metrics_name = process_metrics_name("P",package_metrics_name)
        package_metrics_value = p.xpath("./Metrics/Metric/@value")  #包的所有指标值
        update_metrics(package_metrics,jasome_indicators_path,package_metrics_name,package_metrics_value)

        #class
        class_list = p.xpath("./Classes/Class")
        for c in class_list:
            #print("_________checkpoint2_________")
            class_metrics = package_metrics.copy()  #class指标
            class_name = package_name + "." + c.xpath("./@name")[0] #class名
            class_metrics_name = c.xpath("./Metrics/Metric/@name")    
            class_metrics_name = process_metrics_name("C",class_metrics_name)
            class_metrics_value = c.xpath("./Metrics/Metric/@value")  
            update_metrics(class_metrics,jasome_indicators_path,class_metrics_name,class_metrics_value)#更新class metrics
            class_sourceFile = c.xpath("./@sourceFile")[0]   #class源路径

            if class_name not in name_id_map:#如果class未被写入(考虑到多态)
                #写入class的指标
                write_metrics(dst_path,node_id,'C',class_name,arr_to_string(list(class_metrics.values())),class_sourceFile)
                node_id += 1
                #更新映射
                id_name_map[node_id] = class_name
                name_id_map[class_name] = node_id

            #method
            method_list = c.xpath("./Methods/Method")
            for m in method_list:
                #print("_________checkpoint3_________")
                method_metrics = class_metrics.copy()  #method指标
                method_name = m.xpath("./@name")[0]
                #函数名处理,只匹配函数名，其余不要
                method_name = class_name + "::" + re.findall(r' (\w+)\(',method_name)[0]    #没有考虑函数多态
                method_metrics_name = m.xpath("./Metrics/Metric/@name")    
                method_metrics_name = process_metrics_name("M",method_metrics_name)
                method_metrics_value = m.xpath("./Metrics/Metric/@value")  
                update_metrics(method_metrics,jasome_indicators_path,method_metrics_name,method_metrics_value)#更新method metrics

                if method_name not in name_id_map:#考虑存在多态
                    #写入method的指标
                    write_metrics(dst_path,node_id,'M',method_name,arr_to_string(list(method_metrics.values())),class_sourceFile)
                    node_id += 1
                    #更新映射
                    id_name_map[node_id] = method_name
                    name_id_map[method_name] = node_id   

def attribute_standard_scale(attribute):
    scaler = preprocessing.StandardScaler().fit(attribute)
    X_scaled = scaler.transform(attribute)
    return X_scaled

def get_node_id(metrics_path):
    node_id = []
    with open(metrics_path,"r") as f:
        for line in f.readlines():
            line = line.split("\t") #每行进行划分
            id_ = line[0]   
            node_id.append(int(id_))
    return node_id

def get_attribute(metrics_path):
    attribute = []
    with open(metrics_path,"r") as f:
        for line in f.readlines():
            line = line.split("\t") #每行进行划分
            #node_id = int(line[0])
            feature = list(map(eval,line[3].split(",")))#将字符串转为数字型
            attribute.append(feature)
    attribute = np.array(attribute)
    #attribute = attribute_standard_scale(attribute)
    return attribute

def get_class_id_index(metrics_path):
    class_id_index = []
    with open(metrics_path,"r") as f:
        for line in f.readlines():
            line = line.split("\t") #每行进行划分
            node_id = int(line[0])
            node_type = line[1]
            if node_type == 'C':
                class_id_index.append(node_id)
            
    class_id_index = np.array(class_id_index)
    return class_id_index

def get_class_feature(metrics_path):
    class_feature = []
    with open(metrics_path,"r") as f:
        for line in f.readlines():
            line = line.split("\t") #每行进行划分
            node_type = line[1]
            node_feature = list(map(eval,line[3].split(",")))
            if node_type == 'C':
                class_feature.append(node_feature)
            
    class_feature = np.array(class_feature)
    return class_feature

def get_method_id_index(metrics_path):
    method_id_index = []
    with open(metrics_path,"r") as f:
        for line in f.readlines():
            line = line.split("\t") #每行进行划分
            node_id = int(line[0])
            node_type = line[1]
            if node_type == 'M':
                method_id_index.append(node_id)
            
    method_id_index = np.array(method_id_index)
    return method_id_index

def get_method_feature(metrics_path):
    method_feature = []
    with open(metrics_path,"r") as f:
        for line in f.readlines():
            line = line.split("\t") #每行进行划分
            node_type = line[1]
            node_feature = list(map(eval,line[3].split(",")))
            if node_type == 'M':
                method_feature.append(node_feature)
            
    method_feature = np.array(method_feature)
    return method_feature

def get_X_index(smell_type,metrics_path):
    if smell_type == 'LM' or smell_type == 'FE':
        return get_method_id_index(metrics_path)
    elif smell_type == 'GC':
        return get_class_id_index(metrics_path)
    else:
        print("not found smell type, get feature error!")
        exit(0)



def main():
    project = 'flink-java'
    #============处理代码测试指标=============
    #代码指标源路径
    metrics_src_path = "./JasomeMetrics/" + project + "_jasome_metrics.xml"
    metrics_path = "./Metrics/" + project + "_metrics.txt"  #处理完xml，metrics的保存路径
    jasome_indicators_path = './JaSome_Indicators.txt'  #jasome指标说明路径
    #处理代码指标
    process_metrics(metrics_src_path,metrics_path,jasome_indicators_path)
    #print(get_node_id())


if __name__ == '__main__':
    main()
