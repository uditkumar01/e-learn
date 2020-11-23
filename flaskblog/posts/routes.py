from flask import Blueprint, request, render_template, redirect, url_for, abort, flash
from flask_login import current_user, login_required
from flaskblog import db
from flaskblog.models import Post,Comment,User,Post_like,Todo,Timeline, Notify,Message
from flaskblog.posts.forms import Post_form, Comment_form
from datetime import datetime
from flaskblog.users.utils import send_post_delete_email,add_post_pic
from datetime import datetime
from pytz import timezone

posts = Blueprint('posts',__name__)



@login_required
@posts.route("/check_like_status/<int:post_id>", methods = ['POST','GET'])
def check_like_status(post_id):
    # post_form = Post_form()
    post = Post.query.get_or_404(post_id)
    
    user_exist = Post_like.query.filter_by(post_id = post_id,user_id = current_user.id).first()
    print(post,user_exist)
    like_status = "false"
    if post and (not user_exist):
        
        like_status = "true"
        
    no_of_likes = len(Post_like.query.filter_by(post_id = post_id).all())

    return {'like_status':like_status,'likes':no_of_likes}



@login_required
@posts.route("/like/<int:post_id>", methods = ['POST','GET'])
def like(post_id):
    # post_form = Post_form()
    post = Post.query.get_or_404(post_id)
    
    user_exist = Post_like.query.filter_by(post_id = post_id,user_id = current_user.id).first()
    print(post,user_exist)
    like_status = "false"
    if post and (not user_exist):
        print("adding")
        like = Post_like(post_id = post_id, user_id = current_user.id)
        db.session.add(like)
        db.session.commit()

        now_utc = datetime.now(timezone('UTC'))
        now_asia = now_utc.astimezone(timezone('Asia/Kolkata'))
        
        if current_user.id != post.author.id:
            notify = Notify(username = post.author.username, title = "like", text = "Someone liked Your Post")
            db.session.add(notify)

        add_time1 = Timeline(username=current_user.username,title="You liked a Post",text=current_user.username+" liked a post named "+post.title+" at "+now_asia.strftime("%I:%M %p"),time_am_pm = now_asia.strftime("%I:%M %p"))
        add_time2 = Timeline(username=post.author.username,title="Someone liked your Post",text=post.author.username+"'s post named "+post.title+" was liked by "+current_user.username+" at "+now_asia.strftime("%I:%M %p"),time_am_pm = now_asia.strftime("%I:%M %p"))
        db.session.add(add_time1)
        db.session.add(add_time2)
        db.session.commit()

        like_status = "true"
    elif post and user_exist:
        print("removing")
        db.session.delete(user_exist)
        db.session.commit()
    no_of_likes = len(Post_like.query.filter_by(post_id = post_id).all())

    return {'like_status':like_status,'likes':no_of_likes}

@login_required
@posts.route("/comment/<int:post_id>", methods = ['POST','GET'])
def comment_post(post_id):
    
    post = Post.query.get_or_404(post_id)
    
    print(post,request.method == "POST", request.form['user_comment'])
    
    if post and request.method == "POST":
        # print("adding")
        comment = Comment(commentor = current_user.username,comment = request.form['user_comment'], post__id = post_id)
        db.session.add(comment)
        db.session.commit()

        if current_user!=post.author:
            now_utc = datetime.now(timezone('UTC'))
            now_asia = now_utc.astimezone(timezone('Asia/Kolkata'))
            
            if current_user.id != post.author.id:
                notify = Notify(username = post.author.username, title = "comment", text = "You got a comment")
                db.session.add(notify)

            add_time1 = Timeline(username=current_user.username,title="You commented a post",text=current_user.username+" commented a post named "+post.title+" at "+now_asia.strftime("%I:%M %p"), time_am_pm = now_asia.strftime("%I:%M %p"))
            add_time2 = Timeline(username=post.author.username,title="You got a new comment",text=post.author.username+"'s post named "+post.title+" got a new comment by "+current_user.username+" at "+now_asia.strftime("%I:%M %p"), time_am_pm = now_asia.strftime("%I:%M %p"))
            db.session.add(add_time1)
            db.session.add(add_time2)
            db.session.commit()
            
    no_of_comments = len(Comment.query.filter_by(post__id = post_id).all())

    return {'comment_status': "done",'comments':no_of_comments}

@login_required
@posts.route("/post/<int:post_id>", methods = ['POST','GET'])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    recent_posts = Post.query.order_by(Post.date_posted.desc()).limit(4).all()
    page_no = request.args.get('page',1,type = int)
    user_exist = Post_like.query.filter_by(post_id = post_id,user_id = current_user.id).first()
    # print(post,user_exist)
    like_status = "false"
    comment_status = "false"
    if user_exist:
        
        like_status = "true"
    user_exist = Comment.query.filter_by(post__id = post_id,commentor = current_user.username).first()
    if user_exist:
        
        comment_status = "true"
        
    no_of_likes = len(Post_like.query.filter_by(post_id = post.id).all())
    comments = Comment.query.order_by(Comment.timestamp.desc()).filter_by(post__id = post.id).paginate(page = page_no,per_page = 4)
    no_of_comments = len(Comment.query.filter_by(post__id = post.id).all())
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

    if current_user.is_authenticated:
        
        return render_template('sep_post.html' , title = "Posts", all_tasks = all_tasks, recent_posts = recent_posts, no_of_likes = no_of_likes,no_of_comments = no_of_comments, post = post, comments = comments, like_status = like_status, comment_status = comment_status, time_now = datetime.utcnow(), _id = post.id, current_page_no = page_no, all_notify = all_notify, all_notify_len = all_notify_len, alerts = alerts)
    else:
        flash("Please login to proceed","info")
        return redirect(url_for('users.login'))
    

@login_required
@posts.route("/show_comments/<int:post_id>", methods = ['POST','GET'])
def show_comments(post_id):
    post = Post.query.get_or_404(post_id)
    page_no = request.args.get('page',1,type = int)
    comments = Comment.query.order_by(Comment.timestamp.desc()).filter_by(post__id = post.id).paginate(page = page_no,per_page = 4)
    return render_template('comments.html', comments = comments,next_page = page_no+1,prev_page = page_no-1, time_now = datetime.utcnow())
# @login_required
# @posts.route("/post_id=<int:post_id>/viewcomments", methods = ['POST','GET'])
# def view_comments(post_id):
#     form = Comment_form()
#     post_id = request.args.get('post_id',1,type = int)
#     page_no = request.args.get('page',1,type = int)
#     _comments = Comment.query.order_by(Comment.timestamp.desc()).filter_by(post__id = post_id).paginate(page = page_no, per_page = 5)
#     user = current_user
#     if current_user.is_authenticated:
#         form.commentor.data = current_user.username
#     if form.validate_on_submit and request.method == 'POST':
#         # flash('Not ommented successfully!!!', 'success')
#         if current_user.username == form.commentor.data:
#             comment = Comment(commentor = form.commentor.data,comment = form.comment.data, post__id = post_id)
#             db.session.add(comment)
#             db.session.commit()
#             flash('Commented successfully!!!', 'success')
#             return redirect(url_for('main.home'))
#         elif current_user.username != form.commentor.data:
#             flash(f'Please don\'t use anyone else\'s username','danger')
#             return  redirect(url_for('main.home'))
#         else:
#             flash(f'Your Comment is not uploaded successfully!','danger')
#     if current_user.is_authenticated:
#         return render_template('comment_page.html', title = "Comments",form = form ,user = user, _comments = _comments, present_time = datetime.utcnow(),username_menu = user.username)
#     else:
#         return redirect(url_for('users.login'))
    
@login_required
@posts.route("/ask/<int:post_id>/update" , methods = ['POST','GET'])
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = Post_form()
    if form.validate_on_submit():
        post.title = form.post_title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your question is updated!','success')
        return redirect(url_for('posts.post', post_id = post.id))
    form.post_title.data = post.title
    form.content.data = post.content
    if current_user.theme == 'NULL':
        return render_template('create_post.html', title = "Update Question", form = form , form_title_webpage = "Edit Question" , button_name = 'Update')
    else:
        return render_template('create_post_dark.html', title = "Update Question", form = form , form_title_webpage = "Edit Question" , button_name = 'Update')

@login_required
@posts.route("/ask/<int:post_id>/delete" , methods = ['POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    post_comments = Comment.query.filter_by(post__id = post_id).all()
    if current_user.username != "ADMIN01":
        if post.author != current_user:
            abort(403)
    for comment in post_comments:
        db.session.delete(comment)
    if current_user.username == "ADMIN01":
        send_post_delete_email(post.author,post)
    db.session.delete(post)
    db.session.commit()
    flash('Your question is deleted successfully!','success')
    return redirect(url_for('main.home'))
