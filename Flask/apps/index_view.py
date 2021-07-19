from flask import redirect, render_template
from flask import url_for
from flask import Blueprint

from DataAnalysis import DataApi
index_bp = Blueprint('index_bp', __name__)

@index_bp.route('/')
def root():
    return redirect(url_for('index_bp.index'))

@index_bp.route('/index')
def index():
    return render_template('index.html')

@index_bp.route('/login')
def login():
    return render_template('login.html')

@index_bp.route('/aboutus')
def aboutus():
    return render_template('about-us.html')

@index_bp.route('/eventdetails')
def eventdetails():
    return render_template('event-details.html')

@index_bp.route('/history')
def history():
    return render_template('history.html')

@index_bp.route('/predict')
def predict():
    return render_template('predict.html')

@index_bp.route('/selfcenter')
def selfcenter():
    return render_template('selfcenter.html')

@index_bp.route('/station/<sta_name>')
def station(sta_name):
    sta_info = DataApi.get_station_info(sta_name)
    return render_template('sta.html', sta_name=sta_name, sta_info=sta_info)

@index_bp.route('/client')
def client():
    return render_template('client.html')

@index_bp.route('/userinfo')
def userinfo():
    return render_template('userinfo.html')