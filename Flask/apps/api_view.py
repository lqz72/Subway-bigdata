import os
import json
from flask import request
from flask import jsonify
from flask import Blueprint

from apps import api

api_bp = Blueprint('api_bp', __name__, url_prefix='/api')

abs_path = os.path.abspath(os.path.dirname(__file__)).split('apps')[0]

@api_bp.route('/sta/json')
def get_sta_json() -> json:
    with open(abs_path + 'json_data/stations.json', 'r', encoding='utf-8') as f:
        return f.read()

@api_bp.route('/link/json')
def get_link_json() -> json:
    with open(abs_path + '/json_data/links.json', 'r', encoding='utf-8') as f:
        return f.read()

@api_bp.route('/weather_info/<_type>', methods=['POST', 'GET'])
def weather_info(_type):
    """
    获取天气信息
    type: 类型 可选day或week
    """
    curr_date = request.get_data().decode('utf-8')

    if _type == 'day':
        weather = api.get_recent_weather(curr_date, 1)
    elif _type == 'week':  
        weather = api.get_recent_weather(curr_date)

    return jsonify(weather)


