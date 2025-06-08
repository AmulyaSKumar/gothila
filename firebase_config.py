"""
Minimal Firebase REST API integration
"""
import requests
import json
import time
import os
import firebase_admin
from firebase_admin import credentials, firestore, auth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_firebase_config():
    """Get Firebase configuration from environment variables"""
    return {
        "type": os.getenv('FIREBASE_TYPE', 'service_account'),
        "project_id": os.getenv('FIREBASE_PROJECT_ID'),
        "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
        "private_key": os.getenv('FIREBASE_PRIVATE_KEY').replace('\\n', '\n') if os.getenv('FIREBASE_PRIVATE_KEY') else None,
        "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
        "client_id": os.getenv('FIREBASE_CLIENT_ID'),
        "auth_uri": os.getenv('FIREBASE_AUTH_URI', 'https://accounts.google.com/o/oauth2/auth'),
        "token_uri": os.getenv('FIREBASE_TOKEN_URI', 'https://oauth2.googleapis.com/token'),
        "auth_provider_x509_cert_url": os.getenv('FIREBASE_AUTH_CERT_URL', 'https://www.googleapis.com/oauth2/v1/certs'),
        "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_CERT_URL'),
        "universe_domain": os.getenv('FIREBASE_UNIVERSE_DOMAIN', 'googleapis.com')
    }

def get_firebase_web_config():
    """Get Firebase web configuration from environment variables"""
    return {
        "apiKey": os.getenv('FIREBASE_API_KEY'),
        "authDomain": os.getenv('FIREBASE_AUTH_DOMAIN'),
        "databaseURL": os.getenv('FIREBASE_DATABASE_URL'),
        "projectId": os.getenv('FIREBASE_PROJECT_ID'),
        "storageBucket": os.getenv('FIREBASE_STORAGE_BUCKET'),
        "messagingSenderId": os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
        "appId": os.getenv('FIREBASE_APP_ID'),
        "measurementId": os.getenv('FIREBASE_MEASUREMENT_ID')
    }

# Initialize Firebase Admin SDK with credentials from environment
try:
    # Check if already initialized
    firebase_admin.get_app()
except ValueError:
    # Initialize with credentials from environment
    cred = credentials.Certificate(get_firebase_config())
    firebase_admin.initialize_app(cred)

class FirebaseDB:
    def __init__(self):
        self.db = firestore.client()
    
    def get_data(self, path):
        try:
            doc_ref = self.db.document(path)
            doc = doc_ref.get()
            return {'success': True, 'data': doc.to_dict() if doc.exists else None}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def save_data(self, path, data):
        try:
            doc_ref = self.db.document(path)
            if data is None:
                doc_ref.delete()
            else:
                doc_ref.set(data, merge=True)
            return {'success': True, 'data': data}
        except Exception as e:
            return {'success': False, 'error': str(e)}

# Initialize database instance
db = FirebaseDB()

def initialize_firebase():
    """This function now just verifies the initialization"""
    try:
        firebase_admin.get_app()
        return True
    except ValueError:
        return False