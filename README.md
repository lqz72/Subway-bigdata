# Subway-bigdata
以地铁ACC(地铁自动售检票系统清分中心简称)系统的用户行程数据、站点
数据为基础，完成基于地铁出行行程大数据的分析建模和算法研究，实现对地铁
的线路级别以及站点级别的客流进行分析和预测。

#### 项目结构

##### 1. Flask前端框架

###### 1.1 templates 
放置html模板 模板引擎采用Jinja2 如需绘制图表 需引入jquery.min.js和echarts.min.js

###### 1.2 static 
放置css、js、image等静态文件 引入的方式统一采用url_for('static',filename='路径')

###### 1.3 app.py 
控制模板的跳转 处理前后端的数据交互

##### 2. PredictModel 后端 数据分析与模型建立

###### 2.1 csv_data
放置csv类型的原始数据

###### 2.2 DataSource.py 
提供数据分析所需的数据 使用方法参考注释

###### 2.3 MonthFlow.py -> PeakFlow.py
提供各项数据统计和图表接口 使用方法参考注释

###### 2.4 BoostModel.py
客流预测模型 采用xgboost机器学习集成算法 



#### 后端技术栈

开发语言采用python3

##### 1.web应用框架

使用flask轻量级web框架进行后台开发

##### 2.数据分析

主要技术：

1.数据分析  numpy、pandas

2.可视化 pyecharts

##### 3.数据预测

客流预测归结于时间序列预测的问题 

本项目采用机器学习进行预测

主要技术：

1.数据建模 sklearn

2.集成算法 xgboost

3.模型保存 joblib

##### 4.数据库

采用mysql8.0作为数据库

##### 5.项目部署

本项目部署在远程云服务器，可以实现外网访问以及网站的动态更新

主要技术：

###### 1.Flask

轻量级web应用框架

###### 2.Gunicorn 

高性能 WSGI 服务器  作为web应用程序与web服务器之间的接口

###### 3.Nginx 

高性能 Web 服务器 实现分流、转发、负载均衡