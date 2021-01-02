import smtplib,ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PIL import Image, ImageOps
from flask import url_for, current_app, flash
import secrets
from flaskblog import mail
from flaskblog.config import Config
from flask_mail import Message
import os
from datetime import datetime
from pytz import timezone
import base64
import io
# import mimetypes
# from pytz import timezone
# from urlextract import URLExtract


def pretty_date(time=False):
    
    now = datetime.utcnow()
    diff = now - time
    second_diff = diff.seconds
    day_diff = diff.days
    print(diff)

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(round(second_diff)) + " sec ago"
        if second_diff < 120:
            return "a min ago"
        if second_diff < 3600:
            return str(round(second_diff / 60)) + " mins ago"
        if second_diff < 7200:
            return "an hr ago"
        if second_diff < 86400:
            return str(round(second_diff / 3600))+ " hrs ago"
    if day_diff == 1:
        return "yesterday"
    if day_diff < 7:
        return str(round(day_diff)) + " days ago"
    if day_diff < 31:
        return str(round(day_diff / 7)) + " weeks ago"
    if day_diff < 365:
        return str(round(day_diff / 30)) + " months ago"
    return str(round(day_diff / 365)) + " yrs ago"

def create_image_b64str(pic):

    with open(pic, "rb") as image:
        b64string = str(base64.b64encode(image.read()).decode("utf-8"))
    
    return b64string

def img_exists(pic):
    profile_pic_path = os.path.join(current_app.root_path,'static/img', pic)
    return os.path.isfile(profile_pic_path)

def padding(img, expected_size):
    desired_size = expected_size
    delta_width = desired_size - img.size[0]
    delta_height = desired_size - img.size[1]
    pad_width = delta_width // 2
    pad_height = delta_height // 2
    padding = (pad_width, pad_height, delta_width - pad_width, delta_height - pad_height)
    return ImageOps.expand(img, padding)


def resize_with_padding(img, expected_size):
    img.thumbnail((expected_size[0], expected_size[1]))
    # print(img.size)
    delta_width = expected_size[0] - img.size[0]
    delta_height = expected_size[1] - img.size[1]
    pad_width = delta_width // 2
    pad_height = delta_height // 2
    padding = (pad_width, pad_height, delta_width - pad_width, delta_height - pad_height)
    return ImageOps.expand(img, padding)


def resize_img(img1):
    img = Image.open(img1)
    # print(img)
    img = resize_with_padding(img, (1000, 700))
    print(img.size)
    img.save(img1)

def anchorUrl(text):
	
	return text

def remove_profile_pic(pic):
    profile_pic_path = os.path.join(current_app.root_path,'static/img', pic)
    try:
        os.remove(profile_pic_path)
    except FileNotFoundError:
        pass

def add_post_pic(pic):
    name = secrets.token_hex(32)
    NAME,EXT = os.path.splitext(pic.filename)
    # print(EXT,"sdfffffffffffffffffffffffffffffffffffffffffffffffffffff")
    if EXT.lower() == ".gif":
        picture_name = name + EXT
    else:
        picture_name = name + '.webp'
    profile_pic_path = os.path.join(current_app.root_path,'static/img', picture_name)
    if EXT.lower() != ".gif":
        size = (1280,720)
        img1 = Image.open(pic)
        img1.thumbnail(size)
        img1.save(profile_pic_path)
        resize_img(profile_pic_path)
    else:
        pic.save(profile_pic_path)
    return picture_name


def add_message_pic(pic,file_type):
    string_pic = str(pic)
    
    NAME,EXT = os.path.splitext(pic.filename)
    NAME = NAME[:min(len(NAME),8)]
    # name = string_pic[string_pic.find("('")+2:string_pic.find("')")].split('/')[0]+ "ItypesepI" + NAME
    name = file_type + "ItypesepI" + NAME
    
    # if EXT.lower() == ".gif":
    picture_name = name + EXT
    print(picture_name,"sdfffffffffffffffffffffffffffffffffffffffffffffffffffff")
    # else:
    #     picture_name = name + '.webp'
    profile_pic_path = os.path.join(current_app.root_path,'static/img', picture_name)
    # if EXT.lower() != ".gif":
    #     size = (1280,720)
    #     img1 = Image.open(pic)
    #     img1.thumbnail(size)
    #     img1.save(profile_pic_path)
    #     # resize_img(profile_pic_path)
    # else:
    pic.save(profile_pic_path)
    print(picture_name,"sdfffffffffffffffffffffffffffffffffffffffffffffffffffff")
    return picture_name



def add_profile_pic(pic):
    name = secrets.token_hex(16)
    NAME,EXT = os.path.splitext(pic.filename)
    picture_name = name + '.webp'
    profile_pic_path = os.path.join(current_app.root_path,'static/img', picture_name)
    size = (280,280)
    img1 = Image.open(pic)
    img1.thumbnail(size)
    img1.save(profile_pic_path)
    return picture_name

# def send_request_email(user):
#     token = user.get_reset_token()
#     msg = Message('Password Reset Request',
#                   sender='abhixuditxpiyushcompany@gmail.com',
#                   recipients=[user.email])
#     msg.body = f'''To reset your password, visit the following link:
# {url_for('reset_token', token=token, _external=True)}

# If you did not make this request then simply ignore this email and no changes will be made.
# '''
#     mail.send(msg)

def send_post_delete_email(user,post):

    token = user.get_reset_token()
    message = MIMEMultipart("alternative")
    message["Subject"] = "Your post was deleted !"
    message["From"] = "AskNsolve Team <Config.MAIL_USERNAME>"
    message["To"] = user.email

    # Create the plain-text and HTML version of your message
    text = """\
        We, are really sorry to say that one of your post was delete by the admin. Your post should be valid and should contain valid content.
    """
    html = u"""\
    <html>
    <body>
        <h4 style="color: orange;"> We, are really sorry to say that one of your post was delete by the admin. Your post should be valid and should contain valid content.</h4>
        <h4>Your post with title """+str(post.title)+""" was deleted</h4>
        <h3>Code of Conduct that each post shold follow </h3>
        <ul style="list-style-type: circle;">
            <li>Title should be clear and specific</li>
            <li>No abusive lang allowed</li>
            <li>Content should contain clear explaination of the problem written in the title.</li>
        </ul>
        <br><br>
        <p style="color: green;">If you think you made any mistake while posting then don't worry you can again post your question(with proper explaination).</p><br><br>
        <p>Thanks,<br><br>AskNSolve Team</p>
    </body>
    </html>
    """

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
        server.sendmail(
            Config.MAIL_USERNAME, user.email, message.as_string()
        )
    flash("Mail Sent!",'success')

def send_request_email(user):

    token = user.get_reset_token()
    message = MIMEMultipart("alternative")
    message["Subject"] = "Password Reset"
    message["From"] = "AskNsolve Team <Config.MAIL_USERNAME>"
    message["To"] = user.email

    # Create the plain-text and HTML version of your message
    text = """\
        Please ignore if you have not requested Password Reset.
    """
    html = u"""\
    <html>
    <body>
        <p>Hi """+str(user.username)+""",</p>
        <p>You requested to reset the password for your AskNSolve account with the e-mail address <mark style = "background: aqua; color: green;">"""+str(user.email)+"""</mark>.<br>Please click this link to reset your password.</p>
        <a href = '"""+str(url_for('users.request_token', token = token, _external = True))+"""'><h3>PASSWORD RESET</h3></a>
        <br>
        <p>Here, is the link in case Password Reset above is not working</p><br>
        <u>"""+str(url_for('users.request_token', token = token, _external = True))+"""</u><br><br>
        <p>Thanks,<br><br>AskNSolve Team</p>

    </body>
    </html>
    """

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
        server.sendmail(
            Config.MAIL_USERNAME, user.email, message.as_string()
        )

def set_password_request(user):

    token = user.get_reset_token()
    message = MIMEMultipart("alternative")
    message["Subject"] = "Set Password"
    message["From"] = "AskNsolve Team <Config.MAIL_USERNAME>"
    message["To"] = user.email

    # Create the plain-text and HTML version of your message
    text = """\
        Please ignore if you have not requested set your password.
    """
    html = u"""\
    <html>
    <body>
        <p>Hi """+str(user.username)+""",</p>
        <p>You requested to set the password for your AskNSolve account with the e-mail address <mark style = "background: aqua; color: green;">"""+str(user.email)+"""</mark>.<br>Please click this link to reset your password.</p>
        <a href = '"""+str(url_for('users.set_account_password', user_email = user.email, token = token, _external = True))+"""'><h3>SET PASSWORD</h3></a>
        <br>
        <p>Here, is the link in case set Password Button above is not working</p><br>
        <u>"""+str(url_for('users.set_account_password', user_email = user.email, token = token, _external = True))+"""</u><br><br>
        <p>Thanks,<br><br>AskNSolve Team</p>

    </body>
    </html>
    """

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
        server.sendmail(
            Config.MAIL_USERNAME, user.email, message.as_string()
        )

# def send_request_email(user):
#     token = user.get_reset_token()
#     server = smtplib.SMTP('smtp.gmail.com',587)
#     server.ehlo()
#     server.starttls()
#     server.ehlo()

#     server.login(Config.MAIL_USERNAME,'rypktgiqkystabig')

#     subject = 'Reset Your Password'

#     msg = f"Subject: {subject}\n\n\n\n Hi { user.username },\n\n You requested to reset the password for your AskNSolve account with the e-mail address ({ user.email }).\nPlease click this link to reset your password.\n\n {url_for('users.request_token', token = token, _external = True)}\n\nPlease ignore it if you haven't made any request.\n\nThanks,\nAskNSolve Team\n"

#     server.sendmail(
#         'abhixuditxpiyushcompany@gmail.com',
#         user.email,
#         msg
#     )
#     flash('An email has been sent to you to reset your password','success')
#     flash('Link will be active for 15 minutes ','primary')
