# views.py
from flask import render_template
from app import app

#main page
@app.route('/')
def index():
    return render_template("index.html")


@app.route('/marketplace')
def marcketplace():
    return render_template("marketplace.html")


@app.route('/tos')
def terms():
    return render_template("tos.html")

