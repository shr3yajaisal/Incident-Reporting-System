from extensions import db
from models.incident import Incident
from models.report import Report
from utils.geo import haversine_distance
from utils.time_utils import is_within_temporal_window, temporal_proximity_score
from utils.text_embed import text_similarity
from services.vision_stub import evidence_overlap_score
from config import Config

def find_candidate_incidents(report):
    """
    Find candidate incidents for similarity matching
    Criteria:
    - Same category
    - Within spatial radius (300m)
    - Within temporal window (1 hour)
    """
    candidates = []
    
    # Get all incidents with same category
    incidents = Incident.query.filter_by(category=report.category).all()
    
    for incident in incidents:
        # Check spatial proximity
        distance = haversine_distance(
            report.reported_lat,
            report.reported_lng,
            incident.latitude,
            incident.longitude
        )
        
        if distance > Config.SPATIAL_RADIUS_METERS:
            continue
        
        # Check temporal proximity using incident's most recent report
        if incident.reports:
            # Use the most recent report's reported_time
            most_recent_report = max(incident.reports, key=lambda r: r.reported_time)
            
            if is_within_temporal_window(
                report.reported_time,
                most_recent_report.reported_time,
                Config.TEMPORAL_WINDOW_HOURS
            ):
                candidates.append(incident)
    
    return candidates

def calculate_similarity_score(report, incident):
    """
    Calculate similarity score between a report and an incident
    Components:
    - Spatial proximity (0.35)
    - Temporal proximity (0.25)
    - Category match (0.20) - always 1.0 if we're comparing
    - Description similarity via MiniLM (0.15)
    - Evidence overlap (0.05)
    
    Returns score between 0 and 1
    """
    # 1. Spatial proximity (35%)
    distance = haversine_distance(
        report.reported_lat,
        report.reported_lng,
        incident.latitude,
        incident.longitude
    )
    
    # Normalize distance to 0-1 score (inverse: closer = higher score)
    max_distance = Config.SPATIAL_RADIUS_METERS
    spatial_score = max(0.0, 1.0 - (distance / max_distance))
    
    # 2. Temporal proximity (25%)
    if incident.reports:
        most_recent_report = max(incident.reports, key=lambda r: r.reported_time)
        temporal_score = temporal_proximity_score(
            report.reported_time,
            most_recent_report.reported_time,
            Config.TEMPORAL_WINDOW_HOURS
        )
    else:
        temporal_score = 0.0
    
    # 3. Category match (20%) - always 1.0 since we filter by category
    category_score = 1.0
    
    # 4. Description similarity (15%)
    # Compare with the most similar report in the incident
    if incident.reports:
        best_text_similarity = 0.0
        for existing_report in incident.reports:
            sim = text_similarity(report.description, existing_report.description)
            best_text_similarity = max(best_text_similarity, sim)
        text_score = best_text_similarity
    else:
        text_score = 0.0
    
    # 5. Evidence overlap (5%)
    if incident.reports and report.evidence_path:
        best_evidence_overlap = 0.0
        for existing_report in incident.reports:
            if existing_report.evidence_path:
                overlap = evidence_overlap_score(
                    report.evidence_path,
                    existing_report.evidence_path
                )
                best_evidence_overlap = max(best_evidence_overlap, overlap)
        evidence_score = best_evidence_overlap
    else:
        evidence_score = 0.0
    
    # Weighted sum
    similarity_score = (
        0.35 * spatial_score +
        0.25 * temporal_score +
        0.20 * category_score +
        0.15 * text_score +
        0.05 * evidence_score
    )
    
    return similarity_score

def process_similarity_matching(report):
    """
    Process similarity matching for a verified report
    Returns:
    - (action, incident_id, similarity_score, candidates)
    where action is 'auto_merge', 'review', or 'new_incident'
    """
    candidates = find_candidate_incidents(report)
    
    if not candidates:
        return ('new_incident', None, 0.0, [])
    
    # Calculate similarity scores for all candidates
    candidate_scores = []
    for candidate in candidates:
        score = calculate_similarity_score(report, candidate)
        candidate_scores.append({
            'incident': candidate,
            'score': score
        })
    
    # Sort by score descending
    candidate_scores.sort(key=lambda x: x['score'], reverse=True)
    
    best_match = candidate_scores[0]
    best_score = best_match['score']
    
    # Decision logic
    if best_score >= Config.SIMILARITY_AUTO_MERGE_THRESHOLD:
        # Auto-merge into best matching incident
        return ('auto_merge', best_match['incident'].id, best_score, candidate_scores)
    elif best_score >= Config.SIMILARITY_REVIEW_THRESHOLD:
        # Admin review needed
        return ('review', None, best_score, candidate_scores)
    else:
        # Create new incident
        return ('new_incident', None, best_score, candidate_scores)

