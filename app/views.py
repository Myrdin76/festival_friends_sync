from flask import render_template, request
import pandas as pd

from app import app

data = pd.read_csv('app/lowlands_schema.csv')
data['id'] = data.index
stages = data['stage'].unique().tolist()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/timetable')
def timetable():
    return render_template('timetable.html', stages=stages)