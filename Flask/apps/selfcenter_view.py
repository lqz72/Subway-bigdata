import json
from flask import request
from flask import jsonify
from flask import Blueprint

from MysqlOS import SQLOS

selfcenter_bp = Blueprint('selfcenter_bp', __name__)

@selfcenter_bp.route('/admin_info', methods=['POST', 'GET'])
def admin_info() -> json:
    """返回管理员信息
    """
    user_list = SQLOS.get_admin_info()

    return jsonify(user_list)

@selfcenter_bp.route('/wirte_to_database', methods=['POST', 'GET'])
def add_user():
    """新增用户信息
    """
    info_json = request.get_data().decode('utf-8')
    info_dict = json.loads(info_json)

    username  = info_dict['username']
    pwd = info_dict['pwd']
    tips = info_dict['tips']

    res = SQLOS.add_user_to_db(username, pwd, tips)

    return str(res)

@selfcenter_bp.route('/update_database', methods=['POST', 'GET'])
def update_user():
    """修改用户信息
    """
    info_json = request.get_data().decode('utf-8')
    info_dict = json.loads(info_json)

    index = info_dict['index']
    username  = info_dict['inf']['username']
    pwd = info_dict['inf']['pwd']
    tips = info_dict['inf']['tips']

    res = SQLOS.update_user_info(int(index), username, pwd, tips)

    return str(res)

@selfcenter_bp.route('/del_inf', methods=['POST', 'GET'])
def del_user():
    """删除用户信息
    """
    index = request.get_data().decode('utf-8')
    res = SQLOS.del_user_info(int(index))

    return str(res)