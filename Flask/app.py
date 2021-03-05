from flask import Flask,Response,request
from flask import render_template
from flask import redirect, url_for, jsonify
from sys import path
import os
import json
import warnings
warnings.filterwarnings('ignore')
path.append('..')
path.append(os.path.abspath(os.path.dirname(__file__)).split('Flask')[0])
path.append(os.path.abspath(os.path.dirname(__file__)).split('Flask')[0] + 'PredictModel\\')
from DataAnalysis import DataApi
from MakeChart import ChartApi
from MysqlOS import SQLOS

app=Flask(__name__)
abs_path = os.path.abspath(os.path.dirname(__file__))
print(path)
print(abs_path)

#初始化站点名称 
station_name='Sta1'

api = DataApi()

#网页根目录
@app.route('/')
def root():                             
    return redirect(url_for('index'))

@app.route('/index', methods = ["POST", "GET"])
def index():
    return render_template('index.html')

@app.route('/predict')
def predict():
    return render_template('predict.html')

@app.route('/client')
def client():
    return render_template('client.html')

########需要调用的api
@app.route('/sta.json')
def get_sta_json():
    with open(abs_path + '/stations.json', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/link.json')
def get_link_json():
    with open(abs_path + '/links.json', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/other_info', methods = ['POST', 'GET'])
def other_info():
    current_date = request.get_data().decode('utf-8')[1:-1]
    month, day = current_date[:-3], current_date[-2:]

    weather = SQLOS.get_weather_info(current_date)
    is_hoilday = SQLOS.get_hoilday_info(current_date)
    day_flow = str(api.month_dict[month][day])

    info_dict = {
        'weather': weather[0][0], 
        'is_hoilday': ('是' if is_hoilday[0][0] == '1' else '否'),
        'day_flow': day_flow,
    }
    print(info_dict)

    return jsonify(info_dict)

#------------控制图表的展示----------------
@app.route('/history/day_flow/line', methods = ['POST', 'GET'])
def day_flow():
    current_date = request.get_data().decode('utf-8')[1:-1]
    month = current_date[:-3] 
    month_dict = api.month_dict
    day_dict = month_dict[month]
    day_line = ChartApi.day_line(month, day_dict)

    return day_line.dump_options_with_quotes()

@app.route('/history/curr_week_flow/line', methods = ['POST', 'GET'])
def curr_week_flow():
    current_date = request.get_data().decode('utf-8')[1:-1]
    curr_week_dict = api.get_curr_week_flow(current_date)
    curr_week_line = ChartApi.curr_week_line(curr_week_dict)

    return curr_week_line.dump_options_with_quotes()

# @app.route('/history/age/pie')
# def age_pie():
#     age, percent = api.age, api.percent
#     age_pie = ChartApi.age_pie(age, percent)
#     return age_pie.dump_options_with_quotes()

# @app.route('/history/month_flow/line')
# def month_flow_line():
#     month_line = ChartApi.month_line(api.month_dict)
#     return month_line.dump_options_with_quotes()

# @app.route('/history/week_flow/line')
# def week_flow_line():
#     week_line = ChartApi.week_line(api.week_dict)
#     return week_line.dump_options_with_quotes()

# @app.route('/history/station_flow/bar')
# def station_flow_bar():
#     global station_name
#     in_dict, out_dict = api.in_dict, api.out_dict
#     bar = ChartApi.station_bar(station_name, in_dict, out_dict)
#     return bar.dump_options_with_quotes()

if __name__ == '__main__':
    app.run(debug=False)