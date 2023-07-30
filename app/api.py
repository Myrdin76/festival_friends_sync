from flask import render_template, request
import pandas as pd

from app import app

data = pd.read_csv('app/lowlands_schema.csv')
data['id'] = data.index
stages = data['stage'].unique().tolist()

@app.route('/api/fill_table')
def fill_table():
    global data
    stage = request.args.get('stageselector')
    print("SELECTED STAGE: ", stage)
    if stage:
        ndata = data[data['stage'] == stage].to_dict('records')
    else:
        ndata = data.to_dict('records')
        
    return render_template('fill_table.html', data=ndata)

@app.get('/api/select_artist')
def select_artist():
    res = request.args
    print(res)

    return ""