import os
from sys import path
from flask import Flask
from flask import flash, redirect, url_for
from flask import request, session

path.append('..')
path.append(os.path.abspath(os.path.dirname(__file__)).split('apps')[0])
path.append(os.path.abspath(os.path.dirname(__file__)).split('apps')[0] + 'apps\\')
path.append(os.path.abspath(os.path.dirname(__file__)).split('Flask')[0] + 'SubwayModel\\')

import settings
from api_view import api_bp
from login_view import login_bp
from index_view import index_bp
from history_view import history_bp
from predict_view import predict_bp
from station_view import station_bp
from selfcenter_view import selfcenter_bp
from user_view import user_bp

require_login_path = ['history', 'station', 'predict', 'client', 'selfcenter', 'userinf']

def create_app():
    """创建一个web应用程序
    """
    app = Flask(__name__)
    app.static_folder = '../static'
    app.template_folder = '../templates'
    app.config.from_object(settings)

    app.register_blueprint(api_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(index_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(predict_bp)
    app.register_blueprint(station_bp)
    app.register_blueprint(selfcenter_bp)
    app.register_blueprint(user_bp)

    # 路由拦截及重定向
    @app.before_request
    def my_before_request():
        url_head = request.path.split('/')[1]
        if url_head == 'history' and request.path.split('/')[-1] != url_head:
            return
        if url_head in require_login_path:
            utype = session.get('utype', None)
            if utype:
                if utype != 'admin' and (url_head not in ['client']):
                    flash("很抱歉！您没有权限访问")
                    return redirect(url_for('user_bp.client'))
            else:
                flash("您还没有登录账号！")
                return redirect(url_for('index_bp.login'))

    return app


