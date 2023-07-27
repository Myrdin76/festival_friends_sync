from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd


app = Flask(__name__)
data = pd.read_csv('lowlands_schema.csv').to_dict('records')

@app.route('/')

def index():
    return render_template('index.html')


@app.route('/table')
def timetable():
    return render_template('timetable.html')


@app.route('/fill_table')
def fill_table():
    
    return render_template('fill_table.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)