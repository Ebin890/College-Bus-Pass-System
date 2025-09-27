# payment_email.py
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime
import os
from python.config import Config

def send_payment_confirmation(payment_data):
    """
    Send payment confirmation email to both student and admin.
    
    Args:
        payment_data: Dictionary containing payment details
            - payment_id: Razorpay payment ID
            - amount: Payment amount (in rupees)
            - email: Student's email address
            - payment_date: Date and time of payment
            - status: Payment status
            - student_name: Student's full name
            - student_id: Student's ID
            - bus_no: Bus number
            - boarding_point: Boarding point
    """
    try:
        admin_email = "cecbuspass@gmail.com"
        student_email = payment_data.get("email")
        
        # Format the payment date
        payment_date = payment_data.get("payment_date", datetime.now())
        if isinstance(payment_date, str):
            formatted_date = payment_date
        else:
            formatted_date = payment_date.strftime("%Y-%m-%d %H:%M:%S")
        
        # Path to the Razorpay logo
        logo_path = os.path.join("assets", "razorpay.png")
        
        # Create email HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Payment Confirmation</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #000000;
                    color: #ffffff;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #000000;
                }}
                .header {{
                    background-color: #1a4f8a;
                    padding: 20px;
                    text-align: center;
                }}
                .header img {{
                    max-width: 200px;
                }}
                .success-icon-container {{
                    width: 100%;
                    text-align: center;
                    margin: 30px 0;
                }}
                .success-icon {{
                    width: 80px;
                    height: 80px;
                    border-radius: 50%;
                    background-color: #4CAF50;
                    margin: 0 auto;
                    position: relative;
                    text-align: center;
                    line-height: 80px; 
                }}
                .checkmark {{
                    color: white;
                    font-size: 45px;
                    font-weight: bold;
                    display: inline-block;
                    vertical-align: middle;
                    line-height: normal;
                    margin: 0;
                    padding: 0;
                }}
                .amount {{
                    text-align: center;
                    font-size: 24px;
                    font-weight: bold;
                    margin-bottom: 10px;
                }}
                .success-message {{
                    text-align: center;
                    font-size: 20px;
                    margin-bottom: 30px;
                    color: #ffffff;
                }}
                .payment-details {{
                    border-top: 1px solid #444;
                    padding-top: 20px;
                    margin-bottom: 30px;
                }}
                .detail-row {{
                    display: table;
                    width: 100%;
                    margin-bottom: 15px;
                }}
                .detail-label {{
                    display: table-cell;
                    width: 40%;
                    font-weight: bold;
                    color: #aaa;
                    text-align: left;
                    vertical-align: top;
                }}
                .detail-value {{
                    display: table-cell;
                    width: 60%;
                    text-align: right;
                    vertical-align: top;
                    color: #ffffff;
                }}
                .footer {{
                    text-align: center;
                    color: #aaa;
                    font-size: 12px;
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid #444;
                }}
                hr {{
                    border: none;
                    border-top: 1px solid #444;
                    margin: 30px 0;
                }}
                a {{
                    color: #2b5ebb;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <!-- Use Content-ID embedded image -->
                    <img src="cid:razorpay_logo" alt="Razorpay Logo">
                </div>
                
                <div class="success-icon-container">
                    <div class="success-icon">
                        <span class="checkmark">✓</span>
                    </div>
                </div>
                
                <div class="amount">₹{payment_data.get('amount', '0.0')}</div>
                
                <div class="success-message">Payment Successful</div>
                
                <hr>
                
                <div class="payment-details">
                    <div class="detail-row">
                        <div class="detail-label">Payment Id:</div>
                        <div class="detail-value">{payment_data.get('payment_id', '')}</div>
                    </div>
                    
                    <div class="detail-row">
                        <div class="detail-label">Amount:</div>
                        <div class="detail-value">₹{payment_data.get('amount', '0.0')}</div>
                    </div>
                    
                    <div class="detail-row">
                        <div class="detail-label">Email Id:</div>
                        <div class="detail-value">{student_email}</div>
                    </div>
                    
                    <div class="detail-row">
                        <div class="detail-label">Payment Date:</div>
                        <div class="detail-value">{formatted_date}</div>
                    </div>
                    
                    <div class="detail-row">
                        <div class="detail-label">Status:</div>
                        <div class="detail-value">{payment_data.get('status', 'success')}</div>
                    </div>
                    
                    <div class="detail-row">
                        <div class="detail-label">Student Name:</div>
                        <div class="detail-value">{payment_data.get('student_name', '')}</div>
                    </div>
                    
                    <div class="detail-row">
                        <div class="detail-label">Student ID:</div>
                        <div class="detail-value">{payment_data.get('student_id', '')}</div>
                    </div>
                    
                    <div class="detail-row">
                        <div class="detail-label">Bus Number:</div>
                        <div class="detail-value">{payment_data.get('bus_no', '')}</div>
                    </div>
                    
                    <div class="detail-row">
                        <div class="detail-label">Boarding Point:</div>
                        <div class="detail-value">{payment_data.get('boarding_point', '')}</div>
                    </div>
                </div>
                
                <hr>
                
                <div class="footer">
                    <p>This is an automated message from the CEC Bus Pass System.</p>
                    <p>If you have any questions, please contact the administrator at <a href="mailto:{admin_email}">{admin_email}</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Setup the MIME
        message = MIMEMultipart()
        message['From'] = Config.EMAIL_USERNAME
        message['Subject'] = "CEC Bus Pass Payment Confirmation"
        
        # Attach Razorpay logo as an embedded image
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as img_file:
                img = MIMEImage(img_file.read())
                img.add_header('Content-ID', '<razorpay_logo>')
                img.add_header('Content-Disposition', 'inline', filename='razorpay.png')
                message.attach(img)
        
        # Attach HTML content
        message.attach(MIMEText(html_content, 'html'))
        
        # Connect to the SMTP server
        server = smtplib.SMTP(Config.EMAIL_SERVER, Config.EMAIL_PORT)
        server.starttls()
        server.login(Config.EMAIL_USERNAME, Config.EMAIL_PASSWORD)
        
        # Send email to student
        message['To'] = student_email
        server.send_message(message)
        
        # Send email to admin
        message.replace_header('To', admin_email)
        server.send_message(message)
        
        # Close the connection
        server.quit()
        
        return True, "Emails sent successfully"
    
    except Exception as e:
        print(f"Error sending confirmation email: {str(e)}")
        return False, str(e)