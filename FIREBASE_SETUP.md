# Simple Firebase Setup Guide

Follow these steps to set up Firebase for your application:

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or select an existing one
3. Enable Email/Password Authentication:
   - Go to Authentication > Sign-in method
   - Enable Email/Password provider

4. Get your Firebase config:
   - Go to Project Settings (gear icon)
   - Under "Your apps", click the web icon (</>)
   - Register your app with a nickname
   - Copy the firebaseConfig object
   - Paste it into `firebase-config.json`

5. Get your Firebase Admin SDK credentials:
   - In Project Settings, go to Service Accounts
   - Click "Generate New Private Key"
   - Save the JSON file as `firebase-credentials.json` in your project root

6. Install dependencies:
```bash
pip install -r requirements_firebase.txt
```

That's it! Your Firebase setup is complete. 