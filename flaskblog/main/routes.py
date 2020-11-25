from flask import render_template, request, Blueprint, url_for, redirect, flash
from flaskblog.models import Post, Comment, User, Post_like, Todo, Timeline,Notify,Message
from datetime import datetime
from flask_login import current_user
from flaskblog.posts.forms import Post_form
from flaskblog import db
from flaskblog.users.utils import add_post_pic, img_exists
from pytz import timezone
import io
from PIL import Image
import base64
import os

main = Blueprint('main',__name__)


@main.route("/", methods = ['POST','GET'])
@main.route("/home", methods = ['POST','GET'])
def home():
    post_form = Post_form()

    if not (current_user.is_authenticated):
        # return render_template("index.html")
        return redirect(url_for('users.login'))
    print("post form", post_form.validate_on_submit(), request.method)

    if request.method == "POST" and post_form.validate_on_submit():
        
        print(post_form.pic_1.data,post_form.pic_2.data,post_form.pic_3.data)
        post_imgs = []
        if post_form.pic_1.data:
            post_imgs.append(add_post_pic(post_form.pic_1.data))
            
        if post_form.pic_2.data:
            post_imgs.append(add_post_pic(post_form.pic_2.data))
        if post_form.pic_3.data:
            post_imgs.append(add_post_pic(post_form.pic_3.data))

        post_type = request.form['post_type']
        if post_type == "local":
            post_type = current_user.school

        

        if len(post_imgs) == 3:
            post = Post(title = post_form.post_title.data,post_type = post_type, content = post_form.content.data,pic_1 = post_imgs[0][0], pic_1_data = post_imgs[0][1],pic_2 = post_imgs[1][0], pic_2_data = post_imgs[1][1],pic_3 = post_imgs[2][0], pic_3_data = post_imgs[2][1], author = current_user)
        elif len(post_imgs) == 2:
            post = Post(title = post_form.post_title.data,post_type = post_type, content = post_form.content.data, pic_1 = post_imgs[0][0], pic_1_data = post_imgs[0][1],pic_2 = post_imgs[1][0], pic_2_data = post_imgs[1][1], author = current_user)
        elif len(post_imgs) == 1:
            post = Post(title = post_form.post_title.data,post_type = post_type, content = post_form.content.data,pic_1 = post_imgs[0][0], pic_1_data = post_imgs[0][1], author = current_user)
        else:
            post = Post(title = post_form.post_title.data,post_type = post_type, content = post_form.content.data, author = current_user)



        db.session.add(post)
        db.session.commit()

        now_utc = datetime.now(timezone('UTC'))
        now_asia = now_utc.astimezone(timezone('Asia/Kolkata'))
        

        add_time = Timeline(username=current_user.username,title="New Post posted",text=current_user.username+" posted a new post named "+post_form.post_title.data+" at "+now_asia.strftime("%I:%M %p"), time_am_pm = now_asia.strftime("%I:%M %p"))
        db.session.add(add_time)
        db.session.commit()

        flash('Your post is posted! ', 'success')
    # all_his_comments = Comment.query.order_by(Comment.timestamp.desc()).filter(Comment.commentor == current_user.username,Comment.timestamp >= todays_datetime).all()
    # all_got_comments = Comment.query.order_by(Comment.timestamp.desc()).filter_by(post_writer = current_user.username).all()
    # all_likes = Post_like.query.order_by(Post_like.timestamp.desc()).filter_by(user_post = current_user.id).all()
    # all_chats = Chat.query.order_by(Chat.time_of_chat.desc()).filter_by(user__id = current_user.id).all()
    page_no = request.args.get('page',1,type = int)
    posts = Post.query.order_by(Post.date_posted.desc()).filter(Post.post_type == "global").paginate(page = page_no,per_page = 4)
    all_tasks = Todo.query.order_by(Todo.timestamp.desc()).filter_by(username = current_user.username).limit(5).all()
    posts_with_like_count = []
    for post in posts.items:
        user_exist = Post_like.query.filter_by(post_id = post.id,user_id = current_user.id).first()
        print(post,user_exist)
        like_status = "false"
        comment_status = "false"
        if user_exist:
            
            like_status = "true"
        user_exist = Comment.query.filter_by(post__id = post.id,commentor = current_user.username).first()
        if user_exist:
            
            comment_status = "true"
            
        no_of_likes = len(Post_like.query.filter_by(post_id = post.id).all())
        no_of_comments = len(Comment.query.filter_by(post__id = post.id).all())
        
        # checking deleted post pics begin
        if post.pic_1!="NO IMAGE" and not img_exists(post.pic_1):
            print("not exists")
            f = io.BytesIO(base64.b64decode(post.pic_1_data))
            pilimage = Image.open(f)
            pic_path = os.path.join(os.path.join(os.path.join(os.path.join(os.getcwd(),"flaskblog"), "static"),"img"),post.pic_1)

            pilimage.save(pic_path)
        
        if post.pic_2!="NO IMAGE" and not img_exists(post.pic_2):
            print("not exists")
            f = io.BytesIO(base64.b64decode(post.pic_2_data))
            pilimage = Image.open(f)
            pic_path = os.path.join(os.path.join(os.path.join(os.path.join(os.getcwd(),"flaskblog"), "static"),"img"),post.pic_2)

            pilimage.save(pic_path)

        if post.pic_3!="NO IMAGE" and not img_exists(post.pic_3):
            print("not exists")
            f = io.BytesIO(base64.b64decode(post.pic_3_data))
            pilimage = Image.open(f)
            pic_path = os.path.join(os.path.join(os.path.join(os.path.join(os.getcwd(),"flaskblog"), "static"),"img"),post.pic_3)

            pilimage.save(pic_path)



        posts_with_like_count.append({'id':post.id ,'username':post.author.username,'post_profile_pic':post.author.profile_pic,'user_type':post.author.user_type,'post_title':post.title,'date_posted':post.date_posted,'pic_1':post.pic_1,'pic_2':post.pic_2,'pic_3':post.pic_3,'like_status':like_status,'no_of_likes':no_of_likes,'no_of_comments':no_of_comments,'comment_status':comment_status, })
    # all_like_users = []
    # all_chat_users = []
    # all_his_comment_users = []
    # for like in all_likes:
    #     user = User.query.get_or_404(like.user__id)
    #     all_like_users.append([user.username,user.id,like.post_id])
    # for chat in all_chats:
    #     user = User.query.get_or_404(chat.user_start_id)
    #     all_chat_users.append([user.username,user.id])
    # for comment in all_his_comments:
    #     post = Post.query.get_or_404(comment.post_id)
    #     all_his_comment_users.append([post.author,comment.post__id])


    # img_exists(current_user.profile_pic,current_user.profile_pic_data)

    if not img_exists(current_user.profile_pic):
        print("not exists")
        f = io.BytesIO(base64.b64decode(current_user.profile_pic_data))
        print(type(f))
        pilimage = Image.open(f)
        pic_path = os.path.join(os.path.join(os.path.join(os.path.join(os.getcwd(),"flaskblog"), "static"),"img"),current_user.profile_pic)

        pilimage.save(pic_path)

    alerts = Notify.query.filter_by(username = current_user.username).limit(5).all()


    notify = Message.query.filter_by(user_id = current_user.id,seen = "not seen").limit(10).all()

    all_notify = []

    for notification1 in notify:
        notify_user = User.query.get_or_404(notification1.active_user_id)
        check1 = True
        for n_user in range(len(all_notify)):
            if notify_user.username == all_notify[n_user].get('username'):
                all_notify[n_user]['count'] += 1
                all_notify[n_user]['text'] = notification1.text
                check1 = False
        if check1:
            all_notify.append({'username':notify_user.username, 'profile_pic':notify_user.profile_pic, 'text':notification1.text, 'timestamp': notification1.timestamp, 'count':1})

    all_notify_len = Message.query.filter_by(user_id = current_user.id,seen = "not seen").count()
    if all_notify_len > 9:
        all_notify_len = "9+"

    if current_user.is_authenticated:
        
        return render_template('dashboard.html' , title = "Posts", all_tasks = all_tasks, posts_with_like_count = posts_with_like_count, posts = posts, post_form = post_form, time_now = datetime.utcnow(), like_status = "true", all_notify = all_notify, all_notify_len = all_notify_len, alerts = alerts)
    else:
        
        return render_template('dashboard.html' , title = "Posts", all_tasks = all_tasks, posts_with_like_count = posts_with_like_count, posts = posts, post_form = post_form, time_now = datetime.utcnow(), like_status = "true")



@main.route("/local_post", methods = ['GET','POST'])
def local():
    post_form = Post_form()

    if not (current_user.is_authenticated):
        # return render_template("index.html")
        return redirect(url_for('users.login'))
    print("post form", post_form.validate_on_submit(), request.method)

    if request.method == "POST" and post_form.validate_on_submit():
        
        print(post_form.pic_1.data,post_form.pic_2.data,post_form.pic_3.data)
        post_imgs = []
        if post_form.pic_1.data:
            post_imgs.append(add_post_pic(post_form.pic_1.data))
            
        if post_form.pic_2.data:
            post_imgs.append(add_post_pic(post_form.pic_2.data))
        if post_form.pic_3.data:
            post_imgs.append(add_post_pic(post_form.pic_3.data))
        print(len(post_imgs),post_imgs)

        post_type = request.form['post_type']
        if post_type == "local":
            post_type = current_user.school

        if len(post_imgs) == 3:
            post = Post(title = post_form.post_title.data,post_type = post_type, content = post_form.content.data,pic_1 = post_imgs[0],pic_2 = post_imgs[1],pic_3 = post_imgs[2], author = current_user)
        elif len(post_imgs) == 2:
            post = Post(title = post_form.post_title.data,post_type = post_type, content = post_form.content.data,pic_1 = post_imgs[0],pic_2 = post_imgs[1], author = current_user)
        elif len(post_imgs) == 1:
            post = Post(title = post_form.post_title.data,post_type = post_type, content = post_form.content.data,pic_1 = post_imgs[0], author = current_user)
        else:
            post = Post(title = post_form.post_title.data,post_type = post_type, content = post_form.content.data, author = current_user)



        db.session.add(post)
        db.session.commit()

        now_utc = datetime.now(timezone('UTC'))
        now_asia = now_utc.astimezone(timezone('Asia/Kolkata'))
        

        add_time = Timeline(username=current_user.username,title="New Post posted",text=current_user.username+" posted a new post named "+post_form.post_title.data+" at "+now_asia.strftime("%I:%M %p"), time_am_pm = now_asia.strftime("%I:%M %p"))
        db.session.add(add_time)
        db.session.commit()

        flash('Your post is posted! ', 'success')
    # all_his_comments = Comment.query.order_by(Comment.timestamp.desc()).filter(Comment.commentor == current_user.username,Comment.timestamp >= todays_datetime).all()
    # all_got_comments = Comment.query.order_by(Comment.timestamp.desc()).filter_by(post_writer = current_user.username).all()
    # all_likes = Post_like.query.order_by(Post_like.timestamp.desc()).filter_by(user_post = current_user.id).all()
    # all_chats = Chat.query.order_by(Chat.time_of_chat.desc()).filter_by(user__id = current_user.id).all()
    page_no = request.args.get('page',1,type = int)
    posts = Post.query.order_by(Post.date_posted.desc()).filter(Post.post_type != "global").paginate(page = page_no,per_page = 4)
    all_tasks = Todo.query.order_by(Todo.timestamp.desc()).filter_by(username = current_user.username).limit(5).all()
    posts_with_like_count = []
    for post in posts.items:
        user_exist = Post_like.query.filter_by(post_id = post.id,user_id = current_user.id).first()
        print(post,user_exist)
        like_status = "false"
        comment_status = "false"
        if user_exist:
            
            like_status = "true"
        user_exist = Comment.query.filter_by(post__id = post.id,commentor = current_user.username).first()
        if user_exist:
            
            comment_status = "true"
            
        no_of_likes = len(Post_like.query.filter_by(post_id = post.id).all())
        no_of_comments = len(Comment.query.filter_by(post__id = post.id).all())
        
        posts_with_like_count.append({'id':post.id ,'username':post.author.username,'post_profile_pic':post.author.profile_pic,'user_type':post.author.user_type,'post_title':post.title,'date_posted':post.date_posted,'pic_1':post.pic_1,'pic_2':post.pic_2,'pic_3':post.pic_3,'like_status':like_status,'no_of_likes':no_of_likes,'no_of_comments':no_of_comments,'comment_status':comment_status, })
    # all_like_users = []
    # all_chat_users = []
    # all_his_comment_users = []
    # for like in all_likes:
    #     user = User.query.get_or_404(like.user__id)
    #     all_like_users.append([user.username,user.id,like.post_id])
    # for chat in all_chats:
    #     user = User.query.get_or_404(chat.user_start_id)
    #     all_chat_users.append([user.username,user.id])
    # for comment in all_his_comments:
    #     post = Post.query.get_or_404(comment.post_id)
    #     all_his_comment_users.append([post.author,comment.post__id])

    alerts = Notify.query.filter_by(username = current_user.username).limit(5).all()


    notify = Message.query.filter_by(user_id = current_user.id,seen = "not seen").limit(10).all()

    all_notify = []

    for notification1 in notify:
        notify_user = User.query.get_or_404(notification1.active_user_id)
        check1 = True
        for n_user in range(len(all_notify)):
            if notify_user.username == all_notify[n_user].get('username'):
                all_notify[n_user]['count'] += 1
                all_notify[n_user]['text'] = notification1.text
                check1 = False
        if check1:
            all_notify.append({'username':notify_user.username, 'profile_pic':notify_user.profile_pic, 'text':notification1.text, 'timestamp': notification1.timestamp, 'count':1})

    all_notify_len = Message.query.filter_by(user_id = current_user.id,seen = "not seen").count()
    if all_notify_len > 9:
        all_notify_len = "9+"

    if current_user.is_authenticated:
        
        return render_template('dashboard.html' , title = "Posts", all_tasks = all_tasks, posts_with_like_count = posts_with_like_count, posts = posts, post_form = post_form, time_now = datetime.utcnow(), like_status = "true", all_notify = all_notify, all_notify_len = all_notify_len, alerts = alerts)
    else:
        
        return render_template('dashboard.html' , title = "Posts", all_tasks = all_tasks, posts_with_like_count = posts_with_like_count, posts = posts, post_form = post_form, time_now = datetime.utcnow(), like_status = "true")


@main.route("/table", methods = ['GET','POST'])
def users_table():
    page_no = request.args.get('page',1,type = int)
    school_users = User.query.filter(User.school.ilike(current_user.school)).filter(User.user_type!="school").paginate(page = page_no,per_page = 10)
    school_users_count = User.query.filter(User.school.ilike(current_user.school)).filter(User.user_type!="school").count()
    all_school_users = []
    for user1 in school_users.items:
        post_count = Post.query.filter_by(user_id = current_user.id).count()
        all_school_users.append({"username":user1.username, "profile_pic":user1.profile_pic,"country":user1.country,"user_type":user1.user_type,"email":user1.email,"dob":user1.dob,"post_count":post_count})

    alerts = Notify.query.filter_by(username = current_user.username).limit(5).all()


    notify = Message.query.filter_by(user_id = current_user.id,seen = "not seen").limit(10).all()

    all_notify = []

    for notification1 in notify:
        notify_user = User.query.get_or_404(notification1.active_user_id)
        check1 = True
        for n_user in range(len(all_notify)):
            if notify_user.username == all_notify[n_user].get('username'):
                all_notify[n_user]['count'] += 1
                all_notify[n_user]['text'] = notification1.text
                check1 = False
        if check1:
            all_notify.append({'username':notify_user.username, 'profile_pic':notify_user.profile_pic, 'text':notification1.text, 'timestamp': notification1.timestamp, 'count':1})

    all_notify_len = Message.query.filter_by(user_id = current_user.id,seen = "not seen").count()
    if all_notify_len > 9:
        all_notify_len = "9+"

    return render_template('table.html',all_school_users = all_school_users, school_users = school_users, school_users_count = school_users_count, all_notify = all_notify, all_notify_len = all_notify_len, alerts = alerts)

@main.route("/search_school", methods = ['GET'])
def school_srh():
    page_no = request.args.get('page',1,type = int)
    search_me = '%'+ request.args['data'] +'%'
    school_users = User.query.filter(User.school.ilike(current_user.school)).filter(User.user_type!="school").filter(User.username.ilike(search_me)).paginate(page = page_no,per_page = 10)
    school_users_count = User.query.filter(User.school.ilike(current_user.school)).filter(User.user_type!="school").filter(User.username.ilike(search_me)).count()
    all_school_users = []
    for user1 in school_users.items:
        post_count = Post.query.filter_by(user_id = current_user.id).count()
        all_school_users.append({"username":user1.username, "profile_pic":user1.profile_pic,"country":user1.country,"user_type":user1.user_type,"email":user1.email,"dob":user1.dob,"post_count":post_count})
    return render_template('table_search.html',all_school_users = all_school_users, school_users = school_users, school_users_count = school_users_count)