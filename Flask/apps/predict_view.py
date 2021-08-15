from flask import request
from flask import jsonify, json
from flask import Blueprint

from SubwayModel.MysqlOS import SQLOS
from MakeChart import ChartApi
from apps import api, pred_api

predict_bp = Blueprint('predict_view', __name__, url_prefix='/pred')

@predict_bp.route('/hour_flow', methods=['POST', 'GET'])
def pred_in_out_hour_flow():
    param_str = request.get_data().decode('utf-8')
    param_dict = json.loads(param_str)

    date = param_dict['c_date']
    date = pred_api.time_map(date)

    hour_list = [str(i) for i in range(6, 22)]
    in_flow = pred_api.get_hour_flow(date, 'in')
    # out_flow = pred_api.get_hour_flow(date, 'out')

    return jsonify({'hour': hour_list, 'in_flow': in_flow})

@predict_bp.route('/day_info', methods=['POST', 'GET'])
def pred_day_info():
    param_str = request.get_data().decode('utf-8')
    param_dict = json.loads(param_str)

    date = param_dict['c_date']
    alg = int(param_dict.get('alg', 1))

    day_info = pred_api.get_day_flow_info(date, alg)

    return jsonify(day_info)

@predict_bp.route('/day_eval', methods=['POST', 'GET'])
def pred_day_eval():
    param_str = request.get_data().decode('utf-8')
    param_dict = json.loads(param_str)
    date = param_dict['c_date']

    date = pred_api.time_map(date)

    eval_value = SQLOS.get_eval_factor(date)
    weight = [0.016745, 0.249164, 0.247595, 0.276281, 0.210215]
    result =  100 * sum(list(map(lambda x, y: x * y, eval_value, weight)))

    return jsonify({'eval': int(result)}) 

@predict_bp.route('/section_flow', methods=['POST', 'GET'])
def pred_section_flow():
    param_str = request.get_data().decode('utf-8')
    param_dict = json.loads(param_str)
    date = param_dict['c_date']

    date = pred_api.time_map(date)
    
    section_flow = pred_api.get_section_flow(date, 'up')

    return jsonify(section_flow)

@predict_bp.route('/route_map', methods=['POST', 'GET'])
def pred_route_map_data():
    param_str = request.get_data().decode('utf-8')
    param_dict = json.loads(param_str)

    date = param_dict['c_date']
    graph_type = param_dict['graphtaggle']

    date = pred_api.time_map(date)
    
    if graph_type == 1:
        show_type = 'down' if param_dict['inout_s'] else 'up'
        flow_data = pred_api.get_section_flow(date, show_type)
    else:
        show_type = 'out' if param_dict['inout_s'] else 'in'
        flow_data = pred_api.get_sta_hour_flow(date, show_type)

    return jsonify(flow_data)

################Pyecharts
@predict_bp.route('/month/line', methods=['POST', 'GET'])
def pred_month_line():
    param_str = request.get_data().decode('utf-8')
    param_dict = json.loads(param_str)
    curr_date = param_dict['c_date']

    month = curr_date.split('-')[1].lstrip('0')
    month_dict = pred_api.get_curr_month_flow(month, **param_dict)
    line = ChartApi.pred_month_line(month_dict, int(curr_date.split('-')[1]))

    return line.dump_options_with_quotes()

@predict_bp.route('/week/line', methods=['POST', 'GET'])
def pred_week_line():
    param_str = request.get_data().decode('utf-8')
    param_dict = json.loads(param_str)
    
    curr_date = param_dict['c_date']
    alg = int(param_dict.get('alg', 0))

    week_dict = pred_api.get_curr_week_flow(curr_date, alg)
    line = ChartApi.pred_week_line(week_dict)

    return line.dump_options_with_quotes()

@predict_bp.route('/line/pie', methods=['POST', 'GET'])
def pred_line_pie():
    param_str = request.get_data().decode('utf-8')
    param_dict = json.loads(param_str)
    curr_date = param_dict['c_date']

    line, percent = pred_api.get_line_flow_percent(curr_date, api.sta_dict)
    pie = ChartApi.line_pie(line, percent)

    return pie.dump_options_with_quotes()

@predict_bp.route('/hour/line', methods=['POST', 'GET'])
def pred_hour_line():
    param_str = request.get_data().decode('utf-8')
    param_dict = json.loads(param_str)
    curr_date = param_dict['c_date']

    curr_date = pred_api.time_map(curr_date)

    hour_list = [str(i) for i in range(6, 22, 1)]
    in_flow = pred_api.get_hour_flow(curr_date, 'in')

    line = ChartApi.hour_line(hour_list, in_flow)

    return line.dump_options_with_quotes()

@predict_bp.route('/eval/radar', methods=['POST', 'GET'])
def pred_eval_radar():
    param_str = request.get_data().decode('utf-8')
    param_dict = json.loads(param_str)
    curr_date = param_dict['c_date']

    curr_date = pred_api.time_map(curr_date)

    eval_value = SQLOS.get_eval_factor(curr_date)
    radar = ChartApi.eval_radar(eval_value)

    return radar.dump_options_with_quotes()