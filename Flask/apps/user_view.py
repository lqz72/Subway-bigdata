import json
from flask import request
from flask import jsonify
from flask import Blueprint

from apps import api
user_bp = Blueprint('user_bp', __name__, url_prefix='/user')

@user_bp.route('/info', methods=['POST', 'GET'])
def user_info() -> json:
    """返回指定用户的个人信息
    """
    user_id = request.get_data().decode('utf-8')
    user_info = api.get_user_info(user_id)

    return jsonify(user_info)

@user_bp.route('/users_info/<int:page>', methods=['POST', 'GET'])
def users_info(page) -> json:
    """根据索引返回批量用户信息
    """
    users_info_list = api.get_users_by_index(index=page)

    return jsonify(users_info_list)

@user_bp.route('/trip_record', methods=['POST', 'GET'])
def user_trip_record():
    """返回用户近期出行记录
    """
    user_id = request.get_data().decode('utf-8')
    trip_record = api.get_user_trip_record(user_id)

    return jsonify(trip_record)