
import itertools
from lxml import etree

'''
------------------------class-file dependency---------------------
'''
#读取metrics文件，获得源文件与class的映射
def class_depend_file_read(metrics_path):
    sourcefile_class = {}
    with open(metrics_path, "r") as f:
        for line in f.readlines():
            line = line.strip('\n').split("\t")  #去掉每行换行符并进行切分
            #node_id = line[0]   #节点id
            node_type = line[1] #节点类型
            node_name = line[2]
            source_file = line[4]   #节点源文件
            
            if node_type == 'C':    #如果节点类型为class
                if source_file not in sourcefile_class:
                    sourcefile_class[source_file] = []
                sourcefile_class[source_file].append(node_name)
    return sourcefile_class #{file1:[class1,class2,...],...}

#类从属于一个Java文件
def class_depend_file(metrics_path):
    class_file_dependency = []

    sourcefile_class = class_depend_file_read(metrics_path)    
    common_file_class = list(sourcefile_class.values())
    for k in common_file_class: #如果一个java文件下有多个类，则class两两组合
        if len(k) > 1:
            t = list(itertools.permutations(k, 2))
            for v in t:
                class_file_dependency.append([v[0],v[1]])
    
    return class_file_dependency


'''
------------------class extend superclass dependency-----------------
'''
#将import的xml实例列表转换为当前import路径和import class 映射
#返回值：
#current_import <list> 保存import字符串列表
#import_index_map ,dict> 实现import的类与current_import的index的映射，方便查找
def import_transform(import_list):
    current_import = []
    import_index_map = {}
    index = 0
    for i in import_list:
        import_name = i.xpath("./name//text()")
        import_str = ''.join(import_name)
        current_import.append(import_str)

        import_class = import_name[-1]
        import_index_map[import_class] = index
        index += 1
    return current_import,import_index_map

#查找class是否在import中，若不在返回当前包的类路径名,否则返回全路径类名
def find_import(class_name,current_package,current_import,import_index_map):
    if import_index_map.get(class_name) is None:#不存在
        return current_package + '.' + class_name
    else:
        return current_import[import_index_map.get(class_name)]

#类之间的继承关系
def class_depend_superclass(ast_path):
    class_superclass_dependency = []

    astTree = etree.parse(ast_path)   #解析ast
    units = astTree.xpath("//unit")
    for unit in units:
        #package
        current_package = ''.join(unit.xpath("./package/name//text()")) #当前package名
        #import
        import_list = unit.xpath("./import")    #xml import实例列表
        current_import,import_index_map = import_transform(import_list)     #import转换
        #class
        class_list = unit.xpath(".//class")
        for c in class_list:
            try:
                class_name = current_package + '.' + c.xpath("./name//text()")[0]
                #是否有继承
                try:
                    super_class = c.xpath("./super_list//super//text()")[0]
                    #父类是否为import的类
                    super_class_name = find_import(super_class,current_package,current_import,import_index_map)
                    class_superclass_dependency.append([class_name,super_class_name])
                except:
                    pass
            except:
                pass
    return class_superclass_dependency
    
'''
------------------------method class dependency-----------------------

'''
#class中的包含的method 
def method_depend_class(metrics_path):
    method_class_dependency = []

    class_name = ''
    method_name = ''

    #由于metrics写入时按照class-method顺序写入，故直接进行依赖处理
    with open(metrics_path, "r") as f:
        for line in f.readlines():
            line = line.strip('\n').split("\t")  #去掉每行换行符并进行切分
            #node_id = line[0]
            node_type = line[1]
            node_name = line[2]
            
            if node_type == 'C':    #如果节点类型为class
                class_name = node_name
            else:   #如果节点类型为method
                method_name = node_name
                method_class_dependency.append([class_name,method_name])
                method_class_dependency.append([method_name,class_name])
    return method_class_dependency
            
'''
-----------------------method call dependency--------------------------
'''
def decl_transform(function):#变量声明映射
    var_decl_map = {}
    for decl in function.xpath("./block//decl"):#函数下的所有声明变量语句
        try:
            var_type = decl.xpath("./type/name//text()")[0]#变量类型
            var_name = decl.xpath("./name//text()")[0]#变量名
            var_decl_map[var_name] = var_type #变量名-变量类型
        except:
            continue
    return var_decl_map

def find_decl(var_name,var_decl_map):#查找是否存在变量声明
    if var_decl_map.get(var_name) is None:
        return var_name
    else:#存在变量声明
        return var_decl_map[var_name]#返回所属类型
    


#method中的函数调用，包含：1.函数的参数引用的class;2.函数的调用
def method_depend_call(ast_path):
    method_call_dependency = []

    astTree = etree.parse(ast_path)   #解析ast
    units = astTree.xpath("//unit")
    for unit in units:
        current_package = ''.join(unit.xpath("./package/name//text()"))
        
        import_list = unit.xpath("./import")
        current_import,import_index_map = import_transform(import_list) 
            
        class_list = unit.xpath(".//class")
        for c in class_list:
            try:
                class_name = current_package + '.' + c.xpath("./name//text()")[0]#类名
                
                for f in c.xpath("./block//function"):
                    function_name = class_name + "::" + f.xpath("./name//text()")[0]
                    #处理函数参数依赖 function-class
                    for parameter_type in f.xpath(".//parameter//type/name//text()"):
                        para_name = find_import(parameter_type,current_package,current_import,import_index_map)#查找参数的类是否为import
                        method_call_dependency.append([function_name,para_name])
                    #处理函数调用依赖 function-function
                    var_decl_map = decl_transform(f)#建立变量名和类的映射
                    for f_call in f.xpath(".//call"):
                        call_ = f_call.xpath("./name//text()")
                        if len(call_) == 1:#位于同一个类中
                            call_name = class_name + "::" + call_[0]
                            
                        if len(call_) == 2:#模板类
                            call_class = find_decl(call_[0],var_decl_map)
                            call_name = find_import(call_class,current_package,current_import,import_index_map)
                        
                        if len(call_) >= 2:#调用其他
                            if call_[0] == 'this':#位于同一个类中
                                call_name = class_name + "::" + call_[2]
                            else:#调用其他类
                                call_class = find_decl(call_[0],var_decl_map)
                                #查询类是否在import中
                                call_class_name = find_import(call_class,current_package,current_import,import_index_map)
                                call_name = call_class_name + "::" + call_[2]
            
                        method_call_dependency.append([function_name,call_name])
            except:
                pass
    return method_call_dependency

'''
-----------------------transform name to id -------------------
'''
def build_name_id_map(metrics_path):
    name_id_map = {}
    with open(metrics_path, "r") as f:
        for line in f.readlines():
            line = line.strip('\n').split("\t")
            node_id = line[0]   #节点id
            node_name = line[2]
            name_id_map[node_name] = node_id
    return name_id_map

def transform_name_to_id(name_dependency,name_id_map):
    id_dependency = []
    for d in name_dependency:
        if d[0] in name_id_map and d[1] in name_id_map:
            id_dependency.append((int(name_id_map[d[0]]),int(name_id_map[d[1]])))
    return id_dependency

'''
-------------------process dependency --------------------------------
'''
def process_dependency(ast_path,metrics_path):
    #class-file dependency
    class_file_dependency = class_depend_file(metrics_path)
    #class extend superclass dependency
    class_superclass_dependency = class_depend_superclass(ast_path)
    #method class dependency
    method_class_dependency = method_depend_class(metrics_path)
    #method call dependency
    method_call_dependency = method_depend_call(ast_path)
    #all name dependency
    name_dependency = class_file_dependency + class_superclass_dependency + method_class_dependency + method_call_dependency

    #构建节点名与节点id的映射
    name_id_map = build_name_id_map(metrics_path)
    id_dependency = transform_name_to_id(name_dependency,name_id_map)
    
    return id_dependency




def main():
    project = 'flink-java'
    ast_path = "./SrcmlAst" + project + "_ast.xml"
    metrics_path = "./Metrics/" + project + "_metrics.txt"
    process_dependency(ast_path,metrics_path)

if __name__ == "__main__":
    main()