import smtplib
import ssl
from email.message import EmailMessage
from flask import Blueprint, request, jsonify
import secrets
from python.config import admin_db
import sys
sys.stdout.reconfigure(encoding='utf-8')

def send_password_reset_email_admin(receiver_email, reset_link):
    sender_email = "cecbuspass@gmail.com"  
    sender_password = "khwo tlex uwdk vaky"

    if not sender_email or not sender_password:
        print("Error: Email credentials not set.")
        return False

    subject = "Admin Password Reset Request"
    body = f"""
    <html>
        <body>
            <div style="text-align: left;">
                <p>Dear Admin,</p>
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
        print(f"✅ Admin password reset email sent successfully to {receiver_email}!")
        return True
    except Exception as e:
        print(f"❌ Error sending admin password reset email: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

send_email_admin_bp = Blueprint("send_email_admin", __name__)

@send_email_admin_bp.route("/send-email-admin", methods=["POST"])
def send_reset_email_admin():
    data = request.get_json()
    staff_id = data.get("staff_id")

    if not staff_id:
        return jsonify({"message": "❌ Staff ID is required."}), 400

    admin = admin_db.admin_signups.find_one({"staff_id": staff_id})
    if not admin:
        return jsonify({"message": "❌ Admin not found."}), 400

    reset_token = secrets.token_urlsafe(32)

    # Store token in password_resets collection with staff_id
    admin_db.password_resets.insert_one({
        "token": reset_token,
        "staff_id": staff_id
    })

    # Construct reset link
    reset_link = f"http://127.0.0.1:5000/reset-password-admin?token={reset_token}"

    # Send email 
    email = "cecbuspass@gmail.com"  # Hardcoded admin email or fetch from admin record

    if send_password_reset_email_admin(email, reset_link):
        return jsonify({"message": "✅ Password reset link sent successfully!"}), 200
    else:
        return jsonify({"message": "❌ Failed to send reset email."}), 500