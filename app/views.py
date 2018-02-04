# views.py
from flask import render_template
from app import app

#main page
@app.route('/')
def index():
    return render_template("index.html")


@app.route('/marketplace')
def about():
    return render_template("marketplace.html")

