import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key')
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/student_db')
    ADMIN_MONGO_URI = os.environ.get('ADMIN_MONGO_URI', 'mongodb://localhost:27017/admin_db')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'default-admin-password')
    RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
    RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
    SMTP_EMAIL = os.getenv("SMTP_EMAIL")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    BUSPASS_MONGO_URI = os.getenv("BUSPASS_MONGO_URI")
    EMAIL_SERVER = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USERNAME = 'cecbuspass@gmail.com'  # Use your actual email address
    EMAIL_PASSWORD = 'khwo tlex uwdk vaky'


# ✅ Create MongoDB connections
mongo_client = MongoClient(Config.MONGO_URI)
admin_mongo_client = MongoClient(Config.ADMIN_MONGO_URI)

# ✅ Define the databases
student_db = mongo_client["student_db"]
admin_db = admin_mongo_client["admin_db"]
