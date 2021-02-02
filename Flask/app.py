from flask import Flask,Response
from flask import render_template
from flask import redirect
from sys import path
import os
path.append('..')
path.append(os.path.abspath(os.path.dirname(__file__)).split('Flask')[0])
path.append(os.path.abspath(os.path.dirname(__file__)).split('Flask')[0] + 'PredictModel\\')
print(path)
from PredictModel import AgeStructure, MonthFlow, StationFlow, WeekdayFlow

app = Flask(__name__)

@app.route('/')
def index():
    
    return render_template('index.html')

#测试 
@app.route('/data')
def data():
    age, value = AgeStructure.get_age_structure()

    #return json.dumps({'age':age,'value':value},ensure_ascii=False) #如果有中文的话，就需要ensure_ascii=False
    return render_template('data.html', age = age, value = value)

if __name__ == '__main__':
    app.run()


