import random
from flask import render_template
from apps.api_view import *

station_bp = Blueprint('station_bp', __name__)

@station_bp.route('/station/<staname>', methods=['GET', 'POST'])
def station(staname):
    sta_info = DataApi.get_station_info(staname)
    return render_template('sta.html', staname=staname, sta_info=sta_info)

@api_bp.route('/sta/search', methods=['POST', 'GET'])
def sta_search():
    if request.method == 'POST':
        inner_text = request.form.get('search')
        pattern = re.compile(r'\d+')
        staname = pattern.findall(inner_text)[0]
    return redirect('/station/Sta{}'.format(staname))

@api_bp.route('/sta/thisday_info', methods=['POST', 'GET'])
def sta_thisday_info():
    param_str = request.get_data().decode('utf-8')
    param_dict = json.loads(param_str)

    station = param_dict['sta']
    date = param_dict['date']

    day_flow_info = api.get_sta_flow_info(station, date)

    info_dict = {
        'day_cmp': day_flow_info['day_cmp'],
        'month_cmp': day_flow_info['month_cmp'],
        'year_cmp': day_flow_info['year_cmp'],
        'am_peak_flow': day_flow_info['am_peak_flow'],
        'pm_peak_flow': day_flow_info['pm_peak_flow']
    }

    return jsonify(info_dict)

@api_bp.route('/sta/curr_week_flow', methods=['POST', 'GET'])
def sta_curr_week_flow():
    param_str = request.get_data().decode('utf-8')
    param_dict = json.loads(param_str)

    station = param_dict['sta']
    date = param_dict['date']

    flow_dict = api.get_sta_curr_week_flow(date, station)

    return jsonify(flow_dict)

@api_bp.route('/sta/curr_day_flow', methods=['POST', 'GET'])
def sta_curr_day_flow():
    param_str = request.get_data().decode('utf-8')
    param_dict = json.loads(param_str)

    station = param_dict['sta']
    date = param_dict['date']

    flow_dict = api.get_sta_curr_day_flow(date, station)

    return jsonify(flow_dict)

@station_bp.route('/sta/age/pie', methods = ['POST', 'GET'])
def sta_age_pie():
    param_str = request.get_data().decode('utf-8')
    param_dict = json.loads(param_str)

    station = param_dict['sta']
    date = param_dict['date']

    age, percent = api.get_sta_age_structure(date, station)
    age_pie = ChartApi.sta_age_pie(age, percent)

    return age_pie.dump_options_with_quotes()

@station_bp.route('/sta/schedule/line', methods = ['POST', 'GET'])
def sta_schedule_line():
    param_str = request.get_data().decode('utf-8')
    param_dict = json.loads(param_str)

    station = param_dict['sta']
    date = param_dict['date']

    hour_list = [str(i) for i in range(6,22,3)]
    volunteer = [random.randint(-20, 40)  for i in range(6, 22,3) if i != 0]
    worker = [str(i - abs(i) / i * random.randint(-10, 15)) for i in volunteer]

    volunteer = list(map(lambda x: str(x), volunteer))

    line = ChartApi.sta_schedule_line(hour_list, volunteer, worker)

    return line.dump_options_with_quotes()