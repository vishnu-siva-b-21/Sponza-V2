from sponza_app import mail
from flask_mail import Message


def send_mail(user, token, role):
    msg = Message(
        "Password Reset Request",
        sender="donotreply@gmail.com",
        recipients=[user.email],
    )
    msg.body = f"""To reset your password visit the following link:
http://localhost:3000/user-reset-password?role={role}&token={token}

Note: This Link will expire in 10 mins
If you did not make any changes simply ignore this emailand no chnages will be made
Best regards,
Sponza"""
    mail.send(msg)
