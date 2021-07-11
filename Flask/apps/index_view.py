from flask import redirect, render_template
from flask import url_for
from flask import Blueprint

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