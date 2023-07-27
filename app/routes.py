from flask import render_template
import pandas as pd

from app import app

data = pd.read_csv('app/lowlands_schema.csv').to_dict('records')

@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/')
def timetable():
    return render_template('timetable.html')


@app.route('/fill_table')
def fill_table():
    
    return render_template('fill_table.html', data=data)