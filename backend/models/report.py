from datetime import datetime
from extensions import db

class Report(db.Model):
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incidents.id'), nullable=True)
    
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    reported_time = db.Column(db.DateTime, nullable=False)
    submission_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    reported_lat = db.Column(db.Float, nullable=False)
    reported_lng = db.Column(db.Float, nullable=False)
    device_lat = db.Column(db.Float, nullable=True)
    device_lng = db.Column(db.Float, nullable=True)
    
    evidence_path = db.Column(db.String(500), nullable=True)
    trust_score = db.Column(db.Float, default=0.0, nullable=False)
    
    verification_state = db.Column(db.String(30), default='Unverified', nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert report to dictionary"""
        return {
            'id': self.id,
            'incident_id': self.incident_id,
            'category': self.category,
            'description': self.description,
            'reported_time': self.reported_time.isoformat() if self.reported_time else None,
            'submission_time': self.submission_time.isoformat() if self.submission_time else None,
            'reported_lat': self.reported_lat,
            'reported_lng': self.reported_lng,
            'device_lat': self.device_lat,
            'device_lng': self.device_lng,
            'evidence_path': self.evidence_path,
            'trust_score': self.trust_score,
            'verification_state': self.verification_state,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f'<Report {self.id}: {self.category} - {self.verification_state}>'

