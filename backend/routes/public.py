from flask import Blueprint, request, jsonify
from datetime import datetime
from extensions import db
from models.report import Report
from models.incident import Incident
from services.trust_score import calculate_trust_score
from services.similarity import process_similarity_matching
from services.priority import update_incident_scores, calculate_confidence_score
from config import Config
from sockets.events import emit_report_verification_updated, emit_incident_created, emit_incident_updated

public_bp = Blueprint('public', __name__)

@public_bp.route('/api/report', methods=['POST'])
def submit_report():
    """Submit a new incident report"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['category', 'description', 'reported_lat', 'reported_lng', 'reported_time']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Parse reported_time
        try:
            reported_time = datetime.fromisoformat(data['reported_time'].replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return jsonify({'error': 'Invalid reported_time format. Use ISO 8601 format.'}), 400
        
        # Create report
        report = Report(
            category=data['category'],
            description=data['description'],
            reported_lat=float(data['reported_lat']),
            reported_lng=float(data['reported_lng']),
            device_lat=float(data.get('device_lat')) if data.get('device_lat') is not None else None,
            device_lng=float(data.get('device_lng')) if data.get('device_lng') is not None else None,
            evidence_path=data.get('evidence_path'),
            reported_time=reported_time,
            verification_state='Unverified'
        )
        
        db.session.add(report)
        db.session.flush()  # Get the ID
        
        # Calculate trust score
        trust_score = calculate_trust_score(report)
        report.trust_score = trust_score
        
        # Update verification state based on trust score
        if trust_score >= Config.TRUST_SCORE_VERIFIED_THRESHOLD:
            report.verification_state = 'Verified'
        else:
            report.verification_state = 'Flagged for Admin Review'
        
        db.session.commit()
        
        # Emit WebSocket event
        emit_report_verification_updated(report)
        
        # If verified, process similarity matching
        if report.verification_state == 'Verified':
            action, incident_id, similarity_score, candidates = process_similarity_matching(report)
            
            if action == 'auto_merge':
                # Merge into existing incident
                incident = Incident.query.get(incident_id)
                report.incident_id = incident_id
                db.session.commit()
                
                # Update incident scores
                update_incident_scores(incident)
                
                # Emit update
                emit_incident_updated(incident)
                
            elif action == 'new_incident':
                # Create new incident
                incident = Incident(
                    category=report.category,
                    latitude=report.reported_lat,
                    longitude=report.reported_lng,
                    location_label=data.get('location_label')
                )
                db.session.add(incident)
                db.session.flush()
                
                report.incident_id = incident.id
                db.session.commit()
                
                # Update incident scores
                update_incident_scores(incident)
                
                # Emit creation
                emit_incident_created(incident)
        
        return jsonify({
            'report_id': report.id,
            'trust_score': report.trust_score,
            'verification_state': report.verification_state,
            'incident_id': report.incident_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@public_bp.route('/api/report/status/<int:report_id>', methods=['GET'])
def get_report_status(report_id):
    """Get status of a report"""
    report = Report.query.get_or_404(report_id)
    return jsonify(report.to_dict()), 200

@public_bp.route('/api/incidents/public', methods=['GET'])
def get_public_incidents():
    """Get all incidents visible to public (must have at least one VERIFIED report)"""
    # Get all incidents with at least one verified report
    incidents = db.session.query(Incident).join(Report).filter(
        Report.verification_state == 'Verified'
    ).distinct().all()
    
    # Filter to ensure each incident has at least one verified report
    public_incidents = []
    for incident in incidents:
        if any(r.verification_state == 'Verified' for r in incident.reports):
            public_incidents.append(incident.to_dict(include_reports=False))
    
    return jsonify({'incidents': public_incidents}), 200

