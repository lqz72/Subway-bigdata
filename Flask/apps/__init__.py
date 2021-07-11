import os
from flask import Flask
from sys import path
path.append('..')
path.append(os.path.abspath(os.path.dirname(__file__)).split('apps')[0])
path.append(os.path.abspath(os.path.dirname(__file__)).split('Flask')[0] + 'SubwayModel\\')

import settings
from apps.api_view import api_bp
from apps.login_view import login_bp
from apps.index_view import index_bp
from apps.history_view import history_bp
from apps.predict_view import predict_bp
from apps.station_view import station_bp
from apps.selfcenter_view import selfcenter_bp
from apps.user_view import user_bp

def create_app():
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

    return app


