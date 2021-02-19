from flask import Flask,Response,request
from flask import render_template
from flask import redirect
from sys import path
import os
import json
import warnings
warnings.filterwarnings('ignore')
path.append('..')
path.append(os.path.abspath(os.path.dirname(__file__)).split('Flask')[0])
path.append(os.path.abspath(os.path.dirname(__file__)).split('Flask')[0] + 'PredictModel\\')
from PredictModel import DataSource
from PredictModel import PeakFlow
from PredictModel import MonthFlow, WeekdayFlow, AgeStructure, StationFlow
app=Flask(__name__)
abs_path = os.path.abspath(os.path.dirname(__file__))
print(path)
print(abs_path)
#初始化站点名称 
station_name="Sta1"

#网页根目录
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/echarts')
def echarts():
    return render_template('test.html')

########echarts图表需要调用的api
@app.route('/sta.json')
def get_sta_json():
    with open(abs_path + '/stations.json', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/link.json')
def get_link_json():
    with open(abs_path + '/links.json', 'r', encoding='utf-8') as f:
        return f.read()

########控制模板的跳转和前后端的数据交互
@app.route('/history/age')
def age():
    return render_template('age.html')

@app.route('/history/month_flow')
def month_flow():
    return render_template('wholemonth.html')

@app.route('/history/week_flow')
def week_flow():
    return render_template('week.html')

@app.route('/history/station_flow', methods = ['GET', 'POST'])
def station_flow():
    global station_name
    if request.method == "POST":
        station_name = request.form.get("station_select")
    station_list = DataSource.station_list
    return render_template('station.html', station_list=station_list)

@app.route('/history/dayhigh', methods = ['GET', 'POST'])
def dayhigh():
    # in_am, in_pm = PeakFlow.in_am, PeakFlow.in_pm
    # out_am, out_pm = PeakFlow.out_am, PeakFlow.out_pm
    # return render_template('dayhigh.html', in_am=in_am, in_pm=in_pm,
    #     out_am=out_am, out_pm=out_pm)
    return render_template('dayhigh.html')

#------------控制图表的展示----------------
@app.route('/history/age/pie')
def age_pie():
    age, percent = AgeStructure.age, AgeStructure.percent
    age_pie = AgeStructure.age_pie(age, percent)
    return age_pie.dump_options_with_quotes()

@app.route('/history/month_flow/line')
def month_flow_line():
    month_line = MonthFlow.month_line(MonthFlow.month_dict)
    return month_line.dump_options_with_quotes()

@app.route('/history/week_flow/line')
def week_flow_line():
    week_line = WeekdayFlow.week_line(WeekdayFlow.week_dict)
    return week_line.dump_options_with_quotes()

@app.route('/history/station_flow/bar')
def station_flow_bar():
    global station_name
    in_dict, out_dict = StationFlow.in_dict, StationFlow.out_dict
    bar = StationFlow.station_bar(station_name, in_dict, out_dict)
    return bar.dump_options_with_quotes()

if __name__ == '__main__':
    app.debug = True # 设置调试模式，生产模式的时候要关掉debug
    app.run()