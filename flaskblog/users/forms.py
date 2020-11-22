from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import SubmitField,StringField,PasswordField,BooleanField, IntegerField, DateField
from wtforms.validators import DataRequired, Length, Email, ValidationError, EqualTo
from flaskblog.models import User
from flask_login import current_user


class Registration_Form_School(FlaskForm):

    username = StringField('Username',validators = [DataRequired(),Length(min = 3 , max = 20,message="Length should be between 3 to 20")])
    email = StringField('Email', validators = [DataRequired(), Email()])
    password = PasswordField('Password',validators = [DataRequired()])
    # confirm_password = PasswordField('Password',validators = [DataRequired(),EqualTo('password')])
    school_name = StringField('Username',validators = [DataRequired(),Length(min = 3 , max = 1000,message="Length should be between 3 to 1000")])
    # phone = StringField('Phone Number', validators = [DataRequired()])
    # gender = StringField('Gender',validators = [DataRequired()])
    country = StringField('Country',validators = [DataRequired()])
    # user_type = StringField('Type',validators = [DataRequired()])
    # dob = StringField("DOB", validators=[DataRequired()])
    signup = SubmitField('Sign Up')
    checkbox = BooleanField('checkbox',validators=[DataRequired()])

    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError('Username Already Exists')
    
    def validate_phone(self, phone):
        user = User.query.filter_by(username = phone.data).first()
        if user:
            raise ValidationError('Phone Already Exists')
    
    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError('Email Already Exists')

class Registration_Form(FlaskForm):

    username = StringField('Username',validators = [DataRequired(),Length(min = 3 , max = 20,message="Length should be between 3 to 20")])
    email = StringField('Email', validators = [DataRequired(), Email()])
    password = PasswordField('Password',validators = [DataRequired()])
    # confirm_password = PasswordField('Password',validators = [DataRequired(),EqualTo('password')])
    # full_name = StringField('Username',validators = [DataRequired(),Length(min = 3 , max = 100,message="Length should be between 3 to 100")])
    # phone = StringField('Phone Number', validators = [DataRequired()])
    # gender = StringField('Gender',validators = [DataRequired()])
    country = StringField('Country',validators = [DataRequired()])
    # user_type = StringField('Type',validators = [DataRequired()])
    dob = StringField("DOB", validators=[DataRequired()])
    signup = SubmitField('Sign Up')
    checkbox = BooleanField('checkbox',validators=[DataRequired()])

    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError('Username Already Exists')
    
    def validate_phone(self, phone):
        user = User.query.filter_by(username = phone.data).first()
        if user:
            raise ValidationError('Phone Already Exists')
    
    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError('Email Already Exists')

class Login_form(FlaskForm):

    email = StringField('Username/Email', validators = [DataRequired()])
    password = PasswordField('Password',validators = [DataRequired()])
    signin = SubmitField('Sign In')
    checkbox = BooleanField('checkbox')

class Update_Form(FlaskForm):
    # first_name = StringField('First',validators = [DataRequired()])
    # last_name = StringField('Last',validators = [DataRequired()])
    # country = StringField('Country',validators = [DataRequired()])
    # skills = StringField('Skills',validators = [DataRequired()])
    # username = StringField('Username',validators = [DataRequired(),Length(min = 3 , max = 20,message="Length should be between 3 to 20")])
    # email = StringField('Email', validators = [DataRequired(), Email()])
    profile_pic = FileField('Update Profile Picture' , validators= [FileAllowed(['jpg','jpeg','png','webp'])])
    update = SubmitField('Update')

    # def validate_username(self, username):
    #     if username.data != current_user.username:
    #         user = User.query.filter_by(username = username.data).first()
    #         if user:
    #             raise ValidationError('Username Already Exists')
    
    # def validate_email(self, email):
    #     if email.data != current_user.email:
    #         user = User.query.filter_by(email = email.data).first()
    #         if user:
    #             raise ValidationError('Email Already Exists')


class Request_reset_form(FlaskForm):
    email = StringField('Email', validators = [DataRequired(), Email()])
    submit = SubmitField('Request Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if not user:
            raise ValidationError('No such email address exists. Please Register .')

class Change_password(FlaskForm):
    password = PasswordField('Password',validators = [DataRequired()])
    confirm_password = PasswordField('Password',validators = [DataRequired(),EqualTo('password')])
    submit = SubmitField('Set Password')
