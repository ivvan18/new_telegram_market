# app/__init__.py
import os
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from itsdangerous import URLSafeTimedSerializer
from wtforms import StringField, PasswordField, BooleanField, validators, SelectField, HiddenField
from wtforms.validators import InputRequired, Email, Length
from flask_login import LoginManager, UserMixin

# Initialize the app
app = Flask(__name__)
Bootstrap(app)

db_path = os.path.join(os.path.dirname(__file__), 'users.db')
channels_path = os.path.join(os.path.dirname(__file__), 'channels.db')
db_uri = 'sqlite:///{}'.format(db_path)

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_BINDS'] = {'channels': 'sqlite:///{}'.format(channels_path)}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config.from_pyfile('config.cfg')


db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#Mail_settings
mail = Mail(app)
s = URLSafeTimedSerializer('giax5RHYLB')

#represents each element in users database
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    type = db.Column(db.String(30))
    email_confirmed = db.Column(db.Boolean(), default=0)
    current_balance = db.Column(db.Float(), default=0)

#represents each element in channels database
class Channel(db.Model):
    __bind_key__ = 'channels'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    link = db.Column(db.String(50))
    description = db.Column(db.String(200))
    subscribers = db.Column(db.Integer)
    price = db.Column(db.Integer)
    category = db.Column(db.String(50))
    image = db.Column(db.String)
    admin_id = db.Column(db.Integer, db.ForeignKey(User.id))


# Initialize contact form
class ContactForm(FlaskForm):
    message = StringField('Problem (no more than 400 symbols)', validators=[ Length(max=400)])
    email = StringField('Email', validators=[InputRequired(), Email(message='Incorrect email.'), Length(max=50)])

#login loading
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Initialize login form
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Incorrect email.'), Length(max=50)])
    password = PasswordField('Password', validators=[InputRequired()])
    remember = BooleanField('Remember me')

# Initialize register form
class RegisterForm(FlaskForm):
    name = StringField('Name', [InputRequired(), Length(min=1, max=50)])
    email = StringField('Email', validators=[InputRequired(), Email(message='Incorrect email.'), Length(max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match.')
    ])
    confirm = PasswordField('Confirm Password')
    type = SelectField('Account type',
                       choices=[('Brand/Agency', 'Brand/Agency'), ('Creator/Influencer', 'Creator/Influencer')])
    tos = BooleanField('I agree to <a href="/tos" style = "color: #54C571;">Terms of Service</a>', validators=[validators.DataRequired()])

# Initialize reset form
class ResetForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Incorrect email.'), Length(max=50)])

# Initialize change password form
class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current password', validators=[InputRequired()])
    new_password = PasswordField('New password', validators=[InputRequired(),
                                                             validators.EqualTo('new_password_confirm', message='Passwords do not match.')])
    new_password_confirm = PasswordField('Confirm new password', validators=[InputRequired()])


# Load the views
from app import views

# Load the config file
app.config.from_object('config')