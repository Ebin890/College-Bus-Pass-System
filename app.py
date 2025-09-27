from flask import Flask, send_from_directory
import os
from python.config import Config
from python.db import get_db, get_admin_db
from python.routes import init_routes
from flask_cors import CORS  # Import CORS



# Import the email blueprint
from python.email_blueprint import email_bp

app = Flask(__name__, template_folder='html')
app.config.from_object(Config)
CORS(app)  # Enable CORS for all routes

# Register the email blueprint
app.register_blueprint(email_bp)

# Get the absolute path of the current directory
base_dir = os.path.dirname(os.path.abspath(__file__))

# Define routes for static files
@app.route('/favicon.ico')
def favicon():
    return "", 204  # No Content response

@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory(os.path.join(base_dir, 'css'), filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory(os.path.join(base_dir, 'js'), filename)

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory(os.path.join(base_dir, 'assets'), filename)

# Initialize routes
init_routes(app)


# Create MongoDB indexes when the app starts
with app.app_context():
    try:
        # Student database indexes
        db = get_db()
        db.student_signups.create_index('student_id', unique=True)  
        print("Created unique index on student_id in student_signups collection")
        
        # Create index for email in student_signups for faster password reset lookups
        db.student_signups.create_index('email', unique=True)
        print("Created unique index on email in student_signups collection")
        
        # Create index for tokens in password_resets collection
        db.password_resets.create_index('token', unique=True)
        print("Created unique index on token in password_resets collection")
        db.password_resets.create_index('email', unique=True)
        print("Created unique index on email in password_resets collection")
        
        # Admin database indexes
        admin_db = get_admin_db()
        admin_db.admin_signups.create_index('staff_id', unique=True)  
        print("Created unique index on staff_id in admin_signups collection")
        
        # Ensure admin_logins allows multiple records by creating a compound index
        admin_db.admin_logins.create_index([('staff_id', 1), ('login_time', 1)])  
        print("Created compound index on staff_id and login_time in admin_logins collection")

    except Exception as e:
        print(f"Error creating index: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True)