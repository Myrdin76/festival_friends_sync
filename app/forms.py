from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, validators
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User, Group
from app import config

button_style = {"style": "margin-top: 5px;"}

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In', render_kw=button_style)
    
    
class RegistrationForm(FlaskForm):
    username = StringField(('Username'), validators=[DataRequired()])
    email = StringField(('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(('Password'), validators=[DataRequired()])
    password2 = PasswordField(
        ('Repeat Password'), validators=[DataRequired(),
                                           EqualTo('password')])
    submit = SubmitField(('Register'))

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(('Username already in use'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(('Email address already in use'))
        

class ResetPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(),
                                           EqualTo('password')])
    submit = SubmitField('Reset Password', render_kw=button_style)


class ChangeUsernameForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), validators.Length(min=3, max=20)])
    submit = SubmitField('Change Username', render_kw=button_style)
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(('Username already in use'))


class CreateGroupForm(FlaskForm):
    groupname = StringField('Group Name', validators=[DataRequired(), validators.Length(min=3, max=30)])
    submit = SubmitField('Create Group', render_kw=button_style)
    
    def validate_groupname(self, groupname):
        group = Group.query.filter_by(group_name=groupname.data).first()
        if group is not None:
            raise ValidationError(('Group name already in use'))


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit', render_kw=button_style)