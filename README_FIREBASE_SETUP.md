# Nyaya Legal Platform - Firebase Setup Guide

Complete setup instructions for running the Nyaya Legal Platform locally with Firebase backend.

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8+ installed
- Git installed
- A Google account for Firebase

### 2. Download the Application

```bash
# Clone or download the project
git clone <your-repo-url>
cd nyaya-legal-platform

# OR if downloading as ZIP, extract and navigate to the folder
```

### 3. Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements_firebase.txt
```

### 4. Firebase Setup

#### Step 4.1: Create Firebase Project
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Create a project"
3. Enter project name: `nyaya-legal-app` (or your preferred name)
4. Enable Google Analytics (optional)
5. Create project

#### Step 4.2: Enable Authentication
1. In Firebase Console, go to "Authentication"
2. Click "Get started"
3. Go to "Sign-in method" tab
4. Enable "Email/Password" provider
5. Save

#### Step 4.3: Enable Firestore Database
1. In Firebase Console, go to "Firestore Database"
2. Click "Create database"
3. Choose "Start in test mode" (for development)
4. Select your preferred location
5. Create database

#### Step 4.4: Get Firebase Configuration
1. Go to Project Settings (gear icon)
2. In "General" tab, scroll down to "Your apps"
3. Click "Add app" → Web app
4. Register app with name: "Nyaya Legal App"
5. Copy the config object (you'll need these values)

#### Step 4.5: Generate Service Account Key
1. In Firebase Console, go to Project Settings
2. Click "Service accounts" tab
3. Click "Generate new private key"
4. Download the JSON file
5. Keep this file secure (never commit to version control)

### 5. Environment Configuration

#### Step 5.1: Create Environment File
```bash
# Copy the example environment file
cp .env.example .env
```

#### Step 5.2: Update .env File
Open `.env` file and update with your Firebase credentials:

```env
# Firebase Configuration (from Step 4.4)
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_API_KEY=your-api-key
FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
FIREBASE_MESSAGING_SENDER_ID=your-sender-id
FIREBASE_APP_ID=your-app-id

# Service Account (from downloaded JSON file in Step 4.5)
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@your-project-id.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id

# Flask Configuration
SESSION_SECRET=your-super-secure-random-string-here
FLASK_ENV=development

# AI Configuration (Gemini API)
GEMINI_API_KEY=AIzaSyB55sz3cuGqePKJlZKolIDzJLRUXAOSeoc
```

**Important Notes:**
- Replace all `your-*` placeholders with actual values from Firebase
- The `FIREBASE_PRIVATE_KEY` should include the `\n` characters as shown
- Generate a strong random string for `SESSION_SECRET`

### 6. Create Required Directories

```bash
# Create upload directory
mkdir uploads

# Create data directory (if not exists)
mkdir -p data
```

### 7. Run the Application

```bash
# Run the Flask application
python firebase_app.py
```

The application will start on `http://localhost:5000`

### 8. Access the Application

1. Open browser and go to `http://localhost:5000`
2. Click "Register" to create a new account
3. Fill out the registration form
4. Choose account type (User or Lawyer)
5. Start using the application!

## 🔧 Application Features

### Core Features
- **User Authentication**: Secure Firebase-based login/registration
- **Document Analysis**: AI-powered legal document analysis
- **Smart Document Generator**: Generate legal documents with AI
- **Law Library**: Comprehensive Indian law database with search
- **Emergency Help**: GPS-based lawyer finder for emergencies
- **Chat System**: AI legal assistant for questions

### Document Types Supported
- **Consumer Complaint**: Auto-generate consumer protection complaints
- **Legal Notice**: Formal legal notice generation
- **Rent Agreement**: Rental agreement with Indian law compliance
- **Employment Contract**: Job contract generation
- **RTI Application**: Right to Information applications
- **Will & Testament**: Legal will generation

### Emergency Features
- **Location-based Lawyer Search**: Find nearby lawyers using GPS
- **Emergency Contacts**: Quick access to legal helplines
- **24/7 Availability**: Emergency lawyer availability status

## 🐛 Troubleshooting

### Common Issues

#### Firebase Connection Issues
```bash
# Check if Firebase credentials are correct
python -c "from firebase_config import firebase_service; print('Firebase connected!' if firebase_service.db else 'Connection failed')"
```

#### Import Errors
```bash
# Reinstall dependencies
pip install --upgrade -r requirements_firebase.txt
```

#### Environment Variables Not Loading
- Ensure `.env` file is in the root directory
- Check for syntax errors in `.env` file
- Restart the application after changes

#### File Upload Issues
- Ensure `uploads/` directory exists and has write permissions
- Check file size limits (default: 16MB)

### Debug Mode
To run in debug mode for detailed error messages:

```python
# In firebase_app.py, change the last line to:
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

### Firestore Rules (Production)
For production, update Firestore rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only read/write their own data
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Documents belong to users
    match /documents/{document} {
      allow read, write: if request.auth != null && request.auth.uid == resource.data.user_id;
    }
    
    // Generated documents belong to users
    match /generated_documents/{document} {
      allow read, write: if request.auth != null && request.auth.uid == resource.data.user_id;
    }
    
    // Lawyers can be read by anyone, but only modified by the owner
    match /lawyers/{lawyerId} {
      allow read: if true;
      allow write: if request.auth != null && request.auth.uid == lawyerId;
    }
    
    // Chat sessions and messages
    match /chat_sessions/{sessionId} {
      allow read, write: if request.auth != null && request.auth.uid == resource.data.user_id;
    }
    
    match /chat_messages/{messageId} {
      allow read, write: if request.auth != null;
    }
  }
}
```

## 📁 Project Structure

```
nyaya-legal-platform/
├── firebase_app.py              # Main Flask application
├── firebase_config.py           # Firebase service configuration
├── ai_analyzer.py               # Document analysis with Gemini AI
├── enhanced_law_library.py      # Law database and search
├── smart_document_generator.py  # AI document generation
├── document_processor.py        # Document text extraction
├── requirements_firebase.txt    # Python dependencies
├── .env.example                 # Environment variables template
├── .env                        # Your environment variables (create this)
├── uploads/                    # File upload directory
├── data/                       # Law database files
└── templates/                  # HTML templates
    ├── auth/                   # Authentication pages
    ├── forms/                  # Document generation pages
    ├── emergency/              # Emergency help pages
    └── library/                # Law library pages
```

## 🔒 Security Notes

1. **Never commit `.env` file** to version control
2. **Use strong passwords** for user accounts
3. **Update Firestore rules** for production
4. **Enable Firebase App Check** for production
5. **Use HTTPS** in production environment
6. **Regularly update dependencies** for security patches

## 🚀 Deployment

### Local Development
- Use the setup above with `FLASK_ENV=development`
- Firebase in test mode is sufficient

### Production Deployment
1. Update Firestore rules (see above)
2. Set `FLASK_ENV=production` in `.env`
3. Use a production WSGI server like Gunicorn:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 firebase_app:app
   ```
4. Configure reverse proxy (nginx/Apache)
5. Enable HTTPS/SSL
6. Set up monitoring and logging

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all environment variables are set correctly
3. Ensure Firebase project is properly configured
4. Check application logs for detailed error messages

## 🎯 Key Features Verification

After setup, verify these features work:
- [ ] User registration and login
- [ ] Document upload and analysis
- [ ] AI document generation (Consumer Complaint)
- [ ] Law library search
- [ ] Emergency lawyer finder
- [ ] Chat with AI legal assistant

Your Nyaya Legal Platform is now ready to use with Firebase backend!