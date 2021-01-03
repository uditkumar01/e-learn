from flask import render_template, flash,redirect,url_for,request, abort, Blueprint
from flaskblog.users.forms import Login_form,Registration_Form, Update_Form, Request_reset_form, Change_password, Registration_Form_School
from flaskblog import db,bcrypt
from flaskblog.models import User, Post ,Comment, Todo, Timeline, Message,Notify
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime, timedelta, date
from flaskblog.users.utils import add_profile_pic, send_request_email, set_password_request, remove_profile_pic,add_post_pic,anchorUrl,add_message_pic, img_exists, pretty_date
from pytz import timezone
from PIL import Image
import base64
import os
import io

users = Blueprint('users',__name__)


@users.route("/register",methods = ['GET','POST'])
def school_register():
    formr = Registration_Form_School()
    # flash(f"register button {formr.signup.data} {formr.validate_on_submit()} | login button {forml.signin.data} {forml.validate_on_submit()}",'info')
    # flash(f"{formr.errors}",'danger')
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    if formr.signup.data and formr.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(formr.password.data).decode('utf-8')
        # print(formr.dob.data)
        # dob = formr.dob.data
        user = User(username = formr.username.data, email = formr.email.data, password = hashed_pw, school = formr.school_name.data , dob = "NONE", country = formr.country.data, gender = "NONE", user_type = "school")
        # if user.email!=None:
        #     set_password_request(user)
        # else:
        #     flash("Please enter valid email")
        db.session.add(user)
        db.session.commit()

        now_utc = datetime.now(timezone('UTC'))
        now_asia = now_utc.astimezone(timezone('Asia/Kolkata'))
        

        add_time = Timeline(username=formr.username.data,title="Registeration Successfull",text=formr.username.data+" registered successfully with "+formr.email.data,time_am_pm = now_asia.strftime("%I:%M %p"))
        db.session.add(add_time)
        db.session.commit()
        flash("{}'s account created successfully!".format(formr.username.data),'success')
        # return render_template('info_pass.html' , title = "Check Mail")
        return redirect(url_for('users.login'))
        
    return render_template('register_school.html', title = "Institution Sign up Page", formr = formr)

@users.route("/login",methods = ['GET','POST'])
def login():
    forml = Login_form()
    formr = Registration_Form()
    # flash(f"register button {formr.signup.data} {formr.validate_on_submit()} | login button {forml.signin.data} {forml.validate_on_submit()}",'info')
    # flash(f"{formr.errors}",'danger')
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    if formr.signup.data and formr.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(formr.password.data).decode('utf-8')
        # print(formr.dob.data)
        # dob = formr.dob.data
        user = User(username = formr.username.data, email = formr.email.data, password = hashed_pw, dob = formr.dob.data, country = formr.country.data, gender = request.form.get('gender'), user_type = request.form.get('type'),school = request.form.get('school'))
        # if user.email!=None:
        #     set_password_request(user)
        # else:
        #     flash("Please enter valid email")
        db.session.add(user)
        db.session.commit()

        now_utc = datetime.now(timezone('UTC'))
        now_asia = now_utc.astimezone(timezone('Asia/Kolkata'))
        

        add_time = Timeline(username=formr.username.data,title="Registeration Successfull",text=formr.username.data+" registered successfully with "+formr.email.data,time_am_pm = now_asia.strftime("%I:%M %p"))
        db.session.add(add_time)
        db.session.commit()
        flash("{}'s account created successfully!".format(formr.username.data),'success')
        # return render_template('info_pass.html' , title = "Check Mail")
        return redirect(url_for('users.login'))

    elif forml.signin.data and forml.validate_on_submit():
        user = User.query.filter_by(email = forml.email.data).first()
        print(user)
        if not user:
            user = User.query.filter_by(username = forml.email.data).first()
        if not user:
            flash("No such user exists.",'info')
        print(user)
        # print(bcrypt.check_password_hash(user.password,forml.password.data),user.password,forml.password.data)
        if user and bcrypt.check_password_hash(user.password,forml.password.data):
            login_user(user, remember=forml.checkbox.data)
            flash("{} logined successfully!".format(user.username),'success')
            user.active = "active"
            db.session.commit()
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        elif user and not bcrypt.check_password_hash(user.password,forml.password.data):
            flash("{}, please check your password!".format(user.username),'danger')
        elif user == None:
            flash("Your E-mail is not registered!",'danger')
    all_schools = User.query.filter_by(user_type="school").all()
    return render_template('login.html' , title = "Login Page", forml = forml, formr = formr,all_schools = all_schools)

@login_required
@users.route("/delete_task", methods = ['GET','POST'])
def delete_todo_task():
    if request.method == "POST":
        print(request.form['data'])
        task_id = int(request.form['data'])
        delete_task = Todo.query.get_or_404(task_id)
        print(delete_task)
        db.session.delete(delete_task)
        db.session.commit()
        day_suffix = "th"
        day = int(delete_task.timestamp.strftime("%d"))
        if 4 <= day <= 20 or 24 <= day <= 30:
            day_suffix = "th"
        else:
            day_suffix = ["st", "nd", "rd"][day % 10 - 1]
        add_time = Timeline(username=delete_task.username,title="Task Done",text=delete_task.username+" completed a task named "+delete_task.task+" which was added on "+delete_task.timestamp.strftime("%d"+day_suffix+" %B %Y"))
        db.session.add(add_time)
        db.session.commit()
    all_tasks = Todo.query.order_by(Todo.timestamp.desc()).filter_by(username = current_user.username).limit(5).all()

    return render_template('todo.html', all_tasks = all_tasks, time_now = datetime.utcnow())

@login_required
@users.route("/todo", methods = ['GET','POST'])
def todo_list():
    
    if request.method == "POST":
        print(request.form['data'],request.method)
        add_task1 = Todo(username = current_user.username, task = request.form['data'])
        db.session.add(add_task1)
        db.session.commit()

        now_utc = datetime.now(timezone('UTC'))
        now_asia = now_utc.astimezone(timezone('Asia/Kolkata'))
        

        add_time = Timeline(username=current_user.username,title="Task Added",text=current_user.username+" added a new task named "+request.form['data']+" at "+now_asia.strftime("%I:%M %p"),time_am_pm = now_asia.strftime("%I:%M %p"))
        db.session.add(add_time)
        db.session.commit()
    all_tasks = Todo.query.order_by(Todo.timestamp.desc()).filter_by(username = current_user.username).limit(5).all()
    if request.method == "GET":
        print(request.args['data'],request.method)
        search_me = '%'+ request.args['data'] +'%'
        all_tasks = Todo.query.filter(Todo.task.ilike(search_me)).limit(5).all()

    return render_template('todo.html', all_tasks = all_tasks, time_now = datetime.utcnow())

@login_required
@users.route("/filter_comments/<int:user_id>", methods = ['GET','POST'])
def filter_comments(user_id):
    user = User.query.get_or_404(user_id)
    recent_comments = Todo.query.order_by(Todo.timestamp.desc()).filter_by(username = user.username).limit(5).all()
    if request.method == "GET":
        print(request.args['data'],request.method)
        search_me = '%'+ request.args['data'] +'%'
        recent_comments = Comment.query.filter(Comment.comment.ilike(search_me)).limit(5).all()

    return render_template('filter_comments.html', recent_comments = recent_comments, time_now = datetime.utcnow())


@users.route("/theme_select", methods = ['GET','POST'])
def theme_select():
    if current_user.theme == 'NULL':
        current_user.theme = 'DARK'
        db.session.commit()
    elif current_user.theme == 'DARK':
        current_user.theme = 'NULL'
        db.session.commit()
    return redirect(url_for('users.account',user_id = current_user.id))

@login_required
@users.route("/followers/<int:user_id>", methods = ['GET'])
def my_followers(user_id):
    followers = Follow.query.filter_by(user_id = user_id).all()
    searched_users = []
    follow_page = True
    for _user in followers:
        searched_users.append(User.query.filter_by(id = _user.current_user_id).first())
    searched_posts = []
    if current_user.theme == "NULL":
        return render_template('search_results.html',follow_page=follow_page, title = current_user.username + "'s followers", searched_users = searched_users, searched_posts = searched_posts)
    else:
        return render_template('search_results_dark.html',follow_page=follow_page, title = current_user.username + "'s followers", searched_users = searched_users, searched_posts = searched_posts)

@login_required
@users.route("/following/<int:user_id>", methods = ['GET'])
def my_following(user_id):
    following = Follow.query.filter_by(current_user_id = user_id).all()
    searched_users = []
    follow_page = True
    for _user in following:
        searched_users.append(User.query.filter_by(id = _user.user_id).first())
    searched_posts = []
    if current_user.theme == "NULL":
        return render_template('search_results.html',follow_page=follow_page, title = current_user.username + "'s following", searched_users = searched_users, searched_posts = searched_posts)
    else:
        return render_template('search_results_dark.html',follow_page=follow_page, title = current_user.username + "'s following", searched_users = searched_users, searched_posts = searched_posts)



@login_required
@users.route("/follow/<int:user_id>", methods = ['GET'])
def follow_me(user_id):
    
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    
    user = User.query.filter_by(id = user_id).first()
    user_check = Follow.query.filter_by(user_id = user_id, current_user_id = current_user.id).first()
    if user and not (user_check):
        follower = Follow(user_id = user_id, current_user_id = current_user.id)
        db.session.add(follower)
        db.session.commit()
        
        flash(f'You are now following {user.username}. You might like {user.username}\'s profile, have a look !!!', 'success')
        return redirect(url_for('users.account',user_id = user_id))
    elif user and user_check:
        db.session.delete(user_check)
        db.session.commit()
        
        flash(f'You have unfollowed {user.username}.', 'info')
        return redirect(url_for('main.home'))
    else:
        return redirect(url_for('main.home'))

    

# @users.route("/register", methods = ['GET','POST'])
# def register():

#     if current_user.is_authenticated:
#         return redirect(url_for('main.home'))
#     formr = Registration_Form()
#     forml = Login_form()
#     flash("Register Route",'info')
#     print(formr.validate_on_submit())
    
#     return render_template('login.html' , title = "Sign Up", forml = forml, formr = formr)

@login_required
@users.route("/update_info" ,methods = ['POST'])
def save_update_info():
    print(request.form,request.args)
    if request.form['fb']:
        current_user.facebook_link = request.form['fb']
    if request.form['insta']:
        current_user.instagram_link = request.form['insta']
    if request.form['gm']:
        current_user.gmail_link = request.form['gm']
    if request.form['tw']:
        current_user.twitter_link = request.form['tw']
    if request.form['fn']:
        current_user.first_name = request.form['fn']
    if request.form['ln']:
        current_user.last_name = request.form['ln']
    db.session.commit()
    # flash('Your Info is updated','success')
    return "DONE"

@login_required
@users.route("/search" ,methods = ['POST'])
def search():
    if not (current_user.is_authenticated):
        return redirect(url_for('users.login'))
    if request.form['search_keyword'] != None:
        search_me = request.form['search_keyword']
        searched_users,searched_posts = [],[]
        if current_user.username == "ADMIN01" and search_me.lower() == "all":
            searched_users = User.query.all()
        else:
            search_me = '%'+ search_me +'%'
            searched_users_1 = User.query.filter(User.username.ilike(search_me)).all()
            searched_users_2 = User.query.filter(User.email.ilike(search_me)).all()
            searched_users = list(set(searched_users_1 + searched_users_2))
            searched_post_1 = Post.query.filter(Post.title.ilike(search_me)).all()
            searched_post_2 = Post.query.filter(Post.content.ilike(search_me)).all()
            searched_posts = list(set(searched_post_1 + searched_post_2))
        if searched_posts:
            flash(f'If you are searching for post then it is suggested to the post\'s author instead.And on his account you can check his posts.','info')
        search_me = search_me[1:-1]
        if current_user.theme == "NULL":
            return render_template('search_results.html',follow_page=False, title = search_me + ' results', searched_users = searched_users, searched_posts = searched_posts)
        else:
            return render_template('search_results_dark.html',follow_page=False, title = search_me + ' results', searched_users = searched_users, searched_posts = searched_posts)

@login_required
@users.route("/account/delete_user/<int:user_id>", methods = ['POST','GET'])
def delete_user(user_id):
    if current_user.username != "ADMIN01":
        flash(f"Only Admin have these permissions")
        return redirect(url_for('users.login'))
    else:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('users.login'))



@login_required
@users.route("/update_pic", methods = ['POST','GET'])
def update_profile_pic():
    if request.method == "POST":
        # print(request.files['pic_1'])
        pic_list = add_profile_pic(request.files['pic_1'])
        current_user.profile_pic = pic_list
        db.session.commit()

        now_utc = datetime.now(timezone('UTC'))
        now_asia = now_utc.astimezone(timezone('Asia/Kolkata'))
        

        add_time = Timeline(username=current_user.username,title="Profile Pic Updated",text=current_user.username+" updated his profile pic at "+now_asia.strftime("%I:%M %p"),time_am_pm = now_asia.strftime("%I:%M %p"))
        db.session.add(add_time)
        db.session.commit()
    return render_template('image.html')

@login_required
@users.route("/search_all", methods = ['GET'])
def search_on_home():
    search_me = '%'+ request.args['data'] +'%'
    all_users1 = User.query.filter(User.username.ilike(search_me)).limit(3).all()
    all_users2 = User.query.filter(User.email.ilike(search_me)).limit(3).all()
    all_posts1 = Post.query.filter(Post.title.ilike(search_me)).limit(3).all()
    all_posts2 = Post.query.filter(Post.content.ilike(search_me)).limit(3).all()
    check_all = "false"
    if all_posts1 or all_posts2 or all_users1 or all_users2:
        check_all = "true"
    return {'page':render_template('home_search.html',all_users = set(all_users1+all_users2),all_posts = set(all_posts1+all_posts2),check_all = check_all, time_now = datetime.utcnow())}

@login_required
@users.route("/account/<string:username>", methods = ['POST','GET'])
def account(username):
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    update_form = Update_Form()
    user = User.query.filter_by(username = username).first()
    
    recent_posts = None
    if user.id != current_user.id:
        recent_posts = Post.query.order_by(Post.date_posted.desc()).filter_by(user_id = user.id).limit(6).all()
    if not user:
        flash('No such user exists...','info')
        return redirect(url_for('users.account',username = current_user.username))
    all_times = Timeline.query.order_by(Timeline.timestamp.desc()).filter_by(username = user.username).limit(10).all()
    recent_comments = Comment.query.order_by(Comment.timestamp.desc()).filter_by(commentor = user.username).limit(5).all()
    all_tasks = Todo.query.order_by(Todo.timestamp.desc()).filter_by(username = current_user.username).limit(5).all()
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
    return render_template('profile.html', recent_posts = recent_posts,user = user,all_times = all_times, update_form = update_form, all_tasks = all_tasks ,time_now=datetime.utcnow(), recent_comments = recent_comments, all_notify = all_notify, all_notify_len = all_notify_len, alerts = alerts)

@login_required
@users.route("/timeline/<int:user_id>", methods = ['POST','GET'])
def timeline_get(user_id):
    user = User.query.get_or_404(user_id)
    if not user:
        flash('No such user exists','info')
        return redirect(url_for('main.home'))
    all_times = Timeline.query.order_by(Timeline.timestamp.desc()).filter_by(username = user.username).limit(10).all()
    return render_template('timeline.html',user = user,all_times = all_times,time_now = datetime.utcnow() )


@login_required
@users.route("/graph/<int:user_id>", methods = ['POST','GET'])
def get_graph(user_id):
    chart_numbers = []
    chart_labels = []
    todo_data = []
    comments_data = []
    user = User.query.get_or_404(user_id)
    for i in range(10):
        after = datetime.utcnow() - timedelta(days=i)
        before = datetime.utcnow() - timedelta(days=(i+1))
        chart_numbers.append(Post.query.order_by(Post.date_posted.desc()).filter_by(user_id = user.id).filter(Post.date_posted <= after).filter(Post.date_posted > before).count())
        todo_data.append(Todo.query.order_by(Todo.timestamp.desc()).filter_by(username = user.username).filter(Todo.timestamp <= after).filter(Todo.timestamp > before).count())
        comments_data.append(Comment.query.order_by(Comment.timestamp.desc()).filter(Comment.commentor == user.username).filter(Comment.timestamp <= after).filter(Comment.timestamp > before).count())
        my_after_date = after.strftime("%dth")
        # chart_labels.append({'day':my_after_date[0],'month':my_after_date[1],'year':my_after_date[2]})
        chart_labels.append(my_after_date)
    print(chart_labels,chart_numbers,todo_data,comments_data)
    
    return {'labels':chart_labels[::-1],'data':chart_numbers[::-1],'todo_data':todo_data[::-1],'comments_data':comments_data[::-1]}


@login_required
@users.route("/user/<string:username>")
def all_user_post(username):
    page_no = request.args.get('page',1,type = int)
    user = User.query.filter_by(username = username).first_or_404()
    _posts = Post.query.order_by(Post.date_posted.desc()).filter_by(user_id = user.id).paginate(page = page_no, per_page = 5)
    if current_user.is_authenticated:
        if current_user.theme == 'NULL':
            return render_template('only_his_post.html' , title = user.username ,posts = _posts, profile_pic = current_user.profile_pic , username_menu = user.username ,present_time = datetime.utcnow(), user = user)
        else:
            return render_template('only_his_post_dark.html' , title = user.username ,posts = _posts, profile_pic = current_user.profile_pic , username_menu = user.username ,present_time = datetime.utcnow(), user = user)
    else:
        redirect(url_for('users.login'))


@users.route("/reset_password", methods = ['GET','POST'])
def request_reset():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = Request_reset_form()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        send_request_email(user)
       
        return redirect(url_for('users.login'))
    
    return render_template('reset_request.html', title = "Request Reset", form = form)


@users.route("/reset_password/<token>", methods = ['GET','POST'])
def request_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user:
        flash('Invalid Token','warning')
    form = Change_password()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_pw
        db.session.commit()
        flash("{}'s password is updated successfully!".format(user.username),'success')
        return redirect(url_for('users.login'))
    return render_template('password_reset.html', title = "Password Reset", form = form, form_name = "Password Reset")

@users.route("/set_password/<user_email>/<token>", methods = ['GET','POST'])
def set_account_password(user_email,token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user == None:
        user = User.query.filter_by(email = user_email).first()
    # print("OOOOOOOOOOOOOOOOOOOOOOOOOO",user,user_email)
    if user == None:
        flash('Invalid Token','warning')
    
    form = Change_password()
    if user and form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_pw
        db.session.commit()
        flash("{}'s password is updated successfully!".format(user.username),'success')
        return redirect(url_for('users.login'))
    return render_template('password_reset.html', title = "Password Reset", form = form, form_name = "Set Password")


@login_required
@users.route("/logout")
def logout():
    current_user.active = "notactive"
    current_user.total_time_spent = datetime.utcnow()
    
    logout_user()
    flash(f'Logout Successfull!','success')
    return redirect(url_for('users.login'))

@users.route("/chat_room/delete_chat/<int:chat_id>/<int:user_id>" , methods = ['GET'])
def chat_del(chat_id,user_id):
    text_1 = Chat.query.get(chat_id)
    if text_1:
        db.session.delete(text_1)
        db.session.commit()
        flash('Deleted !','success')
    return redirect(url_for('users.chat_room',user_id = user_id))



@login_required
@users.route("/contacts_search/<int:id1>" , methods = ['GET'])
def search_contacts(id1):
    # current_user1 = User.query.get_or_404(id1)
    all_users = set()
    
    search_me = '%'+ request.args['data'] +'%'
    all_user1 = User.query.filter(User.username.ilike(search_me)).all()
    all_user2 = User.query.filter(User.first_name.ilike(search_me)).all()
    for user12 in all_user1:
        all_users.add(user12)
    for user12 in all_user2:
        all_users.add(user12)
    return {'page':render_template('contacts.html',all_users = all_users, time_now = datetime.utcnow())}

@login_required
@users.route("/contacts_refresh/<int:user_id>/<int:id1>" , methods = ['GET','POST'])
def get_contacts(user_id,id1):

    user1 = User.query.get_or_404(user_id)
    current_user1 = User.query.get_or_404(id1)
    all_users = []
    all_got_messages1 = Message.query.order_by(Message.timestamp.desc()).filter_by(user_id = current_user1.id).filter(Message.active_user_id != current_user1.id).all()
    all_got_messages2 = Message.query.order_by(Message.timestamp.desc()).filter_by(active_user_id = current_user1.id).filter(Message.user_id != current_user1.id).all()
    
    for chat in all_got_messages1:
        chat_user = User.query.get_or_404(chat.active_user_id)
        check1 = True
        for user12 in all_users:
            if user12.get('username') == chat_user.username:
                check1 = False
                break 
        if check1 and chat_user.id != current_user.id:
            msg_count = Message.query.filter_by(active_user_id = chat_user.id,user_id = current_user1.id,seen="not seen").count()
            all_users.append({ 'username':chat_user.username,'user_type':chat_user.user_type,'text':chat.text,'profile_pic':chat_user.profile_pic,'id':chat_user.id, 'timestamp':chat.timestamp, 'time_diff': pretty_date(chat.timestamp), 'msg_count':msg_count })
    for chat in all_got_messages2:
        chat_user = User.query.get_or_404(chat.user_id)
        check1 = True
        for user12 in range(len(all_users)):
            if all_users[user12].get('username') == chat_user.username and all_users[user12].get('timestamp') < chat.timestamp:
                all_users[user12] = { 'username':chat_user.username,'user_type':chat_user.user_type,'text':chat.text,'profile_pic':chat_user.profile_pic,'id':chat_user.id, 'timestamp':chat.timestamp, 'time_diff': pretty_date(chat.timestamp), 'msg_count': 0 }
                check1 = False
                break
            elif all_users[user12].get('username') == chat_user.username:
                check1 = False
                break
        if check1 and chat_user.id != current_user.id:
            all_users.append({ 'username':chat_user.username,'user_type':chat_user.user_type,'text':chat.text,'profile_pic':chat_user.profile_pic,'id':chat_user.id, 'timestamp':chat.timestamp, 'time_diff': pretty_date(chat.timestamp), 'msg_count':0 })
            print(pretty_date(chat.timestamp))
    all_users.sort(reverse=True, key = lambda x:x.get('timestamp'))

    return {'page':render_template('contacts.html',all_users = all_users,active_user = user1.username, time_now = datetime.utcnow())}


@login_required
@users.route("/contacts_refresh_mini" , methods = ['GET'])
def get_mini_contacts():

    search_me = "%"+request.args['data']+"%"
    all_users = User.query.filter(User.username.ilike(search_me)).all()
    print(search_me,all_users)
    return {'page':render_template('mini_chat_search.html',all_users = all_users,time_now = datetime.utcnow())}

@login_required
@users.route("/notify_refresh" , methods = ['GET'])
def get_notify_ref():
    notify = Message.query.filter_by(user_id = current_user.id,seen = "not seen").limit(10).all()
    
    all_notify = []

    all_notify_len = Message.query.filter_by(user_id = current_user.id,seen = "not seen").count()
    if all_notify_len > 9:
        all_notify_len = "9+"

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

    return {"page":render_template('notifications1.html',all_notify = all_notify,all_notify_len = all_notify_len, time_now = datetime.utcnow())}

@login_required
@users.route("/message_page/<int:user_id>/<int:id1>" , methods = ['GET','POST'])
def chat_room(user_id,id1):
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    if current_user.id != id1:
        return redirect(url_for('users.chat_room',user_id = current_user.id,id1 = current_user.id))
    user = User.query.get_or_404(user_id)
    current_user1 = User.query.get_or_404(id1)
    
    if not user or not current_user:
        return redirect(url_for('main.home'))
    
    
    all_got_messages1 = Message.query.order_by(Message.timestamp.desc()).filter_by(user_id = current_user1.id).filter(Message.active_user_id != current_user1.id).all()
    all_got_messages2 = Message.query.order_by(Message.timestamp.desc()).filter_by(active_user_id = current_user1.id).filter(Message.user_id != current_user1.id).all()
    all_users = []
    
    
    # print(all_my_messages)
    # print(all_recieved_messages)
    for chat in all_got_messages1:
        chat_user = User.query.get_or_404(chat.active_user_id)
        check1 = True
        # print("in loop",chat)
        for user12 in all_users:
            if user12.get('username') == chat_user.username:
                check1 = False
                break 
        if check1:
            # print("in check",chat)
            msg_count = Message.query.filter_by(active_user_id = chat_user.id,user_id = current_user1.id,seen="not seen").count()
            all_users.append({ 'username':chat_user.username,'user_type':chat_user.user_type,'text':chat.text,'profile_pic':chat_user.profile_pic,'id':chat_user.id, 'timestamp':chat.timestamp,'msg_count': msg_count})
            
    for chat in all_got_messages2:
        chat_user = User.query.get_or_404(chat.user_id)
        check1 = True
        for user12 in range(len(all_users)):
            if all_users[user12].get('username') == chat_user.username and all_users[user12].get('timestamp') < chat.timestamp:
                all_users[user12] = { 'username':chat_user.username,'user_type':chat_user.user_type,'text':chat.text,'profile_pic':chat_user.profile_pic,'id':chat_user.id, 'timestamp':chat.timestamp, 'msg_count': 0 }
                check1 = False
                break
            elif all_users[user12].get('username') == chat_user.username:
                check1 = False
                break
        if check1:
            all_users.append({ 'username':chat_user.username,'user_type':chat_user.user_type,'text':chat.text,'profile_pic':chat_user.profile_pic,'id':chat_user.id, 'timestamp':chat.timestamp, 'msg_count': 0 })
    all_users.sort(reverse=True, key = lambda x:x.get('timestamp'))

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

    
    # print("allusers",all_users)
    received_msg_len = Message.query.order_by(Message.timestamp.asc()).filter_by(user_id = current_user.id,active_user_id = user_id).count()
    all_seen_messages_len = Message.query.order_by(Message.timestamp.asc()).filter_by(user_id = user_id,active_user_id = current_user.id, seen = "seen").count()
    return render_template('message_page2.html', all_users = all_users, user = user, time_now = datetime.utcnow(), received_msg_len = received_msg_len, seen_message_len = all_seen_messages_len, all_notify = all_notify, all_notify_len = all_notify_len, alerts = alerts)

@login_required
@users.route("/send_pic/<int:user_id>/<string:msg_text>/<string:file_type>" , methods = ['GET','POST'])
def save_pic(user_id,msg_text,file_type):
    
    # user = User.query.get_or_404(user_id)
    if request.method == "POST":
        
        print(request.files['pic_1'],file_type,"check here #1")
        pic_1 = add_message_pic(request.files['pic_1'],file_type)
        now_utc = datetime.now(timezone('UTC'))
        now_asia = now_utc.astimezone(timezone('Asia/Kolkata'))
        message_text = msg_text
        if msg_text == "None":
            if file_type == "image":
                message_text = '📷 image'
            elif file_type == "audio":
                message_text = '🎵 audio'
            else:
                message_text = '📁 file'
            
            
        message1 = Message(user_id = user_id, active_user_id = current_user.id, text = message_text,pic_1 = pic_1, time_am_pm = now_asia.strftime("%I:%M %p"))
        db.session.add(message1)
        db.session.commit()
    
    
    return "DONE HERE1"



@login_required
@users.route("/chats_refresh/<int:user_id>" , methods = ['GET','POST'])
def get_all_messages(user_id):
    
    user = User.query.get_or_404(user_id)
    print(request.args,request.form)
    if request.method == "POST":
        
        message_text = anchorUrl(request.form['data'])
        
        if message_text == "":
            message_text="None"
        now_utc = datetime.now(timezone('UTC'))
        now_asia = now_utc.astimezone(timezone('Asia/Kolkata'))
        
        message1 = Message(user_id = user_id, active_user_id = current_user.id, text = message_text, time_am_pm = now_asia.strftime("%I:%M %p"))
        db.session.add(message1)
        db.session.commit()
    user = User.query.get_or_404(user_id)
    all_my_messages = Message.query.order_by(Message.timestamp.asc()).filter_by(user_id = user_id,active_user_id = current_user.id).all()
    all_recieved_messages = Message.query.order_by(Message.timestamp.asc()).filter_by(user_id = current_user.id,active_user_id = user_id).all()
    all_messages = []
    # print(len(all_recieved_messages))
    for chat in all_my_messages:
        all_messages.append({'active_user_id':chat.active_user_id, 'text':chat.text,'timestamp': chat.timestamp,'id':chat.id,'time_am_pm': chat.time_am_pm,'user_id': chat.user_id,'seen':chat.seen,'pic_1':chat.pic_1})
    for chat in all_recieved_messages:
        chat.seen = "seen"
        all_messages.append({'active_user_id':chat.active_user_id, 'text':chat.text,'timestamp': chat.timestamp,'id':chat.id,'time_am_pm': chat.time_am_pm,'user_id': chat.user_id,'pic_1':chat.pic_1})
    db.session.commit()
    all_messages.sort(reverse=False, key = lambda x:x.get('timestamp'))
    received_msg_len = len(all_recieved_messages)
    all_seen_messages_len = Message.query.order_by(Message.timestamp.asc()).filter_by(user_id = user_id,active_user_id = current_user.id, seen = "seen").count()
    return render_template('messages2.html',all_messages = all_messages, user =  user,time_now = datetime.utcnow(), received_msg_len = received_msg_len, seen_message_len = all_seen_messages_len)


@users.route("/get_active/<int:user_id>" , methods = ['GET'])
def get_active_user(user_id):
    user = User.query.get_or_404(user_id)
    return {'page':render_template('active_user.html',user = user)}

@users.route("/check_count/<int:user_id>" , methods = ['GET'])
def check_count_msg(user_id):
    all_recieved_messages_len = Message.query.order_by(Message.timestamp.asc()).filter_by(user_id = current_user.id,active_user_id = user_id).count()
    all_seen_messages_len = Message.query.order_by(Message.timestamp.asc()).filter_by(user_id = user_id,active_user_id = current_user.id, seen = "seen").count()
    check_count = "false"
    contacts_refresh_check = "false"
    all_got_messages1 = Message.query.order_by(Message.timestamp.desc()).filter_by(user_id = current_user.id).filter(Message.active_user_id != current_user.id).all()

    for chat in all_got_messages1:
        chat_user = User.query.get_or_404(chat.active_user_id)
        msg_count = Message.query.filter_by(active_user_id = chat_user.id,user_id = current_user.id,seen="not seen").count()
        if msg_count:
            contacts_refresh_check = "true"
            break
            
    
    print(request.args, request.form,"check_count")
    if int(request.args['count']) < all_recieved_messages_len or int(request.args['seen_count']) < all_seen_messages_len:
        check_count = "true"
    return {'count_check':check_count, 'msg_count':all_recieved_messages_len, 'seen_message_count' : all_seen_messages_len, 'contact_check':contacts_refresh_check}

# @users.route("/check_seen/<int:user_id>" , methods = ['GET'])
# def check_seen_msg(user_id):
#     all_recieved_messages = Message.query.order_by(Message.timestamp.asc()).filter_by(user_id = current_user.id,active_user_id = user_id).all()

#     check_count = "false"
#     for message_r in all_recieved_messages:
#         if message_r.seen == "":
#     return {'count_check':check_count, 'msg_count':all_recieved_messages_len}

@users.route("/chat_box/<int:user_id>" , methods = ['GET','POST'])
def get_user_chat(user_id):
    
    user = User.query.get_or_404(user_id)
    
    if request.method == "POST":
        
        message_text = request.form['data']
        if message_text == "":
            message_text="."
        now_utc = datetime.now(timezone('UTC'))
        now_asia = now_utc.astimezone(timezone('Asia/Kolkata'))
        
        
        message1 = Message(user_id = user_id, active_user_id = current_user.id, text = request.form['data'], time_am_pm = now_asia.strftime("%I:%M %p"))
        db.session.add(message1)
        db.session.commit()
    user = User.query.get_or_404(user_id)
    all_my_messages = Message.query.order_by(Message.timestamp.asc()).filter_by(user_id = user_id,active_user_id = current_user.id).all()
    all_recieved_messages = Message.query.order_by(Message.timestamp.asc()).filter_by(user_id = current_user.id,active_user_id = user_id).all()
    received_msg_len = len(all_recieved_messages)
    # print(all_recieved_messages,"chat_box", user_id, current_user.id, received_msg_len)
    all_messages = []
    for chat in all_my_messages:
        
        all_messages.append({'active_user_id':chat.active_user_id, 'text':chat.text,'timestamp': chat.timestamp,'id':chat.id,'time_am_pm': chat.time_am_pm,'user_id': chat.user_id,'seen':chat.seen,'pic_1':chat.pic_1})
    for chat in all_recieved_messages:
        chat.seen = "seen"
        
        all_messages.append({'active_user_id':chat.active_user_id, 'text':chat.text,'timestamp': chat.timestamp,'id':chat.id,'time_am_pm': chat.time_am_pm,'user_id': chat.user_id,'pic_1':chat.pic_1})
    db.session.commit()
    all_messages.sort(reverse=False, key = lambda x:x.get('timestamp'))
    all_seen_messages_len = Message.query.order_by(Message.timestamp.asc()).filter_by(user_id = user_id,active_user_id = current_user.id, seen = "seen").count()

    return {'page':render_template('messages2.html',all_messages = all_messages, user =  user,time_now = datetime.utcnow(), received_msg_len = received_msg_len),'count':received_msg_len,'tw':user.twitter_link,'fb':user.facebook_link,'insta':user.instagram_link, 'seen_message_count' : all_seen_messages_len}


@users.route("/chats/<int:user_id>" , methods = ['GET'])
def all_chats(user_id):
    my_chat = Chat.query.filter_by(user_start_id = user_id, user__id = current_user.id).all()
    his_chat = Chat.query.filter_by(user_start_id = current_user.id, user__id = user_id).all()
    _user = User.query.filter_by(id = user_id).first()
    all_messages = []
    for chat in my_chat:
        all_messages.append([chat.user_start_id, chat.messages, chat.time_of_chat,chat.id, chat.user__id])
    for chat in his_chat:
        all_messages.append([chat.user_start_id, chat.messages, chat.time_of_chat,chat.id, chat.user__id])
    all_messages.sort(reverse=False, key = lambda x:x[2])
    if len(all_messages) > 21:
        for i in all_messages[:11]:
            Chat.query.filter_by(id=i[-1]).delete()
        db.session.commit()
        

    if my_chat != None and his_chat != None:
        if current_user.theme == "NULL":
            return render_template('chats_light.html',title = 'Chat', messages = all_messages ,user_id = user_id, _user = _user)
        else:
            return render_template('chats.html',title = 'Chat', messages = all_messages ,user_id = user_id, _user = _user)
    return redirect(url_for('users.account', user_id = user_id))

    
