from flask import (
    current_app,
    url_for,
)
import secrets
from PIL import Image
import os
from sponza_app import mail
from flask_mail import Message
from celery import shared_task


def del_save_image(profile_pic, file, role):
    pic_filename = secrets.token_hex(8) + ".png"
    path = os.path.join(current_app.root_path, f"static/{role}/images/profile_pics")
    if os.path.exists(os.path.join(path, file)) and file != f"{role}.png":
        os.remove(os.path.join(path, file))
    image = Image.open(profile_pic)
    image.thumbnail((200, 200))
    image.save(os.path.join(path, pic_filename))
    return pic_filename


def return_profile_image(profile_image):
    image_file = f"influencer/images/profile_pics/{profile_image}"
    image_path = os.path.join(current_app.root_path, "static", image_file)
    if not os.path.exists(image_path):
        image_file = "influencer/images/profile_pics/influencer.png"
    return url_for("static", filename=image_file)


def return_campaign_image(image):
    image_file = f"sponsor/images/campaigns/{image}"
    image_path = os.path.join(current_app.root_path, "static", image_file)
    if not os.path.exists(image_path):
        image_file = "sponsor/images/campaigns/campaign.png"
    return url_for("static", filename=image_file)


def del_inf_image(image):
    image_file = f"influencer/images/profile_pics/{image}"
    image_path = os.path.join(current_app.root_path, "static", image_file)
    if os.path.exists(image_path) and image != "influencer.png":
        os.remove(image_path)

@shared_task()
def send_negotiate_mail(email, role, inf_name, camp_name, amt):
    msg = Message(
        "Salary Negotiation Request",
        sender="admin@gmail.com",
        recipients=[email],
    )
    msg.body = f"""Subject: Salary Negotiation Request - Action Required

Dear {role},

We are reaching out to inform you that {inf_name} has proposed a new salary of {amt} for their participation in the campaign "{camp_name}". 

Please review this request and respond at your earliest convenience. You can either approve the proposed salary or suggest further changes. 

Prompt action is requested to ensure smooth progress for the campaign. If you have any questions or need assistance, please do not hesitate to contact our team.

Thank you for your attention to this matter.

Best regards,
Sponza
"""
    mail.send(msg)
    return f"Negotiate mail has been sent to {email}"
       

def remainder_influencer_request_nos(user, request_nos):
    msg = Message(
        "Pending Ad Requests",
        sender="admin@gmail.com",
        recipients=[user.email],
    )
    msg.body = f"""Subject: Friendly Reminder: Pending Ad Requests Awaiting Your Attention

Dear Influencer,

We noticed you haven’t checked in on your ad requests recently. Currently, you have {request_nos} ad requests left unnoticed or pending.

Take a moment to review them and make sure you don’t miss any exciting opportunities.

We encourage you to act promptly to maintain engagement with your advertisers.

If you have any questions or need assistance, feel free to reach out to us anytime.

Best regards,
Sponza
"""
    mail.send(msg)
