from extensions import db
from models.incident import Incident
from models.report import Report

# Category severity weights
CATEGORY_SEVERITY = {
    'Fire': 0.9,
    'Medical Emergency': 0.9,
    'Natural Disaster': 0.9,
    'Crime': 0.8,
    'Accident': 0.7,
    'Infrastructure': 0.6,
    'Other': 0.5,
}

def calculate_confidence_score(incident):
    """
    Calculate confidence score as average trust score of VERIFIED reports
    """
    verified_reports = [r for r in incident.reports if r.verification_state == 'Verified']
    
    if not verified_reports:
        return 0.0
    
    total_trust = sum(r.trust_score for r in verified_reports)
    return total_trust / len(verified_reports)

def calculate_priority_score(incident):
    """
    Calculate priority score based on:
    - Category severity
    - Number of verified reports
    - Contextual weighting (stub)
    """
    # Base category severity
    category_severity = CATEGORY_SEVERITY.get(incident.category, 0.5)
    
    # Verified reports count factor
    verified_count = len([r for r in incident.reports if r.verification_state == 'Verified'])
    report_factor = min(1.0, verified_count / 5.0)  # Normalize to 0-1, max at 5 reports
    
    # Contextual weighting (stub - could be based on time of day, location, etc.)
    contextual_weight = 0.7  # Stub value
    
    # Weighted combination
    priority_score = (
        0.5 * category_severity +
        0.3 * report_factor +
        0.2 * contextual_weight
    )
    
    return priority_score

def get_priority_label(priority_score):
    """
    Convert priority score to label
    """
    if priority_score >= 0.8:
        return 'Critical'
    elif priority_score >= 0.6:
        return 'High'
    elif priority_score >= 0.4:
        return 'Medium'
    else:
        return 'Low'

def update_incident_scores(incident):
    """
    Update confidence score, priority score, and priority label for an incident
    """
    incident.confidence_score = calculate_confidence_score(incident)
    incident.priority_score = calculate_priority_score(incident)
    incident.priority_label = get_priority_label(incident.priority_score)
    
    db.session.commit()

