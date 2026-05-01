from datetime import datetime
from extensions import db

class Incident(db.Model):
    __tablename__ = 'incidents'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    location_label = db.Column(db.String(200))
    
    resolution_status = db.Column(db.String(20), default='Unresolved', nullable=False)
    priority_label = db.Column(db.String(20), default='Low', nullable=False)
    priority_score = db.Column(db.Float, default=0.0, nullable=False)
    confidence_score = db.Column(db.Float, default=0.0, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship
    reports = db.relationship('Report', backref='incident', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_reports=False):
        """Convert incident to dictionary"""
        data = {
            'id': self.id,
            'category': self.category,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'location_label': self.location_label,
            'resolution_status': self.resolution_status,
            'priority_label': self.priority_label,
            'priority_score': self.priority_score,
            'confidence_score': self.confidence_score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_reports:
            data['reports'] = [report.to_dict() for report in self.reports]
        
        return data
    
    def __repr__(self):
        return f'<Incident {self.id}: {self.category} at ({self.latitude}, {self.longitude})>'

