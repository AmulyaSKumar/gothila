# Import all necessary modules
from app import app, db, ALLOWED_EXTENSIONS, allowed_file, calculate_distance
from flask import render_template, request, redirect, url_for, flash, jsonify, session, Response
from flask_login import login_user, logout_user, login_required, current_user
from models import User, Document, ChatSession, ChatMessage, Lawyer
from document_processor import DocumentProcessor
from ai_analyzer import AIAnalyzer
import os
import json
import uuid
import logging
from datetime import datetime
from werkzeug.utils import secure_filename
from law_library import LawLibrary

# Add this after the app initialization
@app.template_filter('datetime')
def format_datetime(value, format='%b %d, %Y %I:%M %p'):
    """Format a date time to a readable format"""
    if value is None:
        return ""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            return value
    return value.strftime(format)

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
                
                # Redirect based on user role
                if user.role == 'lawyer':
                    return redirect(next_page) if next_page else redirect(url_for('lawyer_dashboard'))
                else:
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
        
        # Check if user exists by email
        result = db.get_data('users')
        if result['success'] and result['data']:
            for user_data in result['data'].values():
                if user_data.get('email') == email:
                    flash('Email already exists', 'error')
                    return redirect(url_for('register'))
        
        # Generate a unique user ID
        user_id = str(uuid.uuid4())
        
        # Create new user
        user = User({
            'id': user_id,
            'username': username,
            'email': email,
            'full_name': full_name,
            'phone': phone,
            'role': role,
            'location': location
        })
        user.set_password(password)
        
        # Save to Firebase
        result = db.save_data(f'users/{user_id}', user.to_dict())
        if not result['success']:
            flash('Error creating user', 'error')
            return redirect(url_for('register'))
        
        # If registering as a lawyer, create lawyer profile
        if role == 'lawyer':
            # Get lawyer-specific fields
            specializations = request.form.getlist('specializations')
            experience_years = request.form.get('experience_years', 0)
            bar_council_id = request.form.get('bar_council_id')
            bio = request.form.get('bio')
            languages = request.form.getlist('languages')
            consultation_fee = request.form.get('consultation_fee')
            
            # Handle location coordinates
            lat = request.form.get('latitude')
            lng = request.form.get('longitude')
            location_coords = f"{lat},{lng}" if lat and lng else location
            
            # Create lawyer object
            lawyer = Lawyer({
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'full_name': full_name,
                'email': email,
                'phone': phone,
                'specializations': specializations,
                'experience_years': int(experience_years) if experience_years else 0,
                'bar_council_id': bar_council_id,
                'location': location_coords,
                'address': location,
                'bio': bio,
                'languages': languages,
                'consultation_fee': consultation_fee,
                'verified': False  # Lawyers need verification
            })
            
            # Handle document upload
            if 'verification_document' in request.files:
                doc_file = request.files['verification_document']
                if doc_file and allowed_file(doc_file.filename):
                    filename = secure_filename(doc_file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    doc_file.save(file_path)
                    
                    # TODO: Upload to Firebase Storage
                    # For now, just store the local path
                    lawyer.verification_document = file_path
            
            # Save lawyer to Firebase
            db.save_data(f'lawyers/{lawyer.id}', lawyer.to_dict())
            
            flash('Lawyer registration successful! Your account will be verified soon.', 'success')
            login_user(user)
            return redirect(url_for('lawyer_dashboard'))
        
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

@app.route('/lawyer-dashboard')
@login_required
def lawyer_dashboard():
    """Lawyer dashboard"""
    # Ensure only lawyers can access this page
    if current_user.role != 'lawyer':
        flash('Access denied. Lawyer account required.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get lawyer's connections/clients
    connections_result = db.get_data('lawyer_connections')
    connections = []
    
    if connections_result['success'] and connections_result['data']:
        lawyer_connections = [LawyerConnection(conn) for conn in connections_result['data'].values() 
                             if conn.get('lawyer_id') == current_user.id]
        
        for connection in lawyer_connections:
            # Get user details
            user_result = db.get_data(f'users/{connection.user_id}')
            if user_result['success'] and user_result['data']:
                user = User(user_result['data'])
                
                # Get latest message
                messages_result = db.get_data('lawyer_messages')
                latest_message = None
                
                if messages_result['success'] and messages_result['data']:
                    conn_messages = [msg for msg in messages_result['data'].values() 
                                    if msg.get('connection_id') == connection.id]
                    
                    if conn_messages:
                        # Sort by timestamp and get latest
                        sorted_messages = sorted(conn_messages, key=lambda x: x.get('timestamp', ''), reverse=True)
                        latest_message = sorted_messages[0]
                
                connection.user = user
                connection.latest_message = latest_message
                connections.append(connection)
    
    # Sort by last message date
    connections.sort(key=lambda x: x.last_message_date, reverse=True)
    
    return render_template('lawyers/lawyer_dashboard.html', connections=connections)

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

from flask import request, redirect, url_for, render_template, flash
from werkzeug.utils import secure_filename
from datetime import datetime
import os, uuid, json, logging
# Assume Document, db, allowed_file, DocumentProcessor, AIAnalyzer, current_user are imported

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

        db.save_data(f'documents/{doc_id}', document.to_dict())

        # Initialize processors
        try:
            processor = DocumentProcessor()
            analyzer = AIAnalyzer()
        except Exception as e:
            logging.error(f"Processor initialization failed: {str(e)}")
            flash('Document upload failed due to processing error.', 'error')
            return redirect(request.url)

        # Step 1: Text Extraction
        try:
            document.processing_status = 'extracting'
            db.save_data(f'documents/{doc_id}', document.to_dict())

            extracted_text = processor.extract_text(file_path, document.file_type)
            document.extracted_text = extracted_text
        except Exception as e:
            logging.error(f"Text extraction failed: {str(e)}")
            document.processing_status = 'failed'
            db.save_data(f'documents/{doc_id}', document.to_dict())
            flash('Text extraction failed.', 'error')
            return redirect(request.url)

        # Step 2: Analysis
        document.processing_status = 'analyzing'
        db.save_data(f'documents/{doc_id}', document.to_dict())

        try:
            analysis_results = analyzer.analyze_document(extracted_text, document.file_type)
            document.analysis_results = json.dumps(analysis_results)
        except Exception as e:
            logging.error(f"AI analysis error: {str(e)}")
            document.analysis_results = json.dumps({
                'error': str(e),
                'basic_summary': 'AI analysis failed, but document was processed.',
                'document_type': document.file_type
            })

        # Finalize
        document.processed = True
        document.processing_status = 'completed'
        db.save_data(f'documents/{doc_id}', document.to_dict())

        flash('Document uploaded and processed successfully!', 'success')
        return redirect(url_for('view_results', document_id=doc_id))
    
    flash('Invalid file type.', 'error')
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
    
    # Ensure stats are available for legal document summarization
    if 'stats' not in analysis:
        analysis['stats'] = {
            'word_count': 0,
            'character_count': 0,
            'paragraph_count': 0,
            'line_count': 0
        }
    
    return render_template('documents/results.html', document=document, analysis=analysis)

# Lawyer Routes
@app.route('/find-lawyer')
def find_lawyer():
    """Find a lawyer page"""
    # Get search parameters
    specialization = request.args.get('specialization')
    location = request.args.get('location')
    experience = request.args.get('experience')
    language = request.args.get('language')
    
    # Get all lawyers from Firebase
    result = db.get_data('lawyers')
    print(f"Laawyer data recieved:{result}")
    lawyers = []
    
    if result['success'] and result['data']:
        # Convert to Lawyer objects
        all_lawyers = [Lawyer(data) for data in result['data'].values()]
        
        # Apply filters if provided
        filtered_lawyers = all_lawyers
        if specialization:
            filtered_lawyers = [l for l in filtered_lawyers if specialization.lower() in [s.lower() for s in l.specializations]]
        if location:
            filtered_lawyers = [l for l in filtered_lawyers if location.lower() in l.location.lower()]
        if experience:
            min_exp = int(experience)
            filtered_lawyers = [l for l in filtered_lawyers if l.experience_years >= min_exp]
        if language:
            filtered_lawyers = [l for l in filtered_lawyers if language.lower() in [lang.lower() for lang in l.languages]]
        
        # Sort by rating and verified status
        lawyers = sorted(filtered_lawyers, key=lambda x: (-x.verified, -x.rating))
    
    # Get unique specializations and locations for filters
    specializations = sorted(list(set(spec for l in all_lawyers for spec in l.specializations))) if 'all_lawyers' in locals() else []
    locations = sorted(list(set(l.location for l in all_lawyers))) if 'all_lawyers' in locals() else []
    languages = sorted(list(set(lang for l in all_lawyers for lang in l.languages))) if 'all_lawyers' in locals() else []
    
    return render_template('lawyers/find_lawyer.html',
                         lawyers=lawyers,
                         specializations=specializations,
                         locations=locations,
                         languages=languages,
                         current_filters={
                             'specialization': specialization,
                             'location': location,
                             'experience': experience,
                             'language': language
                         })

# Law Library Routes
@app.route('/law-library')
def law_library():
    """Law library page"""
    # Get search parameters
    query = request.args.get('query') or request.args.get('q')  # Support both query and q parameters
    category = request.args.get('category')
    state = request.args.get('state')
    
    # Initialize law library
    law_lib = LawLibrary()
    
    # Get laws based on search criteria
    if query:
        laws = law_lib.search_laws(query, category, state)
    else:
        # Get all laws from the library
        laws = []
        for law_id, law_data in law_lib.law_cards.items():
            # Add the id to each law data
            law_data_with_id = law_data.copy()
            if 'id' not in law_data_with_id:
                law_data_with_id['id'] = law_id
            
            # Apply category filter
            if category and law_data_with_id.get('category', '').lower() != category.lower():
                continue
            
            # Apply state filter
            if state:
                state_field = law_data_with_id.get('state', '')
                state_list = [s.strip() for s in state_field.split(',')] if isinstance(state_field, str) else [state_field]
                if not any(state.lower() == s.lower() for s in state_list) and 'All India' not in state_list:
                    continue
            
            laws.append(law_data_with_id)
    
    # Get categories and states for filters
    categories = law_lib.get_categories()
    states = law_lib.get_states()
    
    return render_template('library/law_library.html',
                     law_cards=laws,
                     categories=categories,
                     states=states,
                     current_filters={
                         'query': query,
                         'category': category,
                         'state': state
                     })

@app.route('/law-library/<law_id>')
def law_detail(law_id):
    """Law detail page"""
    law_lib = LawLibrary()
    law = law_lib.get_law_details(law_id)
    
    if not law:
        flash('Law not found', 'error')
        return redirect(url_for('law_library'))
    
    # Ensure the law has an id field
    if 'id' not in law:
        law['id'] = law_id
    
    return render_template('library/law_detail.html', law=law)

# Legal Forms Routes
@app.route('/legal-forms')
def legal_forms():
    """Legal forms page"""
    return render_template('forms/legal_forms.html')

# Know Your Rights Routes
@app.route('/know-your-rights')
def know_your_rights():
    """Know your rights page"""
    return render_template('rights/know_your_rights.html')

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

@app.route('/api/emergency-lawyers')
def emergency_lawyers_api():
    """API endpoint to find nearby lawyers based on user location"""
    # Get user's location from request parameters
    try:
        user_lat = float(request.args.get('lat'))
        user_lng = float(request.args.get('lng'))
        radius = float(request.args.get('radius', 10))  # Default 10km radius
    except (TypeError, ValueError):
        return jsonify({
            'success': False,
            'error': 'Invalid location parameters. Please provide valid lat and lng values.'
        }), 400
    
    # Get all lawyers from Firebase
    result = db.get_data('lawyers')
    nearby_lawyers = []
    
    if result['success'] and result['data']:
        # Convert to Lawyer objects
        all_lawyers = [Lawyer(data) for data in result['data'].values()]
        
        # Filter available lawyers and those with location data
        available_lawyers = [lawyer for lawyer in all_lawyers 
                           if lawyer.available and lawyer.location and ',' in lawyer.location]
        
        # Calculate distance for each lawyer and filter by radius
        for lawyer in available_lawyers:
            # Parse lawyer location (assuming format like "lat,lng")
            try:
                lawyer_lat, lawyer_lng = map(float, lawyer.location.split(','))
                
                # Calculate distance using Haversine formula
                distance = calculate_distance(user_lat, user_lng, lawyer_lat, lawyer_lng)
                
                # Include lawyer if within radius
                if distance <= radius:
                    lawyer_dict = lawyer.to_dict()
                    lawyer_dict['distance'] = round(distance, 2)
                    nearby_lawyers.append(lawyer_dict)
            except (ValueError, TypeError):
                continue
        
        # Sort by distance (closest first) and take top 3
        nearby_lawyers.sort(key=lambda x: x['distance'])
        nearby_lawyers = nearby_lawyers[:3]
    
    return jsonify({
        'success': True,
        'count': len(nearby_lawyers),
        'lawyers': nearby_lawyers
    })

@app.route('/lawyer-directory')
@login_required
def lawyer_directory():
    """Lawyer directory for users"""
    # Get search parameters
    specialization = request.args.get('specialization')
    location = request.args.get('location')
    radius = float(request.args.get('radius', 10))  # Default 10km radius
    
    # Get all verified lawyers from Firebase
    result = db.get_data('lawyers')
    lawyers = []
    
    if result['success'] and result['data']:
        # Convert to Lawyer objects and filter verified ones
        all_lawyers = [Lawyer(data) for data in result['data'].values() if data.get('verified', False)]
        
        # Apply filters if provided
        filtered_lawyers = all_lawyers
        if specialization:
            filtered_lawyers = [l for l in filtered_lawyers if specialization.lower() in [s.lower() for s in l.specializations]]
        
        # Filter by location radius if user has location and radius is specified
        if location and radius > 0 and current_user.location:
            try:
                # Parse user location (assuming format like "28.6139,77.2090")
                if isinstance(current_user.location, str) and ',' in current_user.location:
                    user_lat, user_lng = map(float, current_user.location.split(','))
                    
                    # Filter lawyers by distance
                    lawyers_with_distance = []
                    for lawyer in filtered_lawyers:
                        if not lawyer.location or ',' not in lawyer.location:
                            continue
                            
                        lawyer_lat, lawyer_lng = map(float, lawyer.location.split(','))
                        distance = calculate_distance(user_lat, user_lng, lawyer_lat, lawyer_lng)
                        
                        if distance <= radius:
                            lawyer_dict = lawyer.to_dict()
                            lawyer_dict['distance'] = round(distance, 1)
                            lawyers_with_distance.append((lawyer, distance))
                    
                    # Sort by distance
                    lawyers_with_distance.sort(key=lambda x: x[1])
                    filtered_lawyers = [l[0] for l in lawyers_with_distance]
            except (ValueError, TypeError):
                pass  # If location parsing fails, skip distance filtering
        
        # Sort by rating
        lawyers = sorted(filtered_lawyers, key=lambda x: -x.rating)
    
    # Get unique specializations for filters
    specializations = sorted(list(set(spec for l in all_lawyers for spec in l.specializations))) if 'all_lawyers' in locals() else []
    
    return render_template('lawyers/lawyer_directory.html',
                         lawyers=lawyers,
                         specializations=specializations,
                         current_filters={
                             'specialization': specialization,
                             'location': location,
                             'radius': radius
                         })

@app.route('/connect-lawyer/<lawyer_id>', methods=['GET', 'POST'])
@login_required
def connect_lawyer_redirect(lawyer_id):
    """Redirect to the contact-lawyer route for backward compatibility"""
    return redirect(url_for('contact_lawyer', lawyer_id=lawyer_id))
@login_required
def contact_lawyer(lawyer_id):
    """Contact a lawyer"""
    # Get lawyer details
    result = db.get_data(f'lawyers/{lawyer_id}')
    if not result['success'] or not result['data']:
        flash('Lawyer not found', 'error')
        return redirect(url_for('lawyer_directory'))
    
    lawyer = Lawyer(result['data'])
    
    if request.method == 'POST':
        # Check if connection already exists
        connections_result = db.get_data('lawyer_connections')
        existing_connection = None
        
        if connections_result['success'] and connections_result['data']:
            for conn_id, conn_data in connections_result['data'].items():
                if conn_data.get('user_id') == current_user.id and conn_data.get('lawyer_id') == lawyer_id:
                    existing_connection = conn_id
                    break
        
        # Create new connection if it doesn't exist
        if not existing_connection:
            connection = LawyerConnection({
                'id': str(uuid.uuid4()),
                'user_id': current_user.id,
                'lawyer_id': lawyer_id,
                'status': 'active',
                'case_description': request.form.get('case_description'),
                'urgency': request.form.get('urgency', 'normal')
            })
            
            connection_id = connection.id
            db.save_data(f'lawyer_connections/{connection_id}', connection.to_dict())
        else:
            connection_id = existing_connection
        
        # Add message
        message = request.form.get('message')
        if message:
            lawyer_message = LawyerMessage({
                'id': str(uuid.uuid4()),
                'connection_id': connection_id,
                'sender_type': 'user',
                'message': message
            })
            
            db.save_data(f'lawyer_messages/{lawyer_message.id}', lawyer_message.to_dict())
            
            # Update last message date in connection
            db.save_data(f'lawyer_connections/{connection_id}', {
                'last_message_date': datetime.utcnow().isoformat()
            })
        
        flash('Message sent successfully!', 'success')
        return redirect(url_for('my_lawyers'))
    
    return render_template('lawyers/contact_lawyer.html', lawyer=lawyer)

@app.route('/my-lawyers')
@login_required
def my_lawyers():
    """View user's lawyer connections"""
    # Get user's connections
    connections_result = db.get_data('lawyer_connections')
    connections = []
    
    if connections_result['success'] and connections_result['data']:
        user_connections = [conn for conn in connections_result['data'].items() 
                           if conn[1].get('user_id') == current_user.id]
        
        for conn_id, conn_data in user_connections:
            # Get lawyer details
            lawyer_result = db.get_data(f'lawyers/{conn_data.get("lawyer_id")}')
            if lawyer_result['success'] and lawyer_result['data']:
                lawyer = Lawyer(lawyer_result['data'])
                
                # Get latest message
                messages_result = db.get_data('lawyer_messages')
                latest_message = None
                
                if messages_result['success'] and messages_result['data']:
                    conn_messages = [msg for msg in messages_result['data'].values() 
                                    if msg.get('connection_id') == conn_id]
                    
                    if conn_messages:
                        # Sort by timestamp and get latest
                        sorted_messages = sorted(conn_messages, key=lambda x: x.get('timestamp', ''), reverse=True)
                        latest_message = sorted_messages[0]
                
                connections.append({
                    'connection_id': conn_id,
                    'connection': LawyerConnection(conn_data),
                    'lawyer': lawyer,
                    'latest_message': latest_message
                })
    
    # Sort by last message date
    connections.sort(key=lambda x: x['connection'].last_message_date, reverse=True)
    
    return render_template('lawyers/my_lawyers.html', connections=connections)

@app.route('/conversation/<connection_id>', methods=['GET', 'POST'])
@login_required
def lawyer_conversation(connection_id):
    """View and send messages in a lawyer conversation"""
    # Get connection details
    result = db.get_data(f'lawyer_connections/{connection_id}')
    if not result['success'] or not result['data']:
        flash('Conversation not found', 'error')
        return redirect(url_for('my_lawyers'))
    
    connection = LawyerConnection(result['data'])
    
    # Ensure user is part of this conversation
    if connection.user_id != current_user.id and connection.lawyer_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('my_lawyers'))
    
    # Get other party details
    other_party = None
    if current_user.role == 'lawyer':
        user_result = db.get_data(f'users/{connection.user_id}')
        if user_result['success'] and user_result['data']:
            other_party = User(user_result['data'])
    else:
        lawyer_result = db.get_data(f'lawyers/{connection.lawyer_id}')
        if lawyer_result['success'] and lawyer_result['data']:
            other_party = Lawyer(lawyer_result['data'])
    
    # Handle new message
    if request.method == 'POST':
        message = request.form.get('message')
        attachment_path = None
        
        # Handle file upload
        if 'attachment' in request.files:
            file = request.files['attachment']
            if file and file.filename:
                filename = secure_filename(file.filename)
                # Create a unique filename to avoid collisions
                unique_filename = f"{uuid.uuid4()}_{filename}"
                upload_folder = os.path.join('uploads', 'lawyer_attachments')
                os.makedirs(os.path.join(app.static_folder, upload_folder), exist_ok=True)
                file_path = os.path.join(app.static_folder, upload_folder, unique_filename)
                file.save(file_path)
                attachment_path = os.path.join(upload_folder, unique_filename)
        
        if message:
            lawyer_message = LawyerMessage({
                'id': str(uuid.uuid4()),
                'connection_id': connection_id,
                'sender_type': current_user.role,
                'message': message,
                'attachment_path': attachment_path
            })
            
            db.save_data(f'lawyer_messages/{lawyer_message.id}', lawyer_message.to_dict())
            
            # Update last message date in connection
            db.save_data(f'lawyer_connections/{connection_id}', {
                'last_message_date': datetime.utcnow().isoformat()
            })
            
            flash('Message sent', 'success')
            return redirect(url_for('lawyer_conversation', connection_id=connection_id))
    
    # Get all messages
    messages_result = db.get_data('lawyer_messages')
    messages = []
    
    if messages_result['success'] and messages_result['data']:
        conn_messages = [LawyerMessage(msg) for msg in messages_result['data'].values() 
                        if msg.get('connection_id') == connection_id]
        
        # Sort by timestamp
        messages = sorted(conn_messages, key=lambda x: x.timestamp)
    
    return render_template('lawyers/conversation.html', 
                         connection=connection,
                         other_party=other_party,
                         messages=messages)