from app import app
import views  # This imports all the routes

if __name__ == '__main__':
    # Enable debug mode for development
    app.config['DEBUG'] = True
    
    # Configure session and security settings
    app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this in production
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
    
    # Configure template and static file settings
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    
    # Run the application
    app.run(
        host='localhost',      # Listen on localhost only
        port=5000,            # Port 5000 is the Flask default
        debug=True,           # Enable debug mode for development
        use_reloader=True     # Auto-reload on code changes
    )