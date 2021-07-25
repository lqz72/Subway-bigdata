import re
import json
import datetime
import random
from flask import request, redirect
from flask import jsonify
from flask import Blueprint

from MakeChart import ChartApi
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