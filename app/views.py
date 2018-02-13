# views.py
from flask_mail import Message

from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_user
from werkzeug.security import check_password_hash, generate_password_hash

from app import app, ContactForm, LoginForm, User, RegisterForm, db, s, mail


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

#register page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('marketplace'))

    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=(form.email.data).lower()).first():
            flash("User already exists!")
            return redirect(url_for('signup'))
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(name=form.name.data, email=(form.email.data).lower(), password=hashed_password,
                        type=form.type.data)
        db.session.add(new_user)
        db.session.commit()

        #Отправка письма
        token = s.dumps(form.email.data, salt='email-confirm')
        msg = Message('Confirm Email', sender='ouramazingapp@gmail.com', recipients=[form.email.data])

        link = url_for('confirm_email', token=token, _external=True)
        msg.body = 'Your link is {}'.format(link)

        mail.send(msg)

        flash("Success! Now you can log in.")
        return redirect(url_for('login'))

    return render_template('signup.html', form=form)



#error 404 page
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


