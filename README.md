# CodeSmell
基于图表示学习的代码异味检测方法的论文源码
## 目标
利用图神经网络对 `特征依赖`,`上帝类`,`长方法`三种代码异味进行检测。  
## 主要工作
* 提出了一个基于图表示学习的代码异味检测框架CSDGR，该框架融合了代码度量信息和结构语义信息进行异味预测。  
* 框架采用两类无监督的图表示学习方法将代码节点表示到低维空间中，以便后续的分类任务，CSDGR具有良好的通用性和可扩展性。  
* 我们在多个开源项目进行实验分析，通过实验表明CSDGR的有效性。

## 源码简介
* [Srcml](https://www.srcml.org/) ：获取代码的抽象语法树
* [JaSome](https://github.com/rodhilton/jasome) : 获取代码的度量指标
* [ProcessDependency](./CSDGR/ProcessDependency.py) : 解决代码的依赖问题
* [ProcessLabel](./CSDGR/ProcessLabel.py) : 生成节点标签
* [CSDGR](/CSDGR/CSDGR.py) : 模型的主函数
* [GraphRepresentation](./CSDGR/GraphRepresentation.py) : 训练节点的图结构和属性的嵌入表示
* [Metrics](./CSDGR/Model.py) : 模型评估
