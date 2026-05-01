import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Handle database URL - Render provides postgres:// but SQLAlchemy needs postgresql://
    database_url = os.environ.get('DATABASE_URL') or 'sqlite:///db.sqlite'
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # SocketIO configuration
    SOCKETIO_ASYNC_MODE = 'eventlet'
    SOCKETIO_CORS_ALLOWED_ORIGINS = "*"
    
    # Admin credentials (simple auth)
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME') or 'admin'
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'admin123'
    
    # Similarity thresholds
    SIMILARITY_AUTO_MERGE_THRESHOLD = 0.70
    SIMILARITY_REVIEW_THRESHOLD = 0.40
    
    # Spatial and temporal windows
    SPATIAL_RADIUS_METERS = 300
    TEMPORAL_WINDOW_HOURS = 1
    
    # Trust score threshold
    TRUST_SCORE_VERIFIED_THRESHOLD = 0.4

