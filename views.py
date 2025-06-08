# Import all necessary modules
from app import app, db, ALLOWED_EXTENSIONS, allowed_file, calculate_distance
from flask import render_template, request, redirect, url_for, flash, jsonify, session, Response
from flask_login import login_user, logout_user, login_required, current_user
from models import User, Document, ChatSession, ChatMessage
from document_processor import DocumentProcessor
from ai_analyzer import AIAnalyzer
import os
import json
import uuid
import logging
from datetime import datetime
from werkzeug.utils import secure_filename

# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Get user from Firebase
        result = db.get_data(f'users/{username}')
        if result['success'] and result['data']:
            user = User(result['data'])
            if user.check_password(password):
                login_user(user)
                next_page = request.args.get('next')
                flash(f'Welcome back, {user.full_name or user.username}!', 'success')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        
        flash('Invalid username or password', 'error')
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        role = request.form.get('role', 'user')
        location = request.form.get('location')
        
        # Check if user exists
        result = db.get_data(f'users/{username}')
        if result['success'] and result['data']:
            flash('Username already exists', 'error')
            return redirect(url_for('register'))
        
        # Create new user
        user = User({
            'id': username,
            'username': username,
            'email': email,
            'full_name': full_name,
            'phone': phone,
            'role': role,
            'location': location
        })
        user.set_password(password)
        
        # Save to Firebase
        result = db.save_data(f'users/{username}', user.to_dict())
        if not result['success']:
            flash('Error creating user', 'error')
            return redirect(url_for('register'))
        
        login_user(user)
        flash('Registration successful! Welcome to Nyaya.', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('auth/register.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

# Main Application Routes
@app.route('/')
def home():
    """Nyaya home page"""
    # Get recent documents from Firebase
    result = db.get_data('documents')
    recent_documents = []
    if result['success'] and result['data']:
        docs = result['data'].values()
        # Sort by upload date and take latest 3
        sorted_docs = sorted(docs, key=lambda x: x.get('upload_date', ''), reverse=True)[:3]
        recent_documents = [Document(doc) for doc in sorted_docs]
    
    # Get user stats
    users_result = db.get_data('users')
    total_users = len(users_result.get('data', {})) if users_result['success'] else 0
    
    # Get document stats
    docs_result = db.get_data('documents')
    total_docs = len([d for d in docs_result.get('data', {}).values() 
                     if d.get('processed', False)]) if docs_result['success'] else 0
    
    stats = {
        'total_users': total_users,
        'total_lawyers': 0,  # We'll implement this later
        'documents_analyzed': total_docs
    }
    
    return render_template('home.html', stats=stats, recent_documents=recent_documents)

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    # Get user's documents
    docs_result = db.get_data('documents')
    user_documents = []
    if docs_result['success'] and docs_result['data']:
        user_docs = [doc for doc in docs_result['data'].values() 
                    if doc.get('user_id') == current_user.id]
        sorted_docs = sorted(user_docs, key=lambda x: x.get('upload_date', ''), reverse=True)[:5]
        user_documents = [Document(doc) for doc in sorted_docs]
    
    return render_template('dashboard/user_dashboard.html', 
                         documents=user_documents)

# Chat Routes
@app.route('/chat')
def chat():
    """AI chatbot page"""
    return render_template('chat/chat.html')

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """Handle chatbot conversations"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        session_id = data.get('session_id') or str(uuid.uuid4())
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Get or create chat session
        session_result = db.get_data(f'chat_sessions/{session_id}')
        chat_session = None
        
        if not session_result['success'] or not session_result['data']:
            chat_session = ChatSession({
                'id': session_id,
                'session_id': session_id,
                'user_id': current_user.id if current_user.is_authenticated else None,
                'title': message[:50] + '...' if len(message) > 50 else message
            })
            db.save_data(f'chat_sessions/{session_id}', chat_session.to_dict())
        else:
            chat_session = ChatSession(session_result['data'])
        
        # Save user message
        msg_id = str(uuid.uuid4())
        user_message = ChatMessage({
            'id': msg_id,
            'session_id': session_id,
            'message_type': 'user',
            'content': message
        })
        db.save_data(f'chat_messages/{msg_id}', user_message.to_dict())
        
        # Get AI response
        analyzer = AIAnalyzer()
        ai_response = analyzer.answer_legal_question(message)
        
        # Save AI response
        bot_msg_id = str(uuid.uuid4())
        bot_message = ChatMessage({
            'id': bot_msg_id,
            'session_id': session_id,
            'message_type': 'bot',
            'content': ai_response
        })
        db.save_data(f'chat_messages/{bot_msg_id}', bot_message.to_dict())
        
        # Update session activity
        chat_session.last_activity = datetime.utcnow().isoformat()
        db.save_data(f'chat_sessions/{session_id}', chat_session.to_dict())
        
        return jsonify({
            'response': ai_response,
            'session_id': session_id,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logging.error(f"Chat API error: {str(e)}")
        return jsonify({'error': 'Chat service temporarily unavailable'}), 500

# Document Routes
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Document upload and analysis"""
    if request.method == 'GET':
        return render_template('documents/upload.html')
        
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = str(int(datetime.now().timestamp()))
        unique_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        file.save(file_path)
        
        # Create document record
        doc_id = str(uuid.uuid4())
        document = Document({
            'id': doc_id,
            'user_id': current_user.id if current_user.is_authenticated else None,
            'filename': unique_filename,
            'original_filename': filename,
            'file_path': file_path,
            'file_size': os.path.getsize(file_path),
            'file_type': filename.rsplit('.', 1)[1].lower()
        })
        
        # Save to Firebase
        db.save_data(f'documents/{doc_id}', document.to_dict())
        
        # Process document
        try:
            processor = DocumentProcessor()
            analyzer = AIAnalyzer()
            
            document.processing_status = 'extracting'
            db.save_data(f'documents/{doc_id}', document.to_dict())
            
            extracted_text = processor.extract_text(file_path, document.file_type)
            document.extracted_text = extracted_text
            
            document.processing_status = 'analyzing'
            db.save_data(f'documents/{doc_id}', document.to_dict())
            
            analysis_results = analyzer.analyze_document(extracted_text, document.file_type)
            document.analysis_results = json.dumps(analysis_results)
            document.processed = True
            document.processing_status = 'completed'
            db.save_data(f'documents/{doc_id}', document.to_dict())
            
            flash('Document uploaded and analyzed successfully!', 'success')
            return redirect(url_for('view_results', document_id=doc_id))
            
        except Exception as e:
            logging.error(f"Document processing error: {str(e)}")
            document.processing_status = 'failed'
            db.save_data(f'documents/{doc_id}', document.to_dict())
            flash('Error processing document. Please try again.', 'error')
            return redirect(url_for('upload_file'))
    
    flash('Invalid file type', 'error')
    return redirect(request.url)

@app.route('/results/<document_id>')
def view_results(document_id):
    """View document analysis results"""
    result = db.get_data(f'documents/{document_id}')
    if not result['success'] or not result['data']:
        return render_template('errors/404.html'), 404
    
    document = Document(result['data'])
    if not document.processed:
        flash('Document is still being processed', 'info')
        return redirect(url_for('dashboard'))
    
    analysis = json.loads(document.analysis_results) if document.analysis_results else {}
    return render_template('documents/results.html', document=document, analysis=analysis)

# Lawyer Routes
@app.route('/find-lawyer')
def find_lawyer():
    """Find a lawyer page"""
    return render_template('lawyers/find.html')

# Law Library Routes
@app.route('/law-library')
def law_library():
    """Law library page"""
    return render_template('law_library.html')

# Legal Forms Routes
@app.route('/legal-forms')
def legal_forms():
    """Legal forms page"""
    return render_template('forms/index.html')

# Know Your Rights Routes
@app.route('/know-your-rights')
def know_your_rights():
    """Know your rights page"""
    return render_template('know_your_rights.html')

# Emergency Help Routes
@app.route('/emergency')
def emergency_help():
    """Emergency legal help page"""
    return render_template('emergency.html')

# Case Notes Routes
@app.route('/case-notes')
@login_required
def case_notes():
    """User's case notes page"""
    # Get user's case notes from Firebase
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    db = get_db()
    notes_ref = db.collection('case_notes').where('user_id', '==', current_user.id).stream()
    notes = []
    for note in notes_ref:
        note_data = note.to_dict()
        note_data['id'] = note.id
        notes.append(note_data)
    
    return render_template('case_notes.html', notes=notes)

@app.route('/case-notes/add', methods=['POST'])
@login_required
def add_case_note():
    """Add a new case note"""
    if not current_user.is_authenticated:
        return jsonify({'error': 'Authentication required'}), 401
    
    title = request.form.get('title')
    content = request.form.get('content')
    case_type = request.form.get('case_type')
    
    if not all([title, content, case_type]):
        flash('Please fill in all required fields', 'error')
        return redirect(url_for('case_notes'))
    
    db = get_db()
    note_data = {
        'user_id': current_user.id,
        'title': title,
        'content': content,
        'case_type': case_type,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    
    db.collection('case_notes').add(note_data)
    flash('Note added successfully', 'success')
    return redirect(url_for('case_notes'))

@app.route('/case-notes/<note_id>/edit', methods=['POST'])
@login_required
def edit_case_note(note_id):
    """Edit an existing case note"""
    if not current_user.is_authenticated:
        return jsonify({'error': 'Authentication required'}), 401
    
    title = request.form.get('title')
    content = request.form.get('content')
    case_type = request.form.get('case_type')
    
    if not all([title, content, case_type]):
        flash('Please fill in all required fields', 'error')
        return redirect(url_for('case_notes'))
    
    db = get_db()
    note_ref = db.collection('case_notes').document(note_id)
    note = note_ref.get()
    
    if not note.exists:
        flash('Note not found', 'error')
        return redirect(url_for('case_notes'))
    
    note_data = note.to_dict()
    if note_data['user_id'] != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('case_notes'))
    
    note_ref.update({
        'title': title,
        'content': content,
        'case_type': case_type,
        'updated_at': datetime.utcnow()
    })
    
    flash('Note updated successfully', 'success')
    return redirect(url_for('case_notes'))

@app.route('/case-notes/<note_id>/delete', methods=['POST'])
@login_required
def delete_case_note(note_id):
    """Delete a case note"""
    if not current_user.is_authenticated:
        return jsonify({'error': 'Authentication required'}), 401
    
    db = get_db()
    note_ref = db.collection('case_notes').document(note_id)
    note = note_ref.get()
    
    if not note.exists:
        flash('Note not found', 'error')
        return redirect(url_for('case_notes'))
    
    note_data = note.to_dict()
    if note_data['user_id'] != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('case_notes'))
    
    note_ref.delete()
    flash('Note deleted successfully', 'success')
    return redirect(url_for('case_notes'))

# Error Handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500

@app.errorhandler(413)
def too_large(error):
    flash('File too large. Maximum size is 16MB.', 'error')
    return redirect(url_for('upload_file')) 