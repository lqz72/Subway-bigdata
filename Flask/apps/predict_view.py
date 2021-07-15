from apps.api_view import *

predict_bp = Blueprint('predict_view', __name__)

@predict_bp.route('/predict')
def predict():
    return render_template('predict.html')

@predict_bp.route('/pred/hour_flow', methods=['POST', 'GET'])
def pred_out_hour_flow():
    param_str = request.get_data().decode('utf-8')
    param_dict = json.loads(param_str)

    date = param_dict['c_date']
    type_ = param_dict['inout_s']
    flow_dict = pred_api.get_sta_hour_flow(date, type_)

    return jsonify(flow_dict)

@predict_bp.route('/pred/day/info', methods=['POST', 'GET'])
def pred_day_info():
    param_str = request.get_data().decode('utf-8')
    param_dict = json.loads(param_str)

    date = param_dict['c_date']
    alg = int(param_dict.get('alg', 1))

    day_info = pred_api.get_day_flow_info(date, alg)

    return jsonify(day_info)

@predict_bp.route('/weather_info', methods=['POST', 'GET'])
def weather_info():
    """获取近7天的天气信息
    """
    curr_date = request.get_data().decode('utf-8')
    curr_weather = api.get_recent_weather(curr_date)

    return jsonify(curr_weather)

################Pyecharts
@predict_bp.route('/pred/month/line', methods=['POST', 'GET'])
def pred_month_line():
    param_str = request.get_data().decode('utf-8')
    param_dict = json.loads(param_str)
    curr_date = param_dict['c_date']

    print(param_dict)
    month = curr_date.split('-')[1].lstrip('0')
    month_dict = pred_api.get_curr_month_flow(month, **param_dict)
    line = ChartApi.pred_month_line(month_dict, int(curr_date.split('-')[1]))

    return line.dump_options_with_quotes()

@predict_bp.route('/pred/week/line', methods=['POST', 'GET'])
def pred_week_line():
    param_str = request.get_data().decode('utf-8')
    param_dict = json.loads(param_str)
    curr_date = param_dict['c_date']
    alg = int(param_dict['alg'])

    week_dict = pred_api.get_curr_week_flow(curr_date, alg)
    line = ChartApi.pred_week_line(week_dict)

    return line.dump_options_with_quotes()

@predict_bp.route('/pred/line/pie', methods=['POST', 'GET'])
def pred_line_pie():
    param_str = request.get_data().decode('utf-8')
    param_dict = json.loads(param_str)
    curr_date = param_dict['c_date']

    line, percent = pred_api.get_line_flow_percent(curr_date, api.sta_dict)
    pie = ChartApi.line_pie(line, percent)

    return pie.dump_options_with_quotes()

@predict_bp.route('/pred/hour/line', methods=['POST', 'GET'])
def pred_hour_line():
    param_str = request.get_data().decode('utf-8')
    param_dict = json.loads(param_str)
    curr_date = param_dict['c_date']

    hour_list = [str(i) for i in range(6, 22, 1)]
    in_flow = pred_api.get_hour_flow(curr_date, 'in')

    line = ChartApi.hour_line(hour_list, in_flow)

    return line.dump_options_with_quotes()

@predict_bp.route('/pred/eval/radar', methods=['POST', 'GET'])
def pred_eval_radar():
    param_str = request.get_data().decode('utf-8')
    param_dict = json.loads(param_str)
    curr_date = param_dict['c_date']

    radar = ChartApi.eval_radar()

    return radar.dump_options_with_quotes()