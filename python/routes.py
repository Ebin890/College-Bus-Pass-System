from flask import jsonify, render_template, request, redirect, url_for, session, flash, render_template_string
from pymongo import MongoClient
import razorpay
from .db import get_db, get_admin_db, close_db, get_buspass_db
from .config import Config
from datetime import datetime
import traceback
import hashlib
from bson import ObjectId, json_util
import base64
import re
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
from email.mime.image import MIMEImage
from jinja2 import Template
import pdfkit
from email.mime.base import MIMEBase
from email import encoders
import pdfkit
import os

# Initialize Razorpay Client
razorpay_client = razorpay.Client(auth=(Config.RAZORPAY_KEY_ID, Config.RAZORPAY_KEY_SECRET))

EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USER = "cecbuspass@gmail.com"
EMAIL_PASSWORD = "khwo tlex uwdk vaky"

# Define maximum capacity for each bus
BUS_CAPACITY = 34

def generate_buspass_pdf(student_data, photo_base64=None):
    """Generate PDF version of the bus pass using inline styles."""
    # Add logo encoding
    logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'logo.jpg')
    logo_base64 = ""
    try:
        with open(logo_path, "rb") as logo_file:
            logo_base64 = base64.b64encode(logo_file.read()).decode("utf-8")
    except Exception as e:
        print(f"Error loading logo: {str(e)}")

    # Fix for background image loading
    background_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'college3.png')
    background_base64 = ""
    try:
        with open(background_path, "rb") as bg_file:
            background_base64 = base64.b64encode(bg_file.read()).decode("utf-8")
    except Exception as e:
        print(f"Error loading background image: {str(e)}")
    
    html_content = render_template_string('''
        <!DOCTYPE html>
    <html>
    <head>
        <style>
            /* Inline CSS to avoid external file dependency */
            body { 
                background: #ffffff;
                padding: 20px 40px;
                font-family: Arial, sans-serif;
                height: 100vh;
                position: relative;
            }
            .container {
                max-width: 700px;
                margin: 0 auto;
                display: flex;
                flex-direction: column;
                height: 100%;
            }
          
          
            .logo-header {
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .logo-header img {
                margin-top:-20px;
                max-width: 800px; /* Kept the original size */
                height: auto;
                text-align: center; /* Added float right for stronger right alignment */
                margin-left: 120px;
            }
            .divider {
                border-top: 2px solid #000;
                width: 200%; /* Changed to 100% to span full width */
                margin-left: -40px; /* Extend beyond the container padding */
                margin-right: -40px; /* Extend beyond the container padding */
            }

            .title {
                text-align: center;
                font-size: 18px;
                font-weight: bold;
                text-transform: uppercase;
                margin: 110px 0;
                text-decoration: underline;
            }
            .bus-pass-section {
                flex-grow: 1;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                margin: 35px 0; /* Add vertical margin to center it */
                padding-top: 0px;
            }
            .bus-pass-card {
                background: url("data:image/png;base64,{{ background_image }}");
                background-size: cover; /* Ensures the image covers the entire container */
                background-position: center; /* Centers the image */
                background-repeat: no-repeat;
                width: 100%;
                max-width: 550px;
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                border: 2px solid #000;
                margin: 0 auto;
                overflow: hidden;
                position: relative; /* Ensure proper stacking in PDF */
            }
            
            .college-name {
                text-align: center;
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 15px;
                color: white;
            }
            .student-info {
                float: left;
                width: 65%;
                color: white;
            }
            .student-info strong {
                color: black;
                font-weight: bold;
            }
            .student-info p {
                margin: 8px 0;
                color: black;
                font-size: 16px;
            }
            .college-name{
                color: black;
            }
            .photo {
                width: 130px;  /* Keep width */
                height: 140px; /* Maintain rectangular shape */
             /* Ensures the image fills the area without distortion */
                border-radius: 15px; 
            }

                        .photo {
                width: 130px;  
                height: 140px; 
                object-fit: cover; /* Ensures the image fills the area without distortion */
                border-radius: 15px; 
            }

            .photo-container {
                float: right;
                width: 130px;  /* Match photo width */
                height: 140px; /* Match photo height */
                text-align: right;
                border-radius: 15px;
                border: 3px solid black;
                display: flex;
                justify-content: center;
                align-items: center;
                margin-top: 30px;
                overflow: hidden; /* Ensures image doesn't overflow */
            }

            .validity {
                font-family: helvetica;
                text-align: center;
                font-size: 15px;
                color: black;
                clear: both;
                font-weight: bold;
                padding-top: 310px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo-header" style="display: block; width: 100%; text-align: center;">
                <img src="data:image/jpeg;base64,{{ logo }}" alt="College Logo" style="max-width: 600px; height: auto; text-align: center;">
                <div style="clear: both;"></div>
            </div>
            <div class="divider"></div>
            
            <div class="title">STUDENT BUS PASS</div>
            
            <div class="bus-pass-section">
                <div class="bus-pass-card">

                    <div class="college-name">College of Engineering Cherthala</div>
                    
                    <div class="student-info">
                        <p><strong>Full Name : </strong> {{ student.full_name }}</p>
                        <p><strong>Student ID : </strong> {{ student.student_id }}</p>
                        <p><strong>Semester : </strong> {{ student.semester }}</p>
                        <p><strong>Gender : </strong> {{ student.gender }}</p>
                        <p><strong>Bus No. : </strong> {{ student.bus_no }}</p>
                        <p><strong>Boarding Point : </strong> {{ student.boarding_point }}</p>
                        <p><strong>Issue Year : </strong> {{ current_year }}</p>
                    </div>
                    
                    {% if photo %}
                    <div class="photo-container">
                        <img class="photo" src="data:image/jpeg;base64,{{ photo }}">
                    </div>
                    {% endif %}
                    
                    <div style="clear: both;"></div>
                </div>
            </div>
            
            <div class="validity">
                This bus pass is valid for the current academic year
            </div>
        </div>
    </body>
    </html>

    ''', 
    student=student_data, 
    photo=photo_base64, 
    current_year=datetime.now().year,
    logo=logo_base64,
    background_image=background_base64)  # Pass the background image base64
    
    # Rest of the function remains the same
    
    options = {
        'page-size': 'A4',
        'encoding': 'UTF-8',
        'quiet': '',
        'margin-top': '15mm',
        'margin-right': '15mm',
        'margin-bottom': '15mm',
        'margin-left': '15mm',
        'enable-local-file-access': '',
        'disable-smart-shrinking': '',
        'no-background': False,  # Important: This ensures backgrounds are printed
        'background': True,
        'print-media-type': False,
        'enable-javascript': True,
        'javascript-delay': 1000  # Give time for gradient to render
    }
    
    try:
        pdf = pdfkit.from_string(html_content, False, options=options)
        return pdf
    except Exception as e:
        print(f"PDF generation error: {str(e)}")
        return None

def send_buspass_email(student_email, student_name, pdf_data):
    """Send email with PDF attachment"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = student_email
        msg['Subject'] = "Your Official College Bus Pass"

        # Email body
        body = f"""
        <html>                   
        <body style="font-family: Arial, sans-serif;margin: 0;">
            <div class="e1" style="max-width: 600px; margin: 0;">
                <p>Dear {student_name},</p>
                <p>Your official college bus pass is attached to this email. Please find the PDF document attached below.</p>
                <p>Do not reply to this automated email.</p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))

        # Attach PDF
        attachment = MIMEBase('application', 'octet-stream')
        attachment.set_payload(pdf_data)
        encoders.encode_base64(attachment)
        attachment.add_header('Content-Disposition', 
                            'attachment', 
                            filename=f"CEC_BusPass_{student_name.replace(' ', '_')}.pdf")
        msg.attach(attachment)

        # Send email
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)
            
    except Exception as e:
        print(f"Error sending bus pass email: {str(e)}")

def init_routes(app):
    # Note: index creation is now handled in app.py
    
    @app.route('/')
    def index():
        """Redirect to login page."""
        return redirect(url_for('login'))
    
    @app.route('/login', methods=['GET'])
    def login():
        """Display login page."""
        # Pass a parameter to control which form is shown
        show_signup = request.args.get('show_signup', 'false') == 'true'
        show_admin_signup = request.args.get('show_admin_signup', 'false') == 'true'
        admin_login = request.args.get('admin_login', 'false') == 'true'  # Add this line
        return render_template('login.html', show_signup=show_signup, show_admin_signup=show_admin_signup, admin_login=admin_login)
    
    @app.route('/student/signup', methods=['POST'])
    def student_signup():
        """Handle student signup."""
        try:
            db = get_db()
            
            # Get form data
            form_data = request.form 
            full_name = form_data.get('full_name')
            student_id = form_data.get('student_id')
            email = form_data.get('email')
            password = form_data.get('password')

            if not student_id or not student_id.startswith('CEC'):
                print(f"Invalid student ID format: {student_id}")
                flash('Invalid Student ID! Use your Registration Number starting with "CEC". ', 'signup_error')
                return redirect(url_for('login', show_signup='true'))
            
            # Hash the password before storing
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            print(f"Attempting signup for student ID: {student_id}")
            
            # Check if student already exists
            existing_student = db.student_signups.find_one({'student_id': student_id})
            if existing_student:
                print(f"Student ID {student_id} already exists")
                flash('Student ID already exists. Please use a different ID.', 'signup_error')
                # Redirect to login page with parameter to show signup form
                return redirect(url_for('login', show_signup='true'))
            
            # Also check if email is already in use
            existing_email = db.student_signups.find_one({'email': email})
            if existing_email:
                print(f"Email {email} already exists")
                flash('Email already exists. Please use a different email.', 'signup_error')
                # Redirect to login page with parameter to show signup form
                return redirect(url_for('login', show_signup='true'))
            
            # Insert into student_signups collection
            try:
                signup_result = db.student_signups.insert_one({
                    'full_name': full_name,
                    'student_id': student_id,
                    'email': email,
                    'password': hashed_password,  # Store hashed password
                    'created_at': datetime.now()
                })
                print(f"Student signup successful. Insert ID: {signup_result.inserted_id}")
                
                # Also create an entry in student_logins collection as a record of account creation
                db.student_logins.insert_one({
                    'student_id': student_id,
                    'action_time': datetime.now(),
                    'status': 'success'
                })
                
                # Automatically log the user in
                session['logged_in'] = True
                session['student_id'] = student_id
                session['full_name'] = full_name
                session['user_type'] = 'student'
                
                # Redirect to homepage instead of login page
                return redirect(url_for('user_home'))
            except Exception as e:
                if "duplicate key error" in str(e).lower():
                    flash('Student ID already exists. Please use a different ID.', 'signup_error')
                else:
                    flash('An error occurred during signup. Please try again.', 'signup_error')
                # Redirect to login page with parameter to show signup form
                return redirect(url_for('login', show_signup='true'))
        except Exception as e:
            print(f"Error during signup: {str(e)}")
            print(traceback.format_exc())
            flash('An error occurred during signup. Please try again.', 'signup_error')
            # Redirect to login page with parameter to show signup form
            return redirect(url_for('login', show_signup='true'))
    
    @app.route('/student/login', methods=['POST'])
    def student_login():
        """Handle student login."""
        try:
            db = get_db()
            
            # Get form data
            form_data = request.form
            student_id = form_data.get('student_id')
            password = form_data.get('password')
            
            # Hash the password to compare with stored hash
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            print(f"Login attempt for student ID: {student_id}")
            
            # Create login record - do this first before any validation
            login_record = {
                'student_id': student_id,
                'login_time': datetime.now(),
                'status': 'attempted'  # Initial status
            }
            
            # Check if student exists and password matches
            student = db.student_signups.find_one({'student_id': student_id})
            print(f"Found student: {student is not None}")
            
            if student and student['password'] == hashed_password:
                print("Password matched. Login successful.")
                
                # Update login status to success
                login_record['status'] = 'success'
                
                # Set session data
                session['logged_in'] = True
                session['student_id'] = student_id
                session['full_name'] = student['full_name']
                session['user_type'] = 'student'
                
                redirect_url = url_for('user_home')
            else:
                print(f"Login failed for student ID: {student_id}")
                # Update login status to failed
                login_record['status'] = 'failed'
                
                flash('Invalid student ID or password.', 'login_error')
                redirect_url = url_for('login')
            
            # Insert login record regardless of success or failure
            print("Inserting login record...")
            result = db.student_logins.insert_one(login_record)
            print(f"Login record inserted. Insert ID: {result.inserted_id}")
            
            return redirect(redirect_url)
            
        except Exception as e:
            print(f"Error during login: {str(e)}")
            print(traceback.format_exc())
            
            # Still try to record the failed login attempt due to error
            try:
                if 'student_id' in locals() and student_id:
                    db = get_db()
                    error_login = {
                        'student_id': student_id,
                        'login_time': datetime.now(),
                        'status': 'error',
                        'error_msg': str(e)[:100]  # Truncate long error messages
                    }
                    db.student_logins.insert_one(error_login)
                    print(f"Error login record inserted for {student_id}")
            except Exception as inner_e:
                print(f"Failed to record login error: {str(inner_e)}")
            
            flash('An error occurred. Please try again.', 'login_error')
            return redirect(url_for('login'))
    
    @app.route('/admin/signup', methods=['POST'])
    def admin_signup():
        """Handle admin signup with auto-set password."""
        try:
            # Use admin database instead of student database
            admin_db = get_admin_db()
            
            # Get form data
            form_data = request.form 
            first_name = form_data.get('first_name')
            last_name = form_data.get('last_name')
            staff_id = form_data.get('staff_id')
            
            # Auto-set the admin password instead of taking it from the form
            password = 'cecbuspass'
            
            # Hash the password before storing
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            print(f"Attempting signup for staff ID: {staff_id}")
            
            # Check if admin already exists
            existing_admin = admin_db.admin_signups.find_one({'staff_id': staff_id})
            if existing_admin:
                print(f"Staff ID {staff_id} already exists")
                flash('Staff ID already exists. Please use a different ID.', 'admin_signup_error')
                # Redirect to login page with parameter to show admin signup form
                return redirect(url_for('login', show_admin_signup='true'))
            
            # Insert into admin_signups collection in admin_db
            try:
                full_name = f"{first_name} {last_name}"
                signup_result = admin_db.admin_signups.insert_one({
                    'first_name': first_name,
                    'last_name': last_name,
                    'full_name': full_name,
                    'staff_id': staff_id,
                    'password': hashed_password,  # Store hashed password
                    'created_at': datetime.now()
                })
                print(f"Admin signup successful. Insert ID: {signup_result.inserted_id}")
                
                # Also create an entry in admin_logins collection as a record of account creation
                admin_db.admin_logins.insert_one({
                    'staff_id': staff_id,
                    'password_used': 'secure_hashed_password',  # Don't store actual password or hash in logs
                    'action_time': datetime.now(),
                    'status': 'success'
                })
                
                # Instead of automatically logging in, flash a success message and redirect to login
                flash('Admin account created successfully. Please log in.', 'signup_success')
                return redirect(url_for('login', admin_login='true'))
            
            except Exception as e:
                if "duplicate key error" in str(e).lower():
                    flash('Staff ID already exists. Please use a different ID.', 'admin_signup_error')
                else:
                    flash('An error occurred during signup. Please try again.', 'admin_signup_error')
                # Redirect to login page with parameter to show admin signup form
                return redirect(url_for('login', show_admin_signup='true'))
        except Exception as e:
            print(f"Error during admin signup: {str(e)}")
            print(traceback.format_exc())
            flash('An error occurred during signup. Please try again.', 'admin_signup_error')
            # Redirect to login page with parameter to show admin signup form
            return redirect(url_for('login', show_admin_signup='true'))
        
        
    @app.route('/admin/login', methods=['POST'])
    def admin_login():
        """Handle admin login."""
        try:
            admin_db = get_admin_db()

            form_data = request.form
            staff_id = form_data.get('staff_id')
            password = form_data.get('password')
            
            # Hash the password to compare with stored hash
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            print(f"Login attempt for staff ID: {staff_id}")

            admin = admin_db.admin_signups.find_one({'staff_id': staff_id})
            print(f"Found admin: {admin is not None}")

            login_record = {
                'staff_id': staff_id,
                'login_time': datetime.now(),  # Ensure uniqueness
            }

            if admin and admin['password'] == hashed_password:
                print("Password matched. Admin login successful.")
                login_record['status'] = 'success'

                # Set session data
                session['logged_in'] = True
                session['staff_id'] = staff_id
                session['full_name'] = admin.get('full_name', f"{admin.get('first_name', '')} {admin.get('last_name', '')}")
                session['user_type'] = 'admin'

                redirect_url = url_for('admin_home')
            else:
                print(f"Login failed for staff ID: {staff_id}")
                login_record['status'] = 'failed'
                flash('Invalid staff ID or password.', 'admin_login_error')
                redirect_url = url_for('login', admin_login = 'true')

            # ✅ Insert login attempt into admin_logins (now allows multiple records)
            admin_db.admin_logins.insert_one(login_record)
            print(f"Admin login attempt recorded: {login_record}")

            return redirect(redirect_url)

        except Exception as e:
            print(f"Error during admin login: {str(e)}")
            print(traceback.format_exc())
            flash('An error occurred. Please try again.', 'admin_login_error')
            return redirect(url_for('login', admin_login='true'))


    
    @app.route('/home')
    def user_home():
        """Display user home page."""
        # Check if user is logged in
        if not session.get('logged_in'):
            print("User not logged in. Redirecting to login page.")
            return redirect(url_for('login'))
        
        # Check user type and redirect accordingly
        if session.get('user_type') == 'admin':
            return redirect(url_for('admin_home'))
            
        # For students or default case
        print(f"User home accessed by student_id: {session.get('student_id')}")
        return render_template('userhome.html', name=session.get('full_name'))
    
    @app.route('/admin/home')
    def admin_home():
        """Display admin home page."""
        # Check if user is logged in and is an admin
        if not session.get('logged_in') or session.get('user_type') != 'admin':
            print("Admin not logged in. Redirecting to login page.")
            return redirect(url_for('login'))
        
        print(f"Admin home accessed by staff_id: {session.get('staff_id')}")
        return render_template('adminhome.html', name=session.get('full_name'))
    
    @app.route('/logout')
    def logout():
        """Handle logout."""
        try:
            if not session.get('logged_in'):
                print("No user logged in. Redirecting to login page.")
                return redirect(url_for('login'))

            user_type = session.get('user_type', 'student')  # Default to student
            
            if user_type == 'admin':
                staff_id = session.get('staff_id')
                if staff_id:
                    admin_db = get_admin_db()
                    print(f"Logging out admin staff ID: {staff_id}")

                    admin_db.admin_logins.insert_one({
                        'staff_id': staff_id,
                        'logout_time': datetime.now(),
                        'status': 'logout'
                    })

            elif user_type == 'student':
                student_id = session.get('student_id')
                if student_id:
                    db = get_db()
                    print(f"Logging out student ID: {student_id}")

                    db.student_logins.insert_one({
                        'student_id': student_id,
                        'logout_time': datetime.now(),
                        'status': 'logout'
                    })

            # Clear session data
            session.clear()
            print("Session cleared. User logged out.")
        except Exception as e:
            print(f"Error during logout: {str(e)}")
            print(traceback.format_exc())
        finally:
            return redirect(url_for('login'))  # Ensure redirection even if an error occurs
        
    @app.route('/forgot-password', methods=['GET'])
    def forgot_password():
        """Render forgot password page."""
        return render_template('index.html')
    
    @app.route('/admin-forgot-password', methods=['GET'])
    def admin_forgot_password():
        return render_template('index2.html')
    
    @app.route('/api/boarding-points/<bus_id>', methods=['GET'])
    def get_boarding_points(bus_id):
        """Fetch boarding points for a specific bus."""
        try:
            # Connect to buses_db
            client = MongoClient(Config.MONGO_URI)
            buses_db = client["buses_db"]
            
            # Map bus_id to the appropriate collection
            collection_map = {
                "Bus 1 (MEC)": "bus_no_1_ernakulam",
                "Bus 2 (Thoppumpady)": "bus_no_2_thoppumpady",
                "Bus 3 (Alappuzha)": "bus_no_3_alappuzha"
            }
            
            if bus_id not in collection_map:
                return jsonify({"error": "Invalid bus ID"}), 400
            
            # Get the boarding points from the appropriate collection
            collection_name = collection_map[bus_id]
            collection = buses_db[collection_name]
            
            # Get all documents in the collection - INCLUDE the _id field
            stops = list(collection.find())
            
            # Convert ObjectId to string for JSON serialization
            for stop in stops:
                stop["_id"] = str(stop["_id"])
            
            return jsonify(stops)
        
        except Exception as e:
            print(f"Error fetching boarding points: {str(e)}")
            return jsonify({"error": "An error occurred"}), 500

    @app.route('/api/bus-capacity/<bus_id>', methods=['GET'])
    def get_bus_capacity(bus_id):
        """Get current capacity and availability for a specific bus."""
        try:
            buspass_db = get_buspass_db()
            
            # Count students registered for this bus with successful payments
            registered_count = buspass_db.bus_registrations.count_documents({
                'bus_no': bus_id,
                'payment_status': 'success'
            })
            
            # Check if bus is available
            is_available = registered_count < BUS_CAPACITY
            
            return jsonify({
                'bus_id': bus_id,
                'registered_students': registered_count,
                'max_capacity': BUS_CAPACITY,
                'available_seats': BUS_CAPACITY - registered_count,
                'is_available': is_available
            })
            
        except Exception as e:
            print(f"Error checking bus capacity: {str(e)}")
            return jsonify({"error": "An error occurred while checking bus capacity"}), 500

    @app.route('/register-bus-student', methods=['POST'])
    def register_bus_student():
        """Handles student registration & starts payment process using auto-generated amount."""
        try:
            if not session.get('logged_in') or session.get('user_type') != 'student':
                return jsonify({"error": "User not logged in"}), 403

            # Get form data
            form_data = request.form
            full_name = form_data.get('fullname')
            student_id = form_data.get('sid')
            semester = form_data.get('semester')
            gender = form_data.get('gender')
            bus_no = form_data.get('bus')
            boarding_point = form_data.get('bp')
            email = form_data.get('eid')
            amount = form_data.get('amount')  

            if not amount or float(amount) <= 0:
                return jsonify({"error": "Invalid amount"}), 400

            # Check if bus has available seats before proceeding
            buspass_db = get_buspass_db()
            
            # Count students registered for this bus with successful payments
            registered_count = buspass_db.bus_registrations.count_documents({
                'bus_no': bus_no,
                'payment_status': 'success',
                'student_id': {'$ne': student_id}  # Exclude current student to handle updates
            })
            
            # Check if bus is full
            if registered_count >= BUS_CAPACITY:
                return jsonify({
                    "error": f"Sorry, this bus is full. Maximum capacity ({BUS_CAPACITY} students) reached."
                }), 400

            amount_paise = int(float(amount) * 100)

            # Handle the image upload
            photo = None
            if 'photo' in request.files:
                photo_file = request.files['photo']
                if photo_file.filename != '':
                    # Convert the image to binary data for MongoDB storage
                    photo = photo_file.read()

            # Check if this student already has a registration
            existing_registration = buspass_db.bus_registrations.find_one({'student_id': student_id})

            # Prepare registration data
            registration = {
                'full_name': full_name,
                'student_id': student_id,
                'semester': semester,
                'gender': gender,
                'bus_no': bus_no,
                'boarding_point': boarding_point,
                'email': email,
                'amount': amount,
                'registration_date': datetime.now(),
                'payment_status': 'pending',  # Initially set to pending, will be updated after payment
            }
            
            # Only update photo if a new one was uploaded
            if photo:
                registration['photo'] = photo
                
            # Insert or update registration details
            if existing_registration:
                # Update existing registration
                result = buspass_db.bus_registrations.update_one(
                    {'student_id': student_id},
                    {'$set': registration}
                )
                registration_id = str(existing_registration['_id'])
                print(f"Updated existing registration for student ID: {student_id}")
            else:
                # Insert new registration
                registration_result = buspass_db.bus_registrations.insert_one(registration)
                registration_id = str(registration_result.inserted_id)
                print(f"Created new registration for student ID: {student_id}")

            # Create Razorpay order
            order_data = {
                "amount": amount_paise,
                "currency": "INR",
                "payment_capture": 1
            }
            order = razorpay_client.order.create(order_data)

            return jsonify({
                "order_id": order["id"], 
                "amount": amount_paise, 
                "email": email,
                "registration_id": registration_id  # Include registration ID for reference
            })

        except Exception as e:
            print(f"Error in register_bus_student: {str(e)}")
            print(traceback.format_exc())
            return jsonify({"error": str(e)}), 500

    # Replace the payment_status route in routes.py with this improved version:
    @app.route("/payment_status", methods=["POST"])
    def payment_status():
        """Verify payment, update MongoDB, send emails, and redirect to user home page."""
        try:
            data = request.json
            payment_id = data.get("payment_id")
            order_id = data.get("order_id")
            signature = data.get("signature")

            if not payment_id:
                return jsonify({"status": "failed", "message": "Missing payment_id"}), 400

            # Fetch payment details from Razorpay
            try:
                payment = razorpay_client.payment.fetch(payment_id)
                payment_status = "success" if payment["status"] == "captured" else "failed"
            except Exception as e:
                print(f"Error fetching payment from Razorpay: {str(e)}")
                return jsonify({"status": "failed", "message": "Payment verification failed"}), 500

            buspass_db = get_buspass_db()

            # Find the student's registration record with pending payment
            student_registration = buspass_db.bus_registrations.find_one({
                "email": payment.get("email", ""),
                "payment_status": "pending"
            })

            if not student_registration:
                print(f"No pending student registration found for email: {payment.get('email', 'unknown')}")
                return jsonify({"status": "failed", "message": "Student registration not found"}), 404

            # If payment was successful, check bus availability again
            if payment_status == "success":
                bus_no = student_registration.get("bus_no")
                
                # Count successful registrations for this bus (excluding this pending one)
                registered_count = buspass_db.bus_registrations.count_documents({
                    'bus_no': bus_no,
                    'payment_status': 'success'
                })
                
                # Check if bus is now full
                if registered_count >= BUS_CAPACITY:
                    # Mark this registration as failed due to capacity
                    buspass_db.bus_registrations.update_one(
                        {"_id": student_registration["_id"]},
                        {"$set": {
                            "payment_status": "refund_needed", 
                            "payment_id": payment["id"], 
                            "payment_date": datetime.now(),
                            "failure_reason": "Bus capacity reached during payment process"
                        }}
                    )
                    
                    # Store payment details with capacity issue flag
                    buspass_db.payments.insert_one({
                        "payment_id": payment["id"],
                        "order_id": order_id,
                        "method": payment.get("method", ""),
                        "amount": payment.get("amount", 0) / 100,
                        "student_email": payment.get("email", ""),
                        "student_id": student_registration.get("student_id", ""),
                        "payment_status": "refund_needed",
                        "payment_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "failure_reason": "Bus capacity reached during payment process"
                    })
                    
                    return jsonify({
                        "status": "failed", 
                        "message": f"Sorry, this bus reached its capacity limit of {BUS_CAPACITY} students during your payment process. Your payment will be refunded.",
                        "redirect_url": url_for('userregister')
                    })

            # Update student's registration status
            buspass_db.bus_registrations.update_one(
                {"_id": student_registration["_id"]},
                {"$set": {"payment_status": payment_status, "payment_id": payment["id"]}}
            )

            # Store payment details in `buspass_db.payments`
            payment_date = datetime.now()
            payment_record = {
                "payment_id": payment["id"],
                "order_id": order_id,
                "method": payment.get("method", ""),
                "amount": payment.get("amount", 0) / 100,
                "student_email": payment.get("email", ""),
                "student_id": student_registration.get("student_id", ""),
                "payment_status": payment_status,
                "payment_date": payment_date.strftime("%Y-%m-%d %H:%M:%S")
            }
            buspass_db.payments.insert_one(payment_record)

            # If payment was successful, send confirmation emails
            if payment_status == "success":
                try:
                    # Import the payment email module
                    from python.payment_email import send_payment_confirmation
                    
                    # Prepare data for email
                    email_data = {
                        "payment_id": payment["id"],
                        "amount": payment.get("amount", 0) / 100,
                        "email": payment.get("email", ""),
                        "payment_date": payment_date,
                        "status": payment_status,
                        "student_name": student_registration.get("full_name", ""),  # Use correct name field
                        "student_id": student_registration.get("student_id", ""),
                        "bus_no": student_registration.get("bus_no", ""),
                        "boarding_point": student_registration.get("boarding_point", "")
                    }
                    
                    # Send confirmation email
                    success, message = send_payment_confirmation(email_data)
                    print(f"Payment Confirmation Email: {message}")

                    photo_base64 = None
                    if 'photo' in student_registration and student_registration['photo']:
                        photo_base64 = base64.b64encode(student_registration['photo']).decode('utf-8')
                    
                    # Generate PDF
                    pdf_data = generate_buspass_pdf(student_registration, photo_base64)
                    
                    if pdf_data:
                        # Send PDF email
                        send_buspass_email(
                            student_email=student_registration['email'],
                            student_name=student_registration['full_name'],
                            pdf_data=pdf_data
                        )
                    else:
                        print("Failed to generate PDF, skipping email attachment")

                except Exception as email_error:
                    print(f"Error sending emails: {str(email_error)}")
                
                return jsonify({"status": "success", "redirect_url": url_for('user_home')})

            return jsonify({"status": "failed", "message": "Payment not captured", "redirect_url": url_for('userregister')})

        except Exception as e:
            print(f"Error processing payment: {str(e)}")
            print(traceback.format_exc())
            return jsonify({"status": "failed", "message": str(e), "redirect_url": url_for('userregister')}), 500
    @app.route('/buspass')
    def buspass():
        """Display student bus pass if payment is successful."""
        # Check if user is logged in
        if not session.get('logged_in'):
            print("User not logged in. Redirecting to login page.")
            return redirect(url_for('login'))
        
        # Check if user is a student
        if session.get('user_type') != 'student':
            print("Admin users cannot view bus passes. Redirecting to admin home.")
            return redirect(url_for('admin_home'))
        
        # Get student ID from session
        student_id = session.get('student_id')
        
        try:
            # Get the bus pass database
            buspass_db = get_buspass_db()
            
            # Find the student's bus registration with successful payment
            student_registration = buspass_db.bus_registrations.find_one({
                'student_id': student_id,
                'payment_status': 'success'
            })
            
            # Get current year for the bus pass
            current_year = datetime.now().year
            
            if not student_registration:
                # No successful registration found
                print(f"No bus pass found for student ID: {student_id}")
                return render_template('buspass.html', has_buspass=False)
            else:
                # Convert ObjectId to string for photo handling
                if '_id' in student_registration:
                    student_registration['_id'] = str(student_registration['_id'])
                
                # Handle photo if it exists
                photo_base64 = None
                if 'photo' in student_registration and student_registration['photo']:
                    import base64
                    photo_base64 = base64.b64encode(student_registration['photo']).decode('utf-8')
                
                # Pass the student data to the template
                return render_template('buspass.html', student=student_registration, photo=photo_base64, has_buspass=True, current_year=current_year)
        
        except Exception as e:
            print(f"Error retrieving bus pass: {str(e)}")
            print(traceback.format_exc())
            flash('An error occurred while retrieving your bus pass. Please try again.', 'error')
            return redirect(url_for('user_home'))
        
    # Add this to your routes.py file inside the init_routes function

    @app.route('/profile')
    def profile():
        """Display user profile edit page."""
        # Check if user is logged in
        if not session.get('logged_in'):
            print("User not logged in. Redirecting to login page.")
            return redirect(url_for('login'))
        
        # Check if user is a student
        if session.get('user_type') != 'student':
            print("Admin users cannot access student profile. Redirecting to admin home.")
            return redirect(url_for('admin_home'))
        
        # Get student ID from session
        student_id = session.get('student_id')
        
        return render_template('editstudent.html')

    @app.route('/get_profile/<student_id>', methods=['GET'])
    def get_profile(student_id):
        """API endpoint to get profile data."""
        try:
            # Validate session to ensure authorized access
            if not session.get('logged_in') or session.get('student_id') != student_id:
                return jsonify({"error": "Unauthorized access"}), 403
                
            db = get_db()
            
            # Find the student's data 
            student = db.student_signups.find_one(
                {'student_id': student_id},
                {'_id': 0, 'password': 0}  # Exclude sensitive fields
            )
            
            if not student:
                return jsonify({"error": "Student not found"}), 404
                
            # Add default values for fields that might not exist in the original signup
            if 'semester' not in student:
                student['semester'] = ""
            if 'phone' not in student:
                student['phone'] = ""
                
            return jsonify(student)
            
        except Exception as e:
            print(f"Error fetching profile: {str(e)}")
            return jsonify({"error": str(e)}), 500
        
    # Add this to your routes.py inside the init_routes function

    @app.route('/get_current_user', methods=['GET'])
    def get_current_user():
        """Get current logged in user info."""
        if not session.get('logged_in'):
            return jsonify({"error": "Not logged in"}), 401
            
        user_type = session.get('user_type')
        
        if user_type == 'student':
            return jsonify({
                "user_type": user_type,
                "student_id": session.get('student_id'),
                "full_name": session.get('full_name')
            })
        elif user_type == 'admin':
            return jsonify({
                "user_type": user_type,
                "staff_id": session.get('staff_id'),
                "full_name": session.get('full_name')
            })
        else:
            return jsonify({"error": "Unknown user type"}), 400

    @app.route('/update_profile', methods=['POST'])
    def update_profile():
        """API endpoint to update profile data."""
        try:
            # Get JSON data
            data = request.json
            student_id = data.get('student_id')
            
            # Validate session to ensure authorized access
            if not session.get('logged_in') or session.get('student_id') != student_id:
                return jsonify({"error": "Unauthorized access"}), 403
            
            # Validate required fields
            if not student_id:
                return jsonify({"error": "Student ID is required"}), 400
            
            db = get_db()
            
            # Check if student exists
            existing_student = db.student_signups.find_one({'student_id': student_id})
            if not existing_student:
                return jsonify({"error": "Student not found"}), 404
            
            # Extract fields to update
            update_data = {
                'full_name': data.get('name'),  # Field name conversion: 'name' in form to 'full_name' in DB
                'email': data.get('email'),
                'semester': data.get('semester'),
                'gender': data.get('gender')
            }
            
            # Update the student in the database
            result = db.student_signups.update_one(
                {'student_id': student_id}, 
                {'$set': update_data}
            )
            
            if result.matched_count:
                # Also update the session with the new name if it was changed
                if session.get('full_name') != update_data['full_name']:
                    session['full_name'] = update_data['full_name']
                    
                return jsonify({"message": "Profile updated successfully"})
            else:
                return jsonify({"error": "Failed to update profile"}), 500
            
        except Exception as e:
            print(f"Error updating profile: {str(e)}")
            return jsonify({"error": str(e)}), 500  
        
    @app.route('/api/current-student', methods=['GET'])
    def get_current_student():
        """Get current logged in student info for form auto-fill."""
        if not session.get('logged_in') or session.get('user_type') != 'student':
            return jsonify({"error": "Not logged in as student"}), 401
            
        student_id = session.get('student_id')
        if not student_id:
            return jsonify({"error": "No student ID in session"}), 400
            
        try:
            db = get_db()
            
            # Find the student's data 
            student = db.student_signups.find_one(
                {'student_id': student_id},
                {'_id': 0, 'password': 0}  # Exclude sensitive fields
            )
            
            if not student:
                return jsonify({"error": "Student not found"}), 404
                
            return jsonify(student)
            
        except Exception as e:
            print(f"Error fetching student data: {str(e)}")
            return jsonify({"error": str(e)}), 500 
        
    @app.route('/adminmanagestudent')
    def adminmanagestudent():
        if not session.get('logged_in') or session.get('user_type') != 'admin':
            return redirect(url_for('login'))

        try:
            buspass_db = get_buspass_db()
            collection = buspass_db["bus_registrations"]
            documents = list(collection.find().limit(50))
            
            # Process binary photo data to base64
            for doc in documents:
                if 'photo' in doc and doc['photo']:
                    # Check if photo is already a string
                    if isinstance(doc['photo'], str):
                        pass
                    else:
                        # Only encode if it's bytes-like
                        doc['photo'] = base64.b64encode(doc['photo']).decode('utf-8')
            
            # Define the specific column order you want
            desired_column_order = [
                'student_id', 'full_name', 'semester', 'gender', 'bus_no', 
                'boarding_point', 'email', 'amount', 'registration_date', 
                'payment_status', 'payment_id', 'photo'
            ]
            
            # Filter the desired columns that actually exist in the documents
            columns = [col for col in desired_column_order if any(col in doc for doc in documents)]
            
            # Add any columns that exist in the documents but weren't in our predefined list
            extra_columns = sorted(set(key for doc in documents for key in doc.keys() 
                                    if key != '_id' and key not in desired_column_order))
            columns.extend(extra_columns)
            
            documents = json.loads(json_util.dumps(documents))

            return render_template('adminmanagestudent.html', documents=documents, columns=columns)
        except Exception as e:
            print(f"Error fetching bus registrations: {str(e)}")
            traceback.print_exc()
            return render_template('adminmanagestudent.html', documents=[], columns=[])
                
    @app.route('/update-student/<student_id>', methods=['POST'])
    def update_student(student_id):
        if not session.get('logged_in') or session.get('user_type') != 'admin':
            return jsonify({"error": "Unauthorized"}), 403

        try:
            buspass_db = get_buspass_db()
            collection = buspass_db["bus_registrations"]
            data = request.json
            
            # Convert string ID to ObjectId
            object_id = ObjectId(student_id)
            
            # Remove any fields that should not be editable
            if '_id' in data:
                del data['_id']
            
            # Handle photo data if it's present
            if 'photo' in data and data['photo']:
                # Extract the base64 data from the data URI
                if data['photo'].startswith('data:'):
                    # Format: data:image/jpeg;base64,/9j/4AAQSkZJRg...
                    _, encoded = data['photo'].split(',', 1)
                    data['photo'] = base64.b64decode(encoded)
                else:
                    # Assume it's already base64 encoded
                    data['photo'] = base64.b64decode(data['photo'])
            
            # Perform update
            result = collection.update_one({"_id": object_id}, {"$set": data})
            
            if result.matched_count == 0:
                return jsonify({"error": "Student not found"}), 404
                
            return jsonify({
                "message": "Student updated successfully",
                "modifiedCount": result.modified_count
            })
        except Exception as e:
            print(f"Error updating student: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route('/delete-student/<student_id>', methods=['DELETE'])
    def delete_student(student_id):
        if not session.get('logged_in') or session.get('user_type') != 'admin':
            return jsonify({"error": "Unauthorized"}), 403

        try:
            buspass_db = get_buspass_db()
            collection = buspass_db["bus_registrations"]
            collection.delete_one({"_id": ObjectId(student_id)})
            return jsonify({"message": "Student deleted successfully"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    @app.route('/delete-all-students', methods=['DELETE'])
    def delete_all_students():
        if not session.get('logged_in') or session.get('user_type') != 'admin':
            return jsonify({"error": "Unauthorized"}), 403

        try:
            buspass_db = get_buspass_db()
            collection = buspass_db["bus_registrations"]
            
            # Get the count of documents to be deleted
            count = collection.count_documents({})
            
            # Delete all documents
            result = collection.delete_many({})
            
            return jsonify({
                "message": "All students deleted successfully",
                "deletedCount": result.deleted_count
            })
        except Exception as e:
            print(f"Error deleting all students: {str(e)}")
            traceback.print_exc()
            return jsonify({"error": str(e)}), 500

    @app.route('/delete-filtered-students', methods=['POST'])
    def delete_filtered_students():
        if not session.get('logged_in') or session.get('user_type') != 'admin':
            return jsonify({"error": "Unauthorized"}), 403

        try:
            buspass_db = get_buspass_db()
            collection = buspass_db["bus_registrations"]
            
            # Get filter criteria from request
            data = request.json
            student_ids = data.get('studentIds', [])
            filters = data.get('filters', {})
            
            # Build query based on filters
            query = {}
            
            if filters.get('semester'):
                query['semester'] = filters['semester']
            
            if filters.get('busNo'):
                query['bus_no'] = filters['busNo']
            
            # If we have specific IDs, use them (client-side filtering already done)
            if student_ids:
                # Convert string IDs to ObjectId
                object_ids = [ObjectId(id) for id in student_ids]
                query['_id'] = {'$in': object_ids}
            
            # If search term is provided, we'd need to implement server-side search
            # This is complex and better handled by the client-side filtering we already have
            
            # Delete matching documents
            result = collection.delete_many(query)
            
            return jsonify({
                "message": "Filtered students deleted successfully",
                "deletedCount": result.deleted_count
            })
        except Exception as e:
            print(f"Error deleting filtered students: {str(e)}")
            traceback.print_exc()
            return jsonify({"error": str(e)}), 500
        
    @app.route('/send-notification', methods=['POST'])
    def send_notification():
        """Handle sending notification emails to all registered students except Semester 8."""
        # Check if user is logged in as admin
        if not session.get('logged_in') or session.get('user_type') != 'admin':
            return jsonify({"error": "Unauthorized access"}), 403

        try:
            # Get buspass database
            buspass_db = get_buspass_db()
            
            # Fetch all emails from bus_registrations collection excluding Semester 8 students
            # We'll use a query to filter out students with Semester "8" or "Semester 8"
            query = {
            "email": {"$exists": True},
            "semester": {"$nin": ["8", "Semester 8"]}  # Exclude both formats of semester 8
            }
            
            recipients = []
            for doc in buspass_db.bus_registrations.find(query, {"_id": 0, "email": 1}):
                if doc.get("email"):
                    recipients.append(doc["email"])
            
            if not recipients:
                return jsonify({"message": "No recipients found"}), 400

            # Set up email credentials
            EMAIL_ADDRESS = "cecbuspass@gmail.com"
            EMAIL_PASSWORD = "khwo tlex uwdk vaky"

            # Set up the email
            msg = MIMEMultipart()
            msg["From"] = EMAIL_ADDRESS
            msg["Subject"] = "Bus Pass Notification"
            
            # Use BCC instead of To for privacy when sending to multiple recipients
            msg["Bcc"] = ", ".join(recipients)
            
            # Create email body
            body = """
            <html>
            <head>
                <style>
                    body {
                        text-align: left;
                    }
                    .email-content {
                        max-width: 600px;
                        margin: 0;
                        text-align: left;
                    }
                </style>
            </head>
            <body>
                <div class="email-content">
                    <p>Dear Student,</p>
                    <p>This is to inform you that the validity of your <strong>College Bus Pass</strong> has expired. 
                    If you wish to continue availing the bus service, you are required to renew your bus pass by completing 
                    the registration process again before the deadline.</p>
                    <p>Please note that students without a valid bus pass will not be permitted to use the college transport 
                    service beyond the expiry date.</p>
                    <p>Thank you for your prompt attention to this matter.</p>
                    <p><strong>Sincerely,</strong><br>
                    College of Engineering Cherthala</p>
                </div>
            </body>
            </html>
            """

            msg.attach(MIMEText(body, "html"))  # Send as HTML


            # Connect to SMTP server and send email
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.ehlo()  # Extended Hello
                server.starttls()  # Secure connection
                server.ehlo()  # Re-identify ourselves after TLS connection
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                server.send_message(msg)  # Use send_message instead of sendmail

            # Log the activity if needed
            print(f"Admin {session.get('staff_id')} sent notifications to {len(recipients)} recipients")
            
            return jsonify({
                "message": f"Notification emails sent successfully to {len(recipients)} recipients!",
                "count": len(recipients)
            })

        except Exception as e:
            print(f"Error sending notification: {str(e)}")
            return jsonify({"error": f"Error sending notification: {str(e)}"}), 500
        
        
    # Route to add a new boarding point
    @app.route('/api/boarding-points/<bus_id>', methods=['POST'])
    def add_boarding_point(bus_id):
        try:
            # Connect to buses_db
            client = MongoClient(Config.MONGO_URI)
            buses_db = client["buses_db"]
            
            # Map bus_id to the appropriate collection
            collection_map = {
                "Bus 1 (MEC)": "bus_no_1_ernakulam",
                "Bus 2 (Thoppumpady)": "bus_no_2_thoppumpady",
                "Bus 3 (Alappuzha)": "bus_no_3_alappuzha"
            }
            
            if bus_id not in collection_map:
                return jsonify({"error": "Invalid bus ID"}), 400
            
            # Get request data
            data = request.json
            
            # Validate input data
            if not data or 'stop' not in data or 'fare' not in data:
                return jsonify({'error': 'Missing required fields'}), 400
            
            # Create new boarding point
            new_point = {
                'stop': data['stop'],
                'fare': data['fare']
            }
            
            # Insert into the appropriate collection
            collection_name = collection_map[bus_id]
            collection = buses_db[collection_name]
            result = collection.insert_one(new_point)
            
            if result.inserted_id:
                return jsonify({'success': True, 'id': str(result.inserted_id)}), 201
            else:
                return jsonify({'error': 'Failed to add boarding point'}), 500
                
        except Exception as e:
            print(f"Error adding boarding point: {str(e)}")
            return jsonify({"error": "An error occurred"}), 500

    # Route to update a boarding point
    @app.route('/api/boarding-points/<bus_id>/<point_id>', methods=['PUT'])
    def update_boarding_point(bus_id, point_id):
        try:
            # Connect to buses_db
            client = MongoClient(Config.MONGO_URI)
            buses_db = client["buses_db"]
            
            # Map bus_id to the appropriate collection
            collection_map = {
                "Bus 1 (MEC)": "bus_no_1_ernakulam",
                "Bus 2 (Thoppumpady)": "bus_no_2_thoppumpady",
                "Bus 3 (Alappuzha)": "bus_no_3_alappuzha"
            }
            
            if bus_id not in collection_map:
                return jsonify({"error": "Invalid bus ID"}), 400
            
            # Get request data
            data = request.json
            
            # Validate input data
            if not data or ('stop' not in data and 'fare' not in data):
                return jsonify({'error': 'No fields to update'}), 400
            
            # Create update document
            update_data = {}
            if 'stop' in data:
                update_data['stop'] = data['stop']
            if 'fare' in data:
                update_data['fare'] = data['fare']
            
            # Update the boarding point
            collection_name = collection_map[bus_id]
            collection = buses_db[collection_name]
            
            result = collection.update_one(
                {'_id': ObjectId(point_id)},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                return jsonify({'success': True}), 200
            else:
                return jsonify({'error': 'Boarding point not found or no changes made'}), 404
                
        except Exception as e:
            print(f"Error updating boarding point: {str(e)}")
            return jsonify({"error": "An error occurred"}), 500

    # Route to delete a boarding point
    @app.route('/api/boarding-points/<bus_id>/<point_id>', methods=['DELETE'])
    def delete_boarding_point(bus_id, point_id):
        try:
            # Connect to buses_db
            client = MongoClient(Config.MONGO_URI)
            buses_db = client["buses_db"]
            
            # Map bus_id to the appropriate collection
            collection_map = {
                "Bus 1 (MEC)": "bus_no_1_ernakulam",
                "Bus 2 (Thoppumpady)": "bus_no_2_thoppumpady",
                "Bus 3 (Alappuzha)": "bus_no_3_alappuzha"
            }
            
            if bus_id not in collection_map:
                return jsonify({"error": "Invalid bus ID"}), 400
            
            # Delete the boarding point
            collection_name = collection_map[bus_id]
            collection = buses_db[collection_name]
            
            result = collection.delete_one({'_id': ObjectId(point_id)})
            
            if result.deleted_count > 0:
                return jsonify({'success': True}), 200
            else:
                return jsonify({'error': 'Boarding point not found'}), 404
                
        except Exception as e:
            print(f"Error deleting boarding point: {str(e)}")
            return jsonify({"error": "An error occurred"}), 500
        
            
    # Register the close_db function with the app context
    @app.teardown_appcontext
    def teardown_db(exception):
        print("Closing database connection")
        close_db(exception)

    @app.route('/userregister')
    def userregister():
        return render_template('userregister.html')
    
    @app.route('/busdetail')
    def busdetail():
        return render_template('busdetail.html')
    
    @app.route('/adminmanagebus')
    def adminmanagebus():
        return render_template('adminmanagebus.html')
    










