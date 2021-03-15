from flask import Flask,Response,request
from flask import render_template
from flask import redirect, url_for, jsonify
from flask.json import JSONEncoder
from sys import path
import os
import json
import warnings
warnings.filterwarnings('ignore')
path.append('..')
path.append(os.path.abspath(os.path.dirname(__file__)).split('Flask')[0])
path.append(os.path.abspath(os.path.dirname(__file__)).split('Flask')[0] + 'PredictModel\\')

import numpy as np
from DataAnalysis import DataApi
from MakeChart import ChartApi
from MysqlOS import SQLOS

app=Flask(__name__)
api=DataApi()

abs_path = os.path.abspath(os.path.dirname(__file__))
station_name='Sta1'

#数据格式转换类
class NpEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super().default(obj)

#------------模板渲染------------
@app.route('/')
def root():                             
    return redirect(url_for('index'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/predict')
def predict():
    return render_template('predict.html')

@app.route('/client')
def client():
    return render_template('client.html')

@app.route('/selfcenter')
def selfcenter():
    return render_template('selfcenter.html')

@app.route('/userinf')
def userinf():
    return render_template('userinf.html')

#------------需要调用的api------------
@app.route('/sta/json')
def get_sta_json() -> json:
    with open(abs_path + '/stations.json', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/link/json')
def get_link_json() -> json:
    with open(abs_path + '/links.json', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/user/json')
def get_user_json() -> json:
    """返回所有用户的信息
    """
    with open(abs_path + '/user_info.json', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/thisday_info', methods = ['POST', 'GET'])
def thisday_info() -> json:
    """返回指定日期天气、节假日、客流信息
    """
    current_date = request.get_data().decode('utf-8')
    month, day = current_date[:-3], current_date[-2:]

    weather = SQLOS.get_weather_info(current_date)
    is_hoilday = SQLOS.get_hoilday_info(current_date)
    day_flow = api.month_dict[month][day]

    info_dict = {
        'weather': weather[0][0], 
        'is_hoilday': ('是' if is_hoilday[0][0] == '1' else '否'),
        'day_flow': day_flow,
    }

    return jsonify(info_dict)

@app.route('/sta_rank', methods=['POST', 'GET'])
def sta_rank() -> json:
    """返回站点客流排行
    """
    current_date = request.get_data().decode('utf-8')
    sta_rank_list = api.get_top_sta(current_date)

    return jsonify(sta_rank_list)

@app.route('/user_info', methods=['POST', 'GET'])
def user_info() -> json:
    """返回指定用户的个人信息
    """
    user_id = request.get_data().decode('utf-8')
    user_info = api.get_user_info(user_id)

    return jsonify(user_info)

@app.route('/admin_info', methods=['POST', 'GET'])
def admin_info() -> json:
    """返回管理员信息
    """
    user_list = SQLOS.get_admin_info()

    return jsonify(user_list)

@app.route('/in_hour_flow', methods = ['POST', 'GET'])
def in_hour_flow() -> json:
    """返回当前日期各站点6点-9点的进站客流量
    """
    current_date = request.get_data().decode('utf-8')
    in_hour_dict = api.get_in_hour_flow(current_date)

    return jsonify(in_hour_dict)

@app.route('/out_hour_flow', methods = ['POST', 'GET'])
def out_hour_flow() -> json:
    """返回当前日期各站点6点-9点的出站客流量
    """
    current_date = request.get_data().decode('utf-8')
    out_hour_dict = api.get_out_hour_flow(current_date)
    
    return jsonify(out_hour_dict)

#------------控制图表的展示------------
@app.route('/history/day_flow/line', methods = ['POST', 'GET'])
def day_flow():
    current_date = request.get_data().decode('utf-8')
    month = current_date[:-3] 
    month_dict = api.month_dict
    day_dict = month_dict[month]
    day_line = ChartApi.day_line(month, day_dict)

    return day_line.dump_options_with_quotes()

@app.route('/history/curr_week_flow/line', methods = ['POST', 'GET'])
def curr_week_flow():
    current_date = request.get_data().decode('utf-8')
    curr_week_dict = api.get_curr_week_flow(current_date)
    curr_week_line = ChartApi.curr_week_line(curr_week_dict)

    return curr_week_line.dump_options_with_quotes()

@app.route('/history/age/pie', methods = ['POST', 'GET'])
def age_pie():
    age, percent = api.age, api.percent
    age_pie = ChartApi.age_pie(age, percent)
    return age_pie.dump_options_with_quotes()

@app.route('/history/age/bar', methods = ['POST', 'GET'])
def age_bar():
    age, percent = api.age, api.percent
    age_bar = ChartApi.age_bar(age, percent)
    return age_bar.dump_options_with_quotes()

@app.route('/history/user_flow/line', methods = ['POST', 'GET'])
def user_flow_line():
    user_id = request.get_data().decode('utf-8')

    if user_id == '' or user_id == None:
        user_id = 'd4ec5a712f2b24ce226970a8d315dfce'

    month_dict = api.get_user_month_flow(user_id)
    flow_line = ChartApi.user_month_line(month_dict)

    return flow_line.dump_options_with_quotes()

@app.route('/history/line/pie', methods=['POST', 'GET'])
def line_pie():
    current_date = request.get_data().decode('utf-8')
    line, percent = api.get_line_flow_percent(current_date)
    pie = ChartApi.line_pie(line, percent)

    return pie.dump_options_with_quotes()

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
    app.json_encoder = NpEncoder
    app.run(debug=True)

