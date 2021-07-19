from flask import request
from flask import jsonify, json
from flask import Blueprint

from MakeChart import ChartApi
from MysqlOS import SQLOS
from apps import api

history_bp = Blueprint('history_bp', __name__, url_prefix='/history')

@history_bp.route('/thisday_info', methods=['POST', 'GET'])
def thisday_info() -> json:
    """返回指定日期天气、节假日、客流信息
    """
    curr_date = request.get_data().decode('utf-8')
    month, day = curr_date[:-3], curr_date[-2:]

    weather = SQLOS.get_weather_info(curr_date)
    is_hoilday = SQLOS.get_hoilday_info(curr_date)
    day_flow = api.month_dict[month][day]
    day_flow_info = api.get_day_flow_info(curr_date)

    info_dict = {
        'weather': weather[0][0],
        'is_hoilday': ('是' if is_hoilday[0][0] == '1' else '否'),
        'day_flow': int(day_flow),
        'day_cmp': day_flow_info['day_cmp'],
        'month_cmp': day_flow_info['month_cmp'],
        'year_cmp': day_flow_info['year_cmp'],
        'am_peak_flow': day_flow_info['am_peak_flow'],
        'pm_peak_flow': day_flow_info['pm_peak_flow']
    }

    return jsonify(info_dict)

@history_bp.route('/sta_rank', methods=['POST', 'GET'])
def sta_rank() -> json:
    """返回站点客流排行
    """
    curr_date = request.get_data().decode('utf-8')
    sta_rank_list = api.get_top_sta(curr_date)

    return jsonify(sta_rank_list)

@history_bp.route('/in_hour_flow', methods=['POST', 'GET'])
def in_hour_flow() -> json:
    """返回当前日期各站点6点-9点的进站客流量
    """
    curr_date = request.get_data().decode('utf-8')
    in_hour_dict = api.get_in_hour_flow(curr_date)

    return jsonify(in_hour_dict)

@history_bp.route('/out_hour_flow', methods=['POST', 'GET'])
def out_hour_flow() -> json:
    """返回当前日期各站点6点-9点的出站客流量
    """
    curr_date = request.get_data().decode('utf-8')
    out_hour_dict = api.get_out_hour_flow(curr_date)

    return jsonify(out_hour_dict)

@history_bp.route('/split_flow/<int:line>', methods=['POST', 'GET'])
def split_flow(line) -> json:
    """返回地铁断面客流
    """
    curr_date = request.get_data().decode('utf-8')
    split_flow = api.get_line_split_flow(curr_date, '%s号线' % line)

    return jsonify(split_flow)

@history_bp.route('/od_flow', methods=['POST', 'GET'])
def od_flow() -> json:
    """返回OD客流
    """
    curr_date = request.get_data().decode('utf-8')
    od_flow = api.get_od_flow(curr_date)

    return jsonify(od_flow)

@history_bp.route('/area/inout_flow', methods=['POST', 'GET'])
def inout_flow() -> json:
    """返回区域点入点出客流
    """
    curr_date = request.get_data().decode('utf-8')
    sta_list, in_flow, out_flow = api.get_area_in_out_flow(curr_date, '住宅区')

    return jsonify(sta_list, in_flow, out_flow)

#################Pyecharts
@history_bp.route('/day_flow/line', methods=['POST', 'GET'])
def day_flow():
    current_date = request.get_data().decode('utf-8')
    month = current_date[:-3]
    month_dict = api.month_dict
    day_dict = month_dict[month]
    day_line = ChartApi.day_line(month, day_dict)

    return day_line.dump_options_with_quotes()

@history_bp.route('/curr_week_flow/line', methods=['POST', 'GET'])
def curr_week_flow():
    current_date = request.get_data().decode('utf-8')
    curr_week_dict = api.get_curr_week_flow(current_date)
    curr_week_line = ChartApi.curr_week_line(curr_week_dict)

    return curr_week_line.dump_options_with_quotes()

@history_bp.route('/age/pie', methods=['POST', 'GET'])
def age_pie():
    age, percent = api.age, api.percent
    age_pie = ChartApi.age_pie(age, percent)
    return age_pie.dump_options_with_quotes()

@history_bp.route('/age/bar', methods=['POST', 'GET'])
def age_bar():
    age, percent = api.age, api.percent
    age_bar = ChartApi.age_bar(age, percent)
    return age_bar.dump_options_with_quotes()

@history_bp.route('/user_flow/line', methods=['POST', 'GET'])
def user_flow_line():
    user_id = request.get_data().decode('utf-8')

    if user_id == '' or user_id is None:
        user_id = 'd4ec5a712f2b24ce226970a8d315dfce'

    month_dict = api.get_user_month_flow(user_id)
    flow_line = ChartApi.user_month_line(month_dict)

    return flow_line.dump_options_with_quotes()

@history_bp.route('/line/pie', methods=['POST', 'GET'])
def line_pie():
    current_date = request.get_data().decode('utf-8')
    line, percent = api.get_line_flow_percent(current_date)
    pie = ChartApi.line_pie(line, percent)

    return pie.dump_options_with_quotes()