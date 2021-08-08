import re
import json
import datetime
import random
import numpy as np
from flask import request, redirect
from flask import jsonify
from flask import Blueprint

from MakeChart import ChartApi
from apps import pred_api
from apps import api
 
station_bp = Blueprint('station_bp', __name__, url_prefix='/sta')

@station_bp.route('/search', methods=['POST', 'GET'])
def sta_search():
    if request.method == 'POST':
        inner_text = request.form.get('search')
        pattern = re.compile(r'\d+')
        sta_name = pattern.findall(inner_text)[0]
    return redirect('/station/Sta{}'.format(sta_name))

@station_bp.route('/thisday_info', methods=['POST', 'GET'])
def sta_thisday_info():
    param_str = request.get_data().decode('utf-8')
    param_dict = json.loads(param_str)
    
    station = param_dict['sta']
    date = param_dict['date']

    day_flow_info = api.get_sta_flow_info(date, station)

    info_dict = {
        'day_cmp': day_flow_info['day_cmp'],
        'month_cmp': day_flow_info['month_cmp'],
        'year_cmp': day_flow_info['year_cmp'],
        'am_peak_flow': day_flow_info['am_peak_flow'],
        'pm_peak_flow': day_flow_info['pm_peak_flow']
    }

    return jsonify(info_dict)

@station_bp.route('/curr_week_flow', methods=['POST', 'GET'])
def sta_curr_week_flow():
    param_str = request.get_data().decode('utf-8')
    param_dict = json.loads(param_str)

    station = param_dict['sta']
    date = param_dict['date']

    flow_dict = api.get_sta_curr_week_flow(date, station)

    return jsonify(flow_dict)

@station_bp.route('/curr_day_flow', methods=['POST', 'GET'])
def sta_curr_day_flow():
    param_str = request.get_data().decode('utf-8')
    param_dict = json.loads(param_str)

    station = param_dict['sta']
    date = param_dict['date']

    flow_dict = api.get_sta_curr_day_flow(date, station)

    return jsonify(flow_dict)

@station_bp.route('/curr_day_eval', methods=['POST', 'GET'])
def sta_curr_day_eval():
    param_str = request.get_data().decode('utf-8')
    param_dict = json.loads(param_str)

    station = param_dict['sta']
    date = param_dict['date']

    cur_date = datetime.datetime.strptime(date, '%Y-%m-%d')
    end_time = datetime.datetime.strptime('2020-07-16', '%Y-%m-%d')
    
    one_day = datetime.timedelta(days=1)

    index = 0
    score_list = []
    if cur_date > end_time:
        day_list = ['2020-07-17', '2020-07-18', '2020-07-19', '2020-07-20', 
                '2020-07-21', '2020-07-22', '2020-07-23']

        date = pred_api.time_map(date)
        index = day_list.index(date)

        for day in day_list:
            score_list.append(pred_api.get_pre_sta_score(day, station))
    else:
        score_list = [api.get_his_sta_score(date, station)]
        for i in range(6):
            cur_date += one_day
            date = cur_date.strftime('%Y-%m-%d')
            if cur_date > end_time:
                score_list.append(pred_api.get_pre_sta_score(date, station))
            else:
                score_list.append(api.get_his_sta_score(date, station))

    score_list = np.array(score_list)
    _range = np.max(score_list) - np.min(score_list)
    res = (score_list - np.min(score_list)) / _range

    return jsonify({'score': int(res[index] * 100)})

@station_bp.route('/curr_day/bicycle_num', methods=['POST', 'GET'])
def sta_curr_day_bicycle_num():
    param_str = request.get_data().decode('utf-8')
    param_dict = json.loads(param_str)

    station = param_dict['sta']
    date = param_dict['date']

    cur_date = datetime.datetime.strptime(date, '%Y-%m-%d')
    end_time = datetime.datetime.strptime('2020-07-16', '%Y-%m-%d')

    if cur_date > end_time:
        date = pred_api.time_map(date)
        res = pred_api.get_pre_bicycles_num(date, station)
    else:
        res = api.get_his_bicycles_num(date, station)

    hour_list = [str(i) for i in range(6, 22)]

    return jsonify((hour_list, res))

@station_bp.route('/curr_day/bus_interval', methods=['POST', 'GET'])
def sta_curr_day_bus_interval():
    param_str = request.get_data().decode('utf-8')
    param_dict = json.loads(param_str)

    station = param_dict['sta']
    date = param_dict['date']

    cur_date = datetime.datetime.strptime(date, '%Y-%m-%d')
    end_time = datetime.datetime.strptime('2020-07-16', '%Y-%m-%d')

    if cur_date > end_time:
        date = pred_api.time_map(date)
        res = pred_api.get_pre_bus_interval(date, station)
    else:
        res = api.get_his_bus_interval(date, station)

    hour_list = [str(i) for i in range(6, 22)]

    return jsonify((hour_list, res))

@station_bp.route('/curr_day/adver_ratio', methods=['POST', 'GET'])
def sta_curr_day_adver_ratio():
    param_str = request.get_data().decode('utf-8')
    param_dict = json.loads(param_str)

    station = param_dict['sta']
    date = param_dict['date']

    cur_date = datetime.datetime.strptime(date, '%Y-%m-%d')
    end_time = datetime.datetime.strptime('2020-07-16', '%Y-%m-%d')

    if cur_date > end_time:
        day_delta = end_time - cur_date
        after_date = cur_date - day_delta
        date = after_date.strftime('%Y-%m-%d')
        res = api.get_his_adver_ratio(date, station)
    else:
        res = api.get_his_adver_ratio(date, station)

    ad_list = ["数码", "运动", "男装", "美妆", "母婴", "女装"]

    return jsonify((ad_list, res))

@station_bp.route('/curr_day/run_info', methods=['POST', 'GET'])
def sta_curr_day_run_info():
    param_str = request.get_data().decode('utf-8')
    param_dict = json.loads(param_str)

    station = param_dict['sta']
    date = param_dict['date']
    hour = param_dict.get('hour', 9)

    cur_date = datetime.datetime.strptime(date, '%Y-%m-%d')
    end_time = datetime.datetime.strptime('2020-07-16', '%Y-%m-%d')

    if cur_date > end_time:
        date = pred_api.time_map(date)
        res = pred_api.get_pre_subway_run(date, station, hour)
    else:
        res = api.get_his_subway_run(date, station, hour)

    temp, xaxis, yaxis = res[0], res[1], res[2]
    axis_pair = [(xaxis, yaxis)]

    while 0 <= xaxis[0] + temp <= 60:

        xaxis = list(map(lambda x: x + temp, xaxis)) 

        x_axis, y_axis = [], []
        for i in range(len(xaxis)):
            if 0 <= xaxis[i] <= 60:
                x_axis.append(xaxis[i])
                y_axis.append(yaxis[i])

        axis_pair.append((x_axis, y_axis))

    yaxis_label = api.get_line_sta_list(station)

    return jsonify((axis_pair, yaxis_label))

@station_bp.route('/age/pie', methods=['POST', 'GET'])
def sta_age_pie():
    param_str = request.get_data().decode('utf-8')
    param_dict = json.loads(param_str)

    station = param_dict['sta']
    date = param_dict['date']

    age, percent = api.get_sta_age_structure(date, station)
    age_pie = ChartApi.sta_age_pie(age, percent)

    return age_pie.dump_options_with_quotes()

@station_bp.route('/schedule/line', methods=['POST', 'GET'])
def sta_schedule_line():
    param_str = request.get_data().decode('utf-8')
    param_dict = json.loads(param_str)

    station = param_dict['sta']
    date = param_dict['date']

    hour_list = [str(i) for i in range(6,22,3)]

    cur_date = datetime.datetime.strptime(date, '%Y-%m-%d')
    base_time = datetime.datetime.strptime('2020-07-16', '%Y-%m-%d')

    if cur_date > base_time:
        worker = pred_api.get_pre_personnel_dispatch(date, 'all', station)
    else:
        worker = api.get_his_personnel_dispatch(date, station)
 
    worker = [str(i) for i in worker.values()]

    line = ChartApi.sta_schedule_line(hour_list, worker)

    return line.dump_options_with_quotes()