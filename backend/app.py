from flask import Flask, send_from_directory
from flask_cors import CORS
from config import Config
from extensions import db, socketio
from models.incident import Incident
from models.report import Report
from routes.public import public_bp
from routes.admin import admin_bp
import os

def create_app():
    """Create and configure the Flask application"""
    app = Flask(
        __name__,
        static_folder="static",
        static_url_path=""
    )

    app.config.from_object(Config)
    
    # Enable CORS for all routes
    CORS(app, supports_credentials=True, origins="*")
    
    # Initialize extensions
    db.init_app(app)
    
    # Use eventlet for production, threading for development
    async_mode = os.environ.get('SOCKETIO_ASYNC_MODE', 'eventlet')
    socketio.init_app(app, cors_allowed_origins="*", async_mode=async_mode)
    
    # Register blueprints
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)
    
    # Serve frontend static files
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_frontend(path):
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, "index.html")
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    socketio.run(app, host='0.0.0.0', port=port, debug=debug)

