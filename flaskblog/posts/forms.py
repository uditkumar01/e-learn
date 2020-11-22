from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flaskblog.models import User
from wtforms import SubmitField,StringField,PasswordField,BooleanField, IntegerField, DateField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, ValidationError, EqualTo
from flask_login import current_user


class Post_form(FlaskForm):

    post_title = StringField('Title',validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    pic_1 = FileField('Image #1' , validators= [FileAllowed(['jpg','jpeg','png','webp'])])
    pic_2 = FileField('Image #2' , validators= [FileAllowed(['jpg','jpeg','png','webp'])])
    pic_3 = FileField('Image #3' , validators= [FileAllowed(['jpg','jpeg','png','webp'])])
    submit = SubmitField('Post')

class Comment_form(FlaskForm):
    # commentor = StringField('Commentor',validators=[DataRequired(),Length(min = 3 , max = 20,message="Length should be between 3 to 20")])
    comment = TextAreaField('Comment', validators=[DataRequired(),Length(min = 2 , max = 99999,message="Length should be between 2 to 99999")])
    # like = BooleanField('Like')
    # post__id = IntegerField('Post_id', validators=[DataRequired()])
    submit = SubmitField('Post')

    def user_existance(self, commentor):
        user = User.query.filter_by(username = commentor.data).first()
        if not user:
            raise ValidationError('No such username exists')