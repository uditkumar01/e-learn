from datetime import datetime
from flaskblog import db,login_manager
from flask import current_app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from pytz import timezone



# SQLALCHEMY_TRACK_MODIFICATIONS = True

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable = False, default = "Unknown")
    last_name = db.Column(db.String(100), nullable = False, default = "Unknown")
    country = db.Column(db.String(100), nullable = False, default = "Unknown")
    school = db.Column(db.String(100), nullable = False, default = "Unknown")
    user_type = db.Column(db.String(30), nullable = False, default = "Unknown")
    username = db.Column(db.String(30), unique = True, nullable = False)
    email = db.Column(db.String(150), unique = True, nullable = False)
    password = db.Column(db.String(60), nullable = False)
    profile_pic = db.Column(db.String(100), nullable = False, default = "default_profile_pic.jpg")
    profile_pic_data = db.Column(db.String(100000000), default = "default_profile_pic")
    gender = db.Column(db.String(15),nullable = False, default  = "NULL")
    dob = db.Column(db.String(30),nullable = False, default  = "NULL")
    facebook_link = db.Column(db.String(100), nullable = False, default = "https://facebook.com")
    twitter_link = db.Column(db.String(100), nullable = False, default = "https://twitter.com")
    gmail_link = db.Column(db.String(100), nullable = False, default = "https://myaccount.google.com/intro/profile")
    instagram_link = db.Column(db.String(100), nullable = False, default = "https://instagram.com")
    start_date = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    active =  db.Column(db.String(15), default  = "NULL")
    posts = db.relationship('Post', backref = 'author', lazy = True)


    def get_reset_token(self,expires_in = 900):
        s = Serializer(current_app.config['SECRET_KEY'],expires_in)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)


    def __repr__(self):
        return f"User('{self.first_name}','{self.country}','{self.username}','{self.email}','{self.profile_pic}')"
    
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable = False)
    date_posted = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    content = db.Column(db.Text, nullable = False)
    pic_1 = db.Column(db.String(1000),default = "NO IMAGE")
    pic_2 = db.Column(db.String(1000),default = "NO IMAGE")
    pic_3 = db.Column(db.String(1000),default = "NO IMAGE")
    pic_1_data = db.Column(db.String(100000000), default = "NO IMAGE")
    pic_2_data = db.Column(db.String(100000000), default = "NO IMAGE")
    pic_3_data = db.Column(db.String(100000000), default = "NO IMAGE")
    post_type = db.Column(db.String(30), nullable = False, default = "global")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    
    comments = db.relationship('Comment', backref = 'blog', lazy = True)

    def __repr__(self):
        return f"Post('{self.title}','{self.content}','{self.date_posted}')"

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    commentor = db.Column(db.String(30), nullable = False)
    comment = db.Column(db.String(100000), nullable = False)
    # post_writer = db.Column(db.String(30), nullable = False)
    post__id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable = False)
    # profile_pic = db.Column(db.String(100), nullable = False, default = "default_profile_pic.jpg")
    timestamp = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)

    def __repr__(self):
        return f"Comment('{self.comment}','{self.commentor}',{self.post__id},'{self.timestamp}')"

class Post_like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    like_type = db.Column(db.String(100), default="heart")
    user_id = db.Column(db.Integer, nullable = False)
    post_id = db.Column(db.Integer, nullable = False)

    def __repr__(self):
        return f"Post_like('{self.like_type}','{self.user_id}',{self.post_id})"

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable = False)
    task = db.Column(db.String(10000), nullable = False)
    timestamp = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)

    def __repr__(self):
        return f"Todo('{self.username}','{self.task}',{self.timestamp})"

class Timeline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable = False)
    title = db.Column(db.String(10000), nullable = False)
    text = db.Column(db.String(10000), nullable = False)
    time_am_pm = db.Column(db.String(30), nullable = False, default = "None")
    timestamp = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)

    def __repr__(self):
        return f"Timeline('{self.username}','{self.title}',{self.text})"

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable = False)
    active_user_id = db.Column(db.Integer, nullable = False)
    text = db.Column(db.String(1000000), nullable = False)
    pic_1 = db.Column(db.String(1000),default = "NO IMAGE")
    pic_1_data = db.Column(db.String(100000000), default = "NO IMAGE")
    seen = db.Column(db.String(1000),default = "not seen")
    time_am_pm = db.Column(db.String(30), nullable = False, default = "None")
    timestamp = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)

    def __repr__(self):
        return f"Message('{self.user_id}','{self.text}',{self.time_am_pm})"

class Notify(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable = False)
    title = db.Column(db.String(10000), nullable = False)
    text = db.Column(db.String(10000), nullable = False)
    post_id = db.Column(db.String(1000),nullable = False)
    timestamp = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)

    def __repr__(self):
        return f"Timeline('{self.username}','{self.title}',{self.text})"

