from flask import Blueprint, request, jsonify, session
from extensions import db
from models.incident import Incident
from models.report import Report
from services.similarity import find_candidate_incidents, calculate_similarity_score
from services.priority import update_incident_scores
from sockets.events import emit_incident_resolved, emit_incident_updated, emit_report_verification_updated
from config import Config

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/api/admin/login', methods=['POST'])
def admin_login():
    """Simple admin login"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if username == Config.ADMIN_USERNAME and password == Config.ADMIN_PASSWORD:
        session['admin'] = True
        return jsonify({'success': True, 'message': 'Login successful'}), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

def require_admin():
    """Check if user is admin"""
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    return None

@admin_bp.route('/api/admin/incidents', methods=['GET'])
def get_all_incidents():
    """Get all incidents (admin view)"""
    auth_error = require_admin()
    if auth_error:
        return auth_error
    
    incidents = Incident.query.all()
    return jsonify({
        'incidents': [incident.to_dict(include_reports=True) for incident in incidents]
    }), 200

@admin_bp.route('/api/admin/reports/flagged', methods=['GET'])
def get_flagged_reports():
    """Get all flagged reports for admin review"""
    auth_error = require_admin()
    if auth_error:
        return auth_error
    
    flagged_reports = Report.query.filter_by(verification_state='Flagged for Admin Review').all()
    return jsonify({
        'reports': [report.to_dict() for report in flagged_reports]
    }), 200

@admin_bp.route('/api/admin/reports/similarity', methods=['GET'])
def get_similarity_review_queue():
    """Get reports that need similarity review"""
    auth_error = require_admin()
    if auth_error:
        return auth_error
    
    # Get all verified reports that are not yet assigned to an incident
    verified_unassigned = Report.query.filter_by(
        verification_state='Verified',
        incident_id=None
    ).all()
    
    similarity_reviews = []
    for report in verified_unassigned:
        candidates = find_candidate_incidents(report)
        if candidates:
            candidate_scores = []
            for candidate in candidates:
                score = calculate_similarity_score(report, candidate)
                candidate_scores.append({
                    'incident_id': candidate.id,
                    'incident': candidate.to_dict(include_reports=False),
                    'similarity_score': score
                })
            
            # Sort by score descending
            candidate_scores.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            # Only include if best score is in review range
            if candidate_scores and Config.SIMILARITY_REVIEW_THRESHOLD <= candidate_scores[0]['similarity_score'] < Config.SIMILARITY_AUTO_MERGE_THRESHOLD:
                similarity_reviews.append({
                    'report': report.to_dict(),
                    'candidates': candidate_scores
                })
    
    return jsonify({'similarity_reviews': similarity_reviews}), 200

@admin_bp.route('/api/admin/report/<int:report_id>/approve', methods=['POST'])
def approve_report(report_id):
    """Approve a flagged report"""
    auth_error = require_admin()
    if auth_error:
        return auth_error
    
    report = Report.query.get_or_404(report_id)
    
    if report.verification_state != 'Flagged for Admin Review':
        return jsonify({'error': 'Report is not flagged for review'}), 400
    
    # Approve the report
    report.verification_state = 'Verified'
    db.session.commit()
    
    # Emit update
    emit_report_verification_updated(report)
    
    # Process similarity matching
    from services.similarity import process_similarity_matching
    action, incident_id, similarity_score, candidates = process_similarity_matching(report)
    
    if action == 'auto_merge':
        incident = Incident.query.get(incident_id)
        report.incident_id = incident_id
        db.session.commit()
        update_incident_scores(incident)
        emit_incident_updated(incident)
    elif action == 'new_incident':
        incident = Incident(
            category=report.category,
            latitude=report.reported_lat,
            longitude=report.reported_lng
        )
        db.session.add(incident)
        db.session.flush()
        report.incident_id = incident.id
        db.session.commit()
        update_incident_scores(incident)
        emit_incident_created(incident)
    
    return jsonify({'success': True, 'report': report.to_dict()}), 200

@admin_bp.route('/api/admin/report/<int:report_id>/reject', methods=['POST'])
def reject_report(report_id):
    """Reject a flagged report"""
    auth_error = require_admin()
    if auth_error:
        return auth_error
    
    report = Report.query.get_or_404(report_id)
    
    if report.verification_state != 'Flagged for Admin Review':
        return jsonify({'error': 'Report is not flagged for review'}), 400
    
    # Reject the report
    report.verification_state = 'Not Verified'
    db.session.commit()
    
    # Emit update
    emit_report_verification_updated(report)
    
    return jsonify({'success': True, 'report': report.to_dict()}), 200

@admin_bp.route('/api/admin/incident/<int:incident_id>/resolve', methods=['POST'])
def resolve_incident(incident_id):
    """Resolve or unresolve an incident"""
    auth_error = require_admin()
    if auth_error:
        return auth_error
    
    incident = Incident.query.get_or_404(incident_id)
    data = request.get_json()
    
    resolution_status = data.get('resolution_status', 'Resolved')
    if resolution_status not in ['Resolved', 'Unresolved']:
        return jsonify({'error': 'Invalid resolution_status. Must be "Resolved" or "Unresolved"'}), 400
    
    incident.resolution_status = resolution_status
    db.session.commit()
    
    # Emit update
    emit_incident_resolved(incident)
    
    return jsonify({'success': True, 'incident': incident.to_dict(include_reports=True)}), 200

