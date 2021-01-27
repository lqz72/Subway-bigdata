# Subway-bigdata
以地铁ACC(地铁自动售检票系统清分中心简称)系统的用户行程数据、站点
数据为基础，完成基于地铁出行行程大数据的分析建模和算法研究，实现对地铁
的线路级别以及站点级别的客流进行分析和预测。

#### 项目结构

##### 1. Flask前端框架

templates 放置html模板 echarts已经成功下载 直接按照文档使用

static 放置css、js、图像等静态文件

app.py 控制网页的运转  处理前后端的数据交互

##### 2. PredictModel 后端 数据分析与模型建立

csv_data放置csv类型的原始数据

 DataSource.py 提供数据分析所需的数据 使用方法可参考其他已完成的分析



