from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, render_template
import secrets
import hashlib
import traceback
from python.db import get_db, get_admin_db
from python.send_email import send_password_reset_email
from python.send_email_admin import send_password_reset_email_admin

email_bp = Blueprint('email', __name__)

# Configurable reset token settings
MAX_ACTIVE_TOKENS = 3  # Maximum number of active reset tokens per email
TOKEN_EXPIRY_HOURS = 1  # Token expires after 1 hour

# 🔹 Student Password Reset Routes
@email_bp.route("/send-email", methods=["POST"])
def send_email():
    try:
        data = request.json
        email = data.get("email")

        db = get_db()
        user = db.student_signups.find_one({"email": email})
        if not user:
            return jsonify({"message": "❌ Email not registered."}), 400

        # Check and manage existing tokens
        existing_tokens = list(db.password_resets.find({
            "email": email, 
            "used": False, 
            "created_at": {"$gte": datetime.utcnow() - timedelta(hours=TOKEN_EXPIRY_HOURS)}
        }))

        # Remove expired tokens
        db.password_resets.delete_many({
            "email": email, 
            "$or": [
                {"used": True},
                {"created_at": {"$lt": datetime.utcnow() - timedelta(hours=TOKEN_EXPIRY_HOURS)}}
            ]
        })

        # Check if max token limit is reached
        if len(existing_tokens) >= MAX_ACTIVE_TOKENS:
            return jsonify({
                "message": f"❌ Maximum {MAX_ACTIVE_TOKENS} active reset tokens allowed. Please wait before requesting again."
            }), 429

        reset_token = secrets.token_urlsafe(32)

        db.password_resets.insert_one({
            "email": email,
            "token": reset_token,
            "used": False,
            "created_at": datetime.utcnow()
        })

        reset_link = f"http://localhost:5000/reset-password?token={reset_token}"

        if send_password_reset_email(email, reset_link):
            return jsonify({
                "message": "✅ Reset link sent successfully!", 
                "active_tokens": len(existing_tokens) + 1,
                "max_tokens": MAX_ACTIVE_TOKENS
            }), 200
        else:
            return jsonify({"message": "❌ Failed to send email."}), 500
    except Exception as e:
        traceback.print_exc()
        return jsonify({"message": f"❌ Server error: {str(e)}"}), 500


@email_bp.route("/reset-password", methods=["GET"])
def reset_password():
    token = request.args.get("token")
    db = get_db()

    token_entry = db.password_resets.find_one({"token": token, "used": False})
    if not token_entry:
        return "Invalid or expired token.", 400

    return render_template("reset_password.html", token=token)


@email_bp.route("/update-password", methods=["POST"])
def update_password():
    try:
        data = request.json
        token = data.get("token")
        new_password = data.get("new_password")

        db = get_db()
        token_entry = db.password_resets.find_one({"token": token, "used": False})
        if not token_entry:
            return jsonify({"message": "❌ You can only submit once."}), 400

        email = token_entry["email"]
        hashed_password = hashlib.sha256(new_password.encode()).hexdigest()

        result = db.student_signups.update_one({"email": email}, {"$set": {"password": hashed_password}})
        if result.modified_count == 0:
            return jsonify({"message": "❌ Password update failed."}), 400

        # ✅ Instead of deleting the token, mark it as used
        db.password_resets.update_one({"token": token}, {"$set": {"used": True, "used_at": datetime.utcnow()}})

        return jsonify({"message": "✅ Password updated successfully!"}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"message": f"❌ Server error: {str(e)}"}), 500


# 🔹 Admin Password Reset Routes
@email_bp.route("/send-email-admin", methods=["POST"])
def send_email_admin():
    try:
        data = request.json
        staff_id = data.get("staff_id")

        admin_db = get_admin_db()
        admin = admin_db.admin_signups.find_one({"staff_id": staff_id})
        if not admin:
            return jsonify({"message": "❌ Staff ID not registered."}), 400

        # Check and manage existing tokens
        existing_tokens = list(admin_db.password_resets.find({
            "staff_id": staff_id, 
            "used": False, 
            "created_at": {"$gte": datetime.utcnow() - timedelta(hours=TOKEN_EXPIRY_HOURS)}
        }))

        # Remove expired tokens
        admin_db.password_resets.delete_many({
            "staff_id": staff_id, 
            "$or": [
                {"used": True},
                {"created_at": {"$lt": datetime.utcnow() - timedelta(hours=TOKEN_EXPIRY_HOURS)}}
            ]
        })

        # Check if max token limit is reached
        if len(existing_tokens) >= MAX_ACTIVE_TOKENS:
            return jsonify({
                "message": f"❌ Maximum {MAX_ACTIVE_TOKENS} active reset tokens allowed. Please wait before requesting again."
            }), 429

        reset_token = secrets.token_urlsafe(32)

        # Store token with staff_id instead of email
        admin_db.password_resets.insert_one({
            "staff_id": staff_id,
            "token": reset_token,
            "used": False,
            "created_at": datetime.utcnow()
        })

        reset_link = f"http://localhost:5000/reset-password-admin?token={reset_token}"

        # Use the admin's email or a predefined admin email
        admin_email = "cecbuspass@gmail.com"  # You might want to store this in admin record

        if send_password_reset_email_admin(admin_email, reset_link):
            return jsonify({
                "message": "✅ Admin reset link sent successfully!", 
                "active_tokens": len(existing_tokens) + 1,
                "max_tokens": MAX_ACTIVE_TOKENS
            }), 200
        else:
            return jsonify({"message": "❌ Failed to send admin email."}), 500
    except Exception as e:
        traceback.print_exc()
        return jsonify({"message": f"❌ Server error: {str(e)}"}), 500


@email_bp.route("/reset-password-admin", methods=["GET"])
def reset_password_admin():
    token = request.args.get("token")
    admin_db = get_admin_db()

    token_entry = admin_db.password_resets.find_one({"token": token, "used": False})
    if not token_entry:
        return "Invalid or expired token.", 400

    return render_template("reset_password_admin.html", token=token)


@email_bp.route("/update-password-admin", methods=["POST"])
def update_password_admin():
    try:
        data = request.json
        token = data.get("token")
        new_password = data.get("new_password")

        admin_db = get_admin_db()
        token_entry = admin_db.password_resets.find_one({"token": token, "used": False})
        if not token_entry:
            return jsonify({"message": "❌ You can only submit once."}), 400

        staff_id = token_entry["staff_id"]
        hashed_password = hashlib.sha256(new_password.encode()).hexdigest()

        result = admin_db.admin_signups.update_one(
            {"staff_id": staff_id},  # ✅ Use staff_id to find the admin
            {"$set": {"password": hashed_password}}
        )
        if result.modified_count == 0:
            return jsonify({"message": "❌ Password update failed."}), 400

        # ✅ Instead of deleting, mark the token as used
        admin_db.password_resets.update_one({"token": token}, {"$set": {"used": True, "used_at": datetime.utcnow()}})

        return jsonify({"message": "✅ Password updated successfully!"}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"message": f"❌ Server error: {str(e)}"}), 500
