# views.py
from flask_mail import Message
import regex as re

from flask import render_template, redirect, url_for, flash, abort
from flask_login import current_user, login_user, login_required, logout_user
from itsdangerous import SignatureExpired
from werkzeug.security import check_password_hash, generate_password_hash

from app.channel_info import ChannelInfo
from app.generator import getrandompassword
from models import User, Channel
from forms import ChangeMailForm, ContactForm, ChangePasswordForm, ChangeUsernameForm, CreateChannelForm, LoginForm, RegisterForm, ResetForm

from app import app, login_manager, db, mail, s

#login loading
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#main page
@app.route('/')
def index():
    return render_template("navbar/index.html")

#marketplace page
@app.route('/marketplace')
@login_required
def marketplace():
    channels = Channel.query.all()
    return render_template("navbar/marketplace.html", channels = channels)

#term of service page
@app.route('/tos')
def terms():
    return render_template("footer/tos.html")

#privacy page
@app.route('/privacy')
def privacy():
    return render_template("footer/privacy.html")

#contact page
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        msg = Message('User meassage', sender='ouramazingapp@gmail.com', recipients=['ouramazingapp@gmail.com'])
        msg.html = form.message.data
        mail.send(msg)
        return redirect('/')

    return render_template("footer/contact.html", form = form)

#login page
@app.route('/login',  methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('marketplace'))

    form = LoginForm()
    form1 = ResetForm()

    if form.validate_on_submit():
        user = db.session.query(User).filter_by(email=(form.email.data).lower()).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('marketplace'))

        flash("Invalid email or/and password!")
        return redirect(url_for('login'))

    if form1.validate_on_submit():
        if not db.session.query(User).filter_by(email=form1.email.data.lower()).first():
            flash("User with email you entered not found!")
            return redirect(url_for('login'))
        else:
            new_password = getrandompassword()
            curr = db.session.query(User).filter_by(email=form1.email.data.lower()).first()
            curr.password = generate_password_hash(new_password, method='sha256')
            db.session.commit()

            msg = Message('Password reset', sender='ouramazingapp@gmail.com', recipients=[form1.email.data])
            msg.html = 'Your new password is <b>{}</b>, you can change it in account settings'.format(new_password)
            mail.send(msg)

            flash('Check your email for further instructions.')
            return redirect(url_for('login'))

    return render_template("forms/login.html", form = form, form1 = form1)

#register page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('marketplace'))

    form = RegisterForm()
    if form.validate_on_submit():
        if db.session.query(User).filter_by(email=(form.email.data).lower()).first():
            flash("User already exists!")
            return redirect(url_for('signup'))
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        if re.search('[a-zA-Z]', form.name.data):
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
        else:
            flash('Invalid username! It must contain at least 1 english letter.')
            return redirect(url_for('signup'))

    return render_template('forms/signup.html', form=form)


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    change_username_form = ChangeUsernameForm()
    change_email_form = ChangeMailForm()
    change_password_form = ChangePasswordForm()

    #actions with changing username
    if change_username_form.validate_on_submit():
        if re.search('[a-zA-Z]', change_username_form.name.data):
            current_user.name = change_username_form.name.data
            db.session.commit()
            flash('Successfully updated your username!')
            return redirect(url_for('settings'))
        else:
            flash('Invalid username! It must contain at least 1 english letter.')
            return redirect(url_for('settings'))


    #actions with changing email
    if change_email_form.validate_on_submit():
        if db.session.query(User).filter_by(email=(change_email_form.new_email.data).lower()).first():
            flash("Error! User with the given email already exists! ")
            return redirect(url_for('settings'))

        if check_password_hash(current_user.password, change_email_form.current_password.data):
            curr = db.session.query(User).filter_by(email=(current_user.email).lower()).first()
            curr.email = change_email_form.new_email.data
            # Message sending
            token = s.dumps(change_email_form.new_email.data, salt='email-confirm')
            msg = Message('Confirm Email', sender='ouramazingapp@gmail.com', recipients=[change_email_form.new_email.data])

            link = url_for('confirm_email', token=token, _external=True)
            msg.body = 'Your link is {}'.format(link)

            mail.send(msg)
            current_user.email_confirmed = 0
            db.session.commit()
            flash("Success! Now you can confirm your new email!")
            return redirect(url_for('settings'))
        else:
            flash("Error! Password does not match! ")
            return redirect(url_for('settings'))


    #actions with changing password
    if change_password_form.validate_on_submit():
        if check_password_hash(current_user.password, change_password_form.current_password.data):
            new_hashed_password = generate_password_hash(change_password_form.new_password.data, method='sha256')

            curr = db.session.query(User).filter_by(email=current_user.email).first()
            curr.password = new_hashed_password

            db.session.commit()
            flash('Successfully updated your password!')
            return redirect(url_for('settings'))
        else:
            flash('Current password is wrong!')
            return redirect(url_for('settings'))


    return render_template('profile/settings.html', change_username_form = change_username_form, change_email_form = change_email_form, change_password_form = change_password_form)



@app.route('/add_channel', methods=['GET', 'Post'])
@login_required
def add_channel():
    if current_user.type != 'Brand/Agency':
        flash('You cannot add a channel because of your account type!')
        return redirect(url_for('marketplace'))
    form = CreateChannelForm()
    if form.validate_on_submit():
        if db.session.query(Channel).filter_by(link=form.link.data).first():
            flash('Such marketplace already exists!')
            return redirect(url_for('add_channel'))
        try:
            # some magic with api inside ChannelInfo object
            ci = ChannelInfo(form.link.data)
            form.name.data = ci.name
            new_channel = Channel(name=ci.name,
                                  link=form.link.data, description=form.description.data,
                                  subscribers=ci.subscribers,
                                  price=form.price.data, category=form.category.data,
                                  image=ci.photo, admin_id=current_user.id)

            db.session.add(new_channel)
            db.session.commit()

            flash('Great! Your channel "%s" successfully added!' % new_channel.name)

            return redirect(url_for('marketplace'))
        except NameError:
            flash('No such channel found or incorrect link given!')
            return redirect(url_for('add_channel'))

    return render_template('profile/add_channel.html', form=form)


@app.route('/channel/<r>')
@login_required
def channel(r):
    chan = Channel.query.filter_by(link='@'+r).first()
    if not chan:
        abort(404)
    return render_template('channel.html', chan=chan)


#sending confirmation link
@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
        curr = db.session.query(User).filter_by(email=email).first()
        curr.email_confirmed = 1
        db.session.commit()
    except SignatureExpired:
        return '<h1>The confirmation link has expired...</h1>'
    return render_template('additional/confirm_email.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))



#error 404 page
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


