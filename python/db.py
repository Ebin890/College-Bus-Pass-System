from python.config import Config  # Ensure correct import
from pymongo import MongoClient
from flask import g

def get_db():
    """Get the student MongoDB database connection."""
    if 'db' not in g:
        # Use Config instead of current_app.config
        mongo_uri = Config.MONGO_URI
        client = MongoClient(mongo_uri)
        g.db = client.get_database()
    return g.db

def get_admin_db():
    """Get the admin MongoDB database connection."""
    if 'admin_db' not in g:
        # Use Config instead of current_app.config
        admin_mongo_uri = Config.ADMIN_MONGO_URI
        client = MongoClient(admin_mongo_uri)
        g.admin_db = client.get_database()
    return g.admin_db

def get_buspass_db():
    """Return the buspass MongoDB database connection."""
    if 'buspass_db' not in g:
        client = MongoClient(Config.BUSPASS_MONGO_URI)
        g.buspass_db = client.get_database()
    return g.buspass_db

def get_payments_collection():
    """Return the payments collection from buspass_db."""
    return get_buspass_db().payments


def close_db(_=None):
    """Close the MongoDB connections."""
    db = g.pop('db', None)
    if db is not None:
        db.client.close()
        
    admin_db = g.pop('admin_db', None)
    if admin_db is not None:
        admin_db.client.close()
        
    buspass_db = g.pop('buspass_db', None)
    if buspass_db is not None:
        buspass_db.client.close()    
    
        