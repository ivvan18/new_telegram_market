# views.py
from flask_mail import Message

from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, login_required, logout_user
from itsdangerous import SignatureExpired
from werkzeug.security import check_password_hash, generate_password_hash
from app.generator import getrandompassword


from app import app, ContactForm, LoginForm, User, RegisterForm, db, s, mail, ResetForm, ChangePasswordForm, Channel


#main page
@app.route('/')
def index():
    return render_template("index.html")

#marketplace page
@app.route('/marketplace')
@login_required
def marketplace():
    channels = Channel.query.all()
    return render_template("marketplace.html", channels = channels)

#term of service page
@app.route('/tos')
def terms():
    return render_template("tos.html")

#privacy page
@app.route('/privacy')
def privacy():
    return render_template("privacy.html")

#contact page
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        msg = Message('User meassage', sender='ouramazingapp@gmail.com', recipients=['ouramazingapp@gmail.com'])
        msg.html = form.message.data
        mail.send(msg)
        return redirect('/')

    return render_template("contact.html", form = form)

#login page
@app.route('/login',  methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('marketplace'))

    form = LoginForm()
    form1 = ResetForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=(form.email.data).lower()).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('marketplace'))

        flash("Invalid email or/and password!")
        return redirect(url_for('login'))

    if form1.validate_on_submit():
        if not User.query.filter_by(email=form1.email.data.lower()).first():
            flash("User with email you entered not found!")
            return redirect(url_for('login'))
        else:
            new_password = getrandompassword()
            curr = User.query.filter_by(email=form1.email.data.lower()).first()
            curr.password = generate_password_hash(new_password, method='sha256')
            db.session.commit()

            msg = Message('Password reset', sender='ouramazingapp@gmail.com', recipients=[form1.email.data])
            msg.html = 'Your new password is <b>{}</b>, you can change it in account settings'.format(new_password)
            mail.send(msg)

            flash('Check your email for further instructions.')
            return redirect(url_for('login'))

    return render_template("login.html", form = form, form1 = form1)

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

        #Message sending
        token = s.dumps(form.email.data, salt='email-confirm')
        msg = Message('Confirm Email', sender='ouramazingapp@gmail.com', recipients=[form.email.data])

        link = url_for('confirm_email', token=token, _external=True)
        msg.body = 'Your link is {}'.format(link)

        mail.send(msg)

        flash("Success! Now you can log in.")
        return redirect(url_for('login'))

    return render_template('signup.html', form=form)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if check_password_hash(current_user.password, form.current_password.data):
            new_hashed_password = generate_password_hash(form.new_password.data, method='sha256')

            curr = User.query.filter_by(email=current_user.email).first()
            curr.password = new_hashed_password

            db.session.commit()
            flash('Successfully updated your password')
            return redirect(url_for('settings'))
        else:
            flash('Current password is wrong')
            return redirect(url_for('settings'))
    return render_template('settings.html', form=form)


#sending confirmation link
@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
        curr = User.query.filter_by(email=email).first()
        curr.email_confirmed = 1
        db.session.commit()
    except SignatureExpired:
        return '<h1>The confirmation link has expired...</h1>'
    return render_template('confirm_email.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))



#error 404 page
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


