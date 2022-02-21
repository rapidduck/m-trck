from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(message="Please enter your email."),
                                             Email(message="Please enter a valid email.")])
    password = PasswordField("Password", validators=[DataRequired(message="Please enter your password.")])
    submit = SubmitField("Log In")


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(message="Please enter your email."),
                                             Email(message="Please enter a valid email."),
                                             Length(max=100)])
    password = PasswordField("Password", validators=[DataRequired(message="Please enter your password."),
                                                     Length(min=8, max=50, message="This password is too short.")])
    submit = SubmitField("Register")


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField("Old Password", validators=[DataRequired(message="Please enter your password.")])
    new_password = PasswordField("New Password", validators=[DataRequired(message="Please enter your password."),
                                                             Length(min=8, max=50, message="This password is too short.")])
    submit = SubmitField("Submit")