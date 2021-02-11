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




