from flask import redirect
from flask import request, url_for
from flask import session, flash
from flask import Blueprint

login_bp = Blueprint('login_bp', __name__)
require_login_path = ['history', 'station', 'predict', 'client', 'selfcenter', 'userinf']

#设置session
@login_bp.route('/verify/<uid>/<utype>')
def verify(uid, utype):
    response = redirect(url_for('history_bp.history'))
    #使用更安全的session
    session['uid'] = uid
    session['utype'] = utype
    # response.set_cookie('utype', utype, max_age= 60*60*24)
    return response

#路由拦截及重定向
@login_bp.before_request
def my_before_request():
    url_head = request.path.split('/')[1]
    if url_head == 'history' and request.path.split('/')[-1] != url_head:
        return
    if url_head in require_login_path:
        # utype = request.cookies.get('utype', None)
        utype = session.get('utype', None)
        if utype:
            if utype != 'admin' and (url_head not in ['client']):
                flash("很抱歉！您没有权限访问")
                return redirect(url_for('user_view.client'))
        else:
            flash("您还没有登录账号！")
            return redirect(url_for('index.login'))