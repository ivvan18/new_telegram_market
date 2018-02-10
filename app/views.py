# views.py
from flask import render_template
from app import app

#main page
@app.route('/')
def index():
    return render_template("index.html")

#marketplace page
@app.route('/marketplace')
def marketplace():
    return render_template("marketplace.html")

#term of service page
@app.route('/tos')
def terms():
    return render_template("tos.html")

#privacy page
@app.route('/privacy')
def privacy():
    return render_template("privacy.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


