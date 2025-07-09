from flask import (
    current_app,
    url_for,
)
import os
from sponza_app import mail
from flask_mail import Message
from celery import shared_task


def return_sponsor_profile_image(profile_image):
    image_file = f"sponsor/images/profile_pics/{profile_image}"
    image_path = os.path.join(current_app.root_path, "static", image_file)
    if not os.path.exists(image_path):
        image_file = "sponsor/images/profile_pics/sponsor.png"
    return url_for("static", filename=image_file)


def return_inf_profile_image(profile_image):
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

@shared_task()
def send_flag_mail(email, role):
    msg = Message(
        "Flag Warning Mail",
        sender="admin@gmail.com",
        recipients=[email],
    )
    msg.body = f"""Subject: Account Temporarily Disabled - Immediate Action Required

Dear {role},

We hope this message finds you well. We are writing to inform you that your account on our platform has been temporarily disabled because our admin flagged it.
To resolve this issue and restore your account,please reply to this email at your earliest convenience. Our team will assist you with the necessary steps to reactivate your account.

Please be aware that if we do not receive a response from you within 10 days of this email, your account will be permanently deleted, along with all associated data.

We apologize for any inconvenience this may cause and appreciate your prompt attention to this matter.

Best regards
Sponza"""
    mail.send(msg)
    return f"User Flag mail has been sent to {email}"

@shared_task()
def send_camp_flag_mail(email, camp_name):
    msg = Message(
        "Flag Warning Mail",
        sender="admin@gmail.com",
        recipients=[email],
    )
    msg.body = f"""Subject: Campaign Flagged by Admin - Immediate Action Required

Dear Sponsor,

We hope this message finds you well. We are writing to inform you that {camp_name} campaign on our platform has been flagged by our admin team due to some reason. As a result, no further operations can be performed on this campaign until the issue is resolved.

To address this matter and avoid any disruption, please reply to this email at your earliest convenience. Our team will assist you with the necessary steps to resolve the issue.
Please note that if we do not receive a response from you within 5 days of this email, the campaign will be automatically deleted, and all associated data will be permanently lost.

We apologize for any inconvenience this may cause and appreciate your prompt attention to this issue.

Best regards,
Sponza"""
    mail.send(msg)
    return f"Campaign Flag mail has been sent to {email}"

@shared_task()
def send_approve_mail(email, role):
    msg = Message(
        "Account Approval Mail",
        sender="admin@gmail.com",
        recipients=[email],
    )
    msg.body = f"""Subject: Your Account Has Been Approved!

Dear {role},

Dear {role},

We are thrilled to inform you that your account on our platform has been successfully approved! You can now access all the features available to sponsors and start creating impactful campaigns to connect with influencers.

Your dedication and interest in collaborating through our platform are greatly appreciated, and we look forward to supporting your journey.

If you have any questions or need assistance navigating your account, please don't hesitate to reach out to our support team.

Thank you for choosing our platform, and we wish you great success in your sponsorship ventures.

Best regards,  
The Admin Team
"""
    mail.send(msg)
    return f"Sponsor Approve mail has been sent to {email}"

@shared_task()
def send_reject_mail(email, role):
    msg = Message(
        "Account Rejected Mail",
        sender="admin@gmail.com",
        recipients=[email],
    )
    msg.body = f"""Subject: Account Approval Request Rejected

Dear {role},

We regret to inform you that your account approval request on our platform has been rejected by our admin team. After careful consideration, it was determined that your account does not meet the requirements necessary for approval at this time.

If you believe this decision was made in error or would like to discuss the matter further, please feel free to reach out to us by replying to this email. We are happy to provide clarification or guidance on how you might address any concerns.

Thank you for understanding, and we appreciate your interest in joining our platform. We encourage you to review our policies and consider reapplying in the future.

Best regards,  
The Admin Team
"""
    mail.send(msg)
    return f"Sponsor Reject mail has been sent to {email}"

