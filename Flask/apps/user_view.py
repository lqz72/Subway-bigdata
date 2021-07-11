from flask import render_template
from apps.api_view import *

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/client')
def client():
    return render_template('client.html')

@user_bp.route('/userinf')
def userinf():
    return render_template('userinf.html')

@user_bp.route('/user_info', methods=['POST', 'GET'])
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

@user_bp.route('/user_record', methods=['POST', 'GET'])
def user_trip_record():
    """返回用户近期出行记录
    """
    user_id = request.get_data().decode('utf-8')
    trip_record = api.get_user_trip_record(user_id)

    return jsonify(trip_record)