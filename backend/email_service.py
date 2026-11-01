from flask_mail import Message
from extensions import mail

def send_otp_email(email, otp):

    msg = Message(
        subject="AgriVisionAI Login OTP",
        recipients=[email]
    )

    msg.body = f"""

Your AgriVisionAI OTP is:

{otp}

This OTP is valid for 5 minutes.

"""

    mail.send(msg)