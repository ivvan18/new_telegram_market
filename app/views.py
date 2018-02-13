# views.py
from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_user
from werkzeug.security import check_password_hash

from app import app, ContactForm, LoginForm, User


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

#contact page
@app.route('/contact')
def contact():
    form = ContactForm()
    return render_template("contact.html", form = form)

#login page
@app.route('/login',  methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('marketplace'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=(form.email.data).lower()).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('marketplace'))

        flash("Invalid email or/and password!")
        return redirect(url_for('login'))

    return render_template("login.html", form = form)


#error 404 page
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


