from flask import redirect
from flask import url_for
from flask import session
from flask import Blueprint

login_bp = Blueprint('login_bp', __name__, url_prefix='/login')
require_login_path = ['history', 'station', 'predict', 'client', 'selfcenter', 'userinf']

#设置session
@login_bp.route('/verify/<uid>/<utype>')
def verify(uid, utype):
    response = redirect(url_for('index_bp.history'))
    #使用更安全的session
    session['uid'] = uid
    session['utype'] = utype
    # response.set_cookie('utype', utype, max_age= 60*60*24)
    return response