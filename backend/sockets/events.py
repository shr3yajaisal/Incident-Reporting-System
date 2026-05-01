from extensions import socketio, db
from models.incident import Incident
from models.report import Report

def emit_incident_created(incident):
    """Emit INCIDENT_CREATED event"""
    socketio.emit('INCIDENT_CREATED', incident.to_dict(include_reports=True))

def emit_incident_updated(incident):
    """Emit INCIDENT_UPDATED event"""
    socketio.emit('INCIDENT_UPDATED', incident.to_dict(include_reports=True))

def emit_incident_resolved(incident):
    """Emit INCIDENT_RESOLVED event"""
    socketio.emit('INCIDENT_RESOLVED', incident.to_dict(include_reports=True))

def emit_report_verification_updated(report):
    """Emit REPORT_VERIFICATION_UPDATED event"""
    # Include the incident if it exists
    payload = report.to_dict()
    if report.incident_id:
        incident = Incident.query.get(report.incident_id)
        if incident:
            payload['incident'] = incident.to_dict(include_reports=True)
    
    socketio.emit('REPORT_VERIFICATION_UPDATED', payload)

