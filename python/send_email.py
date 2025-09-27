import smtplib
import ssl
from email.message import EmailMessage
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Function to Send Password Reset Email
def send_password_reset_email(receiver_email, reset_link):
    sender_email = "cecbuspass@gmail.com"  
    # You may want to consider storing this in an environment variable
    sender_password = "khwo tlex uwdk vaky"

    if not sender_email or not sender_password:
        print("Error: Email credentials not set.")
        return False

    subject = "Password Reset Request"
    body = f"""
    <html>
        <body>
            <div style="text-align: left;">
                <p>Dear Student,</p>
                <p>We received a request to reset your password for the College Bus Pass System.<br> Click the button below to create a new password:</p>
                <a href="{reset_link}" style="display: inline-block; background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                    Reset Password
                </a>
                <p>If you did not request this change, please ignore this email.<br> This link will expire after a certain period for security reasons.</p>
                <p>For any assistance, feel free to contact support.</p>
                <p>Best regards,<br>College of Engineering Cherthala</p>
            </div>
        </body>
    </html>
    """

    msg = EmailMessage()
    msg.set_content("Your email client does not support HTML. Use a modern email client.")
    msg.add_alternative(body, subtype="html")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print(f"✅ Email sent successfully to {receiver_email}!")
        return True
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        print(f"Error type: {type(e).__name__}")  # Added to show the exact error type
        return False

# New generic send_email function to resolve import
def send_email(receiver_email, subject, body):
    sender_email = "cecbuspass@gmail.com"  
    sender_password = "khwo tlex uwdk vaky"

    if not sender_email or not sender_password:
        print("Error: Email credentials not set.")
        return False

    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print(f"✅ Email sent successfully to {receiver_email}!")
        return True
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        print(f"Error type: {type(e).__name__}")  # Added to show the exact error type
        return False