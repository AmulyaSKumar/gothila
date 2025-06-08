from firebase_config import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, user_data=None):
        if user_data is None:
            user_data = {}
        self.id = user_data.get('id')
        self.username = user_data.get('username')
        self.email = user_data.get('email')
        self.full_name = user_data.get('full_name')
        self.phone = user_data.get('phone')
        self.role = user_data.get('role', 'user')
        self.location = user_data.get('location')
        self.password_hash = user_data.get('password_hash')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'role': self.role,
            'location': self.location,
            'password_hash': self.password_hash
        }

    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

class Document:
    def __init__(self, doc_data=None):
        if doc_data is None:
            doc_data = {}
        self.id = doc_data.get('id')
        self.user_id = doc_data.get('user_id')
        self.filename = doc_data.get('filename')
        self.original_filename = doc_data.get('original_filename')
        self.file_path = doc_data.get('file_path')
        self.file_size = doc_data.get('file_size')
        self.file_type = doc_data.get('file_type')
        self.upload_date = doc_data.get('upload_date', datetime.utcnow().isoformat())
        self.processed = doc_data.get('processed', False)
        self.processing_status = doc_data.get('processing_status', 'pending')
        self.extracted_text = doc_data.get('extracted_text')
        self.analysis_results = doc_data.get('analysis_results')
        self.compliance_score = doc_data.get('compliance_score')
        self.issues_found = doc_data.get('issues_found', 0)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'upload_date': self.upload_date,
            'processed': self.processed,
            'processing_status': self.processing_status,
            'extracted_text': self.extracted_text,
            'analysis_results': self.analysis_results,
            'compliance_score': self.compliance_score,
            'issues_found': self.issues_found
        }

class AnalysisResult:
    def __init__(self, result_data=None):
        if result_data is None:
            result_data = {}
        self.id = result_data.get('id')
        self.document_id = result_data.get('document_id')
        self.category = result_data.get('category')
        self.issue_type = result_data.get('issue_type')
        self.severity = result_data.get('severity')
        self.description = result_data.get('description')
        self.suggestion = result_data.get('suggestion')
        self.line_number = result_data.get('line_number')
        self.created_date = result_data.get('created_date', datetime.utcnow().isoformat())

    def to_dict(self):
        return {
            'id': self.id,
            'document_id': self.document_id,
            'category': self.category,
            'issue_type': self.issue_type,
            'severity': self.severity,
            'description': self.description,
            'suggestion': self.suggestion,
            'line_number': self.line_number,
            'created_date': self.created_date
        }

class ChatSession:
    def __init__(self, session_data=None):
        if session_data is None:
            session_data = {}
        self.id = session_data.get('id')
        self.user_id = session_data.get('user_id')
        self.session_id = session_data.get('session_id')
        self.title = session_data.get('title')
        self.created_date = session_data.get('created_date', datetime.utcnow().isoformat())
        self.last_activity = session_data.get('last_activity', datetime.utcnow().isoformat())

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'title': self.title,
            'created_date': self.created_date,
            'last_activity': self.last_activity
        }

class ChatMessage:
    def __init__(self, message_data=None):
        if message_data is None:
            message_data = {}
        self.id = message_data.get('id')
        self.session_id = message_data.get('session_id')
        self.message_type = message_data.get('message_type')
        self.content = message_data.get('content')
        self.timestamp = message_data.get('timestamp', datetime.utcnow().isoformat())

    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'message_type': self.message_type,
            'content': self.content,
            'timestamp': self.timestamp
        }

class LawyerConnection:
    def __init__(self, connection_data=None):
        if connection_data is None:
            connection_data = {}
        self.id = connection_data.get('id')
        self.user_id = connection_data.get('user_id')
        self.lawyer_id = connection_data.get('lawyer_id')
        self.status = connection_data.get('status', 'active')
        self.connection_date = connection_data.get('connection_date', datetime.utcnow().isoformat())
        self.case_description = connection_data.get('case_description')
        self.urgency = connection_data.get('urgency', 'normal')
        self.last_message_date = connection_data.get('last_message_date', datetime.utcnow().isoformat())

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'lawyer_id': self.lawyer_id,
            'status': self.status,
            'connection_date': self.connection_date,
            'case_description': self.case_description,
            'urgency': self.urgency,
            'last_message_date': self.last_message_date
        }

class LawyerMessage:
    def __init__(self, message_data=None):
        if message_data is None:
            message_data = {}
        self.id = message_data.get('id')
        self.connection_id = message_data.get('connection_id')
        self.sender_type = message_data.get('sender_type')
        self.message = message_data.get('message')
        self.timestamp = message_data.get('timestamp', datetime.utcnow().isoformat())
        self.is_read = message_data.get('is_read', False)
        self.attachment_path = message_data.get('attachment_path')

    def to_dict(self):
        return {
            'id': self.id,
            'connection_id': self.connection_id,
            'sender_type': self.sender_type,
            'message': self.message,
            'timestamp': self.timestamp,
            'is_read': self.is_read,
            'attachment_path': self.attachment_path
        }

class LawyerReview:
    def __init__(self, review_data=None):
        if review_data is None:
            review_data = {}
        self.id = review_data.get('id')
        self.lawyer_id = review_data.get('lawyer_id')
        self.user_id = review_data.get('user_id')
        self.rating = review_data.get('rating')
        self.review_text = review_data.get('review_text')
        self.created_date = review_data.get('created_date', datetime.utcnow().isoformat())

    def to_dict(self):
        return {
            'id': self.id,
            'lawyer_id': self.lawyer_id,
            'user_id': self.user_id,
            'rating': self.rating,
            'review_text': self.review_text,
            'created_date': self.created_date
        }

class CaseNote:
    def __init__(self, note_data=None):
        if note_data is None:
            note_data = {}
        self.id = note_data.get('id')
        self.user_id = note_data.get('user_id')
        self.title = note_data.get('title')
        self.content = note_data.get('content')
        self.category = note_data.get('category')
        self.created_date = note_data.get('created_date', datetime.utcnow().isoformat())
        self.updated_date = note_data.get('updated_date', datetime.utcnow().isoformat())
        self.is_private = note_data.get('is_private', True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'created_date': self.created_date,
            'updated_date': self.updated_date,
            'is_private': self.is_private
        }

class LegalForm:
    def __init__(self, form_data=None):
        if form_data is None:
            form_data = {}
        self.id = form_data.get('id')
        self.name = form_data.get('name')
        self.category = form_data.get('category')
        self.description = form_data.get('description')
        self.form_fields = form_data.get('form_fields')
        self.template_content = form_data.get('template_content')
        self.is_active = form_data.get('is_active', True)
        self.created_date = form_data.get('created_date', datetime.utcnow().isoformat())

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'form_fields': self.form_fields,
            'template_content': self.template_content,
            'is_active': self.is_active,
            'created_date': self.created_date
        }

class GeneratedDocument:
    def __init__(self, doc_data=None):
        if doc_data is None:
            doc_data = {}
        self.id = doc_data.get('id')
        self.user_id = doc_data.get('user_id')
        self.form_id = doc_data.get('form_id')
        self.generated_content = doc_data.get('generated_content')
        self.form_data = doc_data.get('form_data')
        self.created_date = doc_data.get('created_date', datetime.utcnow().isoformat())

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'form_id': self.form_id,
            'generated_content': self.generated_content,
            'form_data': self.form_data,
            'created_date': self.created_date
        } 