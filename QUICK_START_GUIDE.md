# Nyaya Legal Platform - Quick Start Guide

Complete Firebase-based legal application ready for local deployment.

## 🚀 Instant Setup (5 minutes)

### 1. Download & Extract
Download this project and extract to your preferred directory.

### 2. Install Dependencies
```bash
cd nyaya-legal-platform
pip install -r requirements_firebase.txt
```

### 3. Firebase Setup (2 minutes)
1. Visit [Firebase Console](https://console.firebase.google.com/)
2. Create new project: "nyaya-legal-app"
3. Enable Authentication (Email/Password)
4. Enable Firestore Database (test mode)
5. Get project configuration from Project Settings

### 4. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your Firebase credentials
nano .env  # or use any text editor
```

Update these key values in `.env`:
```env
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_API_KEY=your-firebase-api-key
FIREBASE_PRIVATE_KEY="your-private-key"
FIREBASE_CLIENT_EMAIL=your-service-account-email
```

### 5. Run Application
```bash
# Create uploads directory
mkdir uploads

# Start the application
python run.py
```

Application runs at: `http://localhost:5000`

## 🎯 Core Features Available

### Document Analysis
- Upload PDF/DOCX files for AI legal analysis
- Compliance scoring with Indian law standards
- Issue detection and recommendations

### Smart Document Generation
- **Consumer Complaint**: Auto-generate consumer protection complaints
- **Legal Notice**: Formal legal notice creation
- **Rent Agreement**: Indian rental law compliant agreements
- **Employment Contract**: Job contract generation
- **RTI Application**: Right to Information requests
- **Will & Testament**: Legal will creation

### Emergency Legal Help
- GPS-based nearby lawyer finder
- Emergency contact numbers (100, 15100, 1091)
- Real-time lawyer availability status

### Comprehensive Law Library
- 10+ detailed Indian law entries
- Search by everyday topics ("bike accident", "property dispute")
- State-wise and category filtering
- AI-powered legal question answering

## 📋 Commands Summary

```bash
# Setup
pip install -r requirements_firebase.txt
cp .env.example .env
mkdir uploads

# Run
python run.py

# Alternative run methods
python firebase_app.py
gunicorn firebase_app:app
```

## 🔧 File Structure

```
nyaya-legal-platform/
├── firebase_app.py              # Main application
├── firebase_config.py           # Database service
├── run.py                      # Simple run script
├── requirements_firebase.txt    # Dependencies
├── .env.example               # Environment template
├── README_FIREBASE_SETUP.md   # Detailed setup guide
├── data/laws_database.json    # Indian laws database
├── templates/                 # HTML templates
└── uploads/                   # File upload directory
```

## 🌟 Key Capabilities

### AI-Powered Features
- Document compliance analysis using Gemini 2.0 Flash
- Smart legal document generation with Indian law references
- Natural language legal question answering
- Contextual legal advice based on uploaded documents

### Location Services
- Emergency lawyer finder with GPS distance calculation
- Filter lawyers by specialization, language, availability
- Direct calling and contact features

### Database Features
- Firebase Firestore for scalable data storage
- User authentication and session management
- Document storage and analysis history
- Real-time lawyer-user messaging system

## 🔐 Security Features

- Firebase Authentication for secure user management
- Encrypted data transmission
- Secure file upload with validation
- Role-based access control (User/Lawyer)

## 📱 User Experience

### For Citizens
- Simple document upload and analysis
- Plain-English legal explanations
- Emergency help with location services
- Generate legal documents without legal knowledge

### For Lawyers
- Client management dashboard
- Emergency availability toggle
- Direct client communication
- Profile management with specializations

## 🚨 Emergency Features

### Instant Help
- One-click emergency lawyer finder
- GPS-based distance calculation
- Emergency contact integration
- 24/7 availability indicators

### Legal Situations Covered
- Arrest and detention rights
- Property disputes and eviction
- Traffic accidents and insurance
- Domestic violence support
- Consumer protection issues

## 💡 Usage Examples

### Document Analysis
1. Login/Register
2. Upload PDF/DOCX legal document
3. View AI analysis with compliance score
4. Get recommendations for improvements

### Generate Consumer Complaint
1. Go to "Generate Documents"
2. Select "Consumer Complaint"
3. Fill smart form with guided fields
4. Download professionally formatted complaint

### Emergency Lawyer Search
1. Visit "Emergency Help"
2. Allow location access
3. Find nearby lawyers within customizable radius
4. Contact directly or view profiles

## 🔄 Development vs Production

### Development (Default)
- Uses Firebase test mode
- Local file storage
- Debug mode enabled
- Detailed error messages

### Production Deployment
- Update Firestore security rules
- Enable HTTPS/SSL
- Use production WSGI server
- Configure monitoring

This complete Firebase-based solution provides all the legal assistance features with professional-grade architecture suitable for both development and production deployment.