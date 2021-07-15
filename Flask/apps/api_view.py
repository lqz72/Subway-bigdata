import json
import os
import re
from flask import render_template
from flask import redirect, request
from flask import jsonify
from flask import Blueprint

from DataAnalysis import DataApi
from PredictResult import PredictApi
from MakeChart import ChartApi
from MysqlOS import SQLOS

api_bp = Blueprint('api_bp', __name__)

api = DataApi()
pred_api = PredictApi()

abs_path = os.path.abspath(os.path.dirname(__file__)).split('apps')[0]

@api_bp.route('/sta/json')
def get_sta_json() -> json:
    with open(abs_path + 'json_data/stations.json', 'r', encoding='utf-8') as f:
        return f.read()

@api_bp.route('/link/json')
def get_link_json() -> json:
    with open(abs_path + '/json_data/links.json', 'r', encoding='utf-8') as f:
        return f.read()



