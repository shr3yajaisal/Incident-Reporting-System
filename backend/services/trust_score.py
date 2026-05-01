from utils.geo import geolocation_consistency_score
from utils.time_utils import temporal_validity_score
from services.vision_stub import analyze_evidence

# High-risk categories that should have a bias boost
HIGH_RISK_CATEGORIES = {
    'Fire': 0.9,
    'Medical Emergency': 0.9,
    'Crime': 0.8,
    'Accident': 0.8,
    'Natural Disaster': 0.9,
}

def calculate_category_bias(category):
    """
    Calculate category bias score based on high-risk categories
    Returns score between 0.5 and 1.0
    """
    return HIGH_RISK_CATEGORIES.get(category, 0.5)

def calculate_completeness_score(description, evidence_path, device_lat, device_lng):
    """
    Calculate report completeness score
    Returns score between 0 and 1
    """
    score = 0.0
    
    # Description presence and length
    if description and len(description.strip()) > 0:
        score += 0.4
        if len(description.strip()) >= 50:
            score += 0.2  # Bonus for detailed description
    
    # Evidence presence
    if evidence_path:
        score += 0.3
    
    # Device location presence
    if device_lat is not None and device_lng is not None:
        score += 0.1
    
    return min(1.0, score)

def calculate_trust_score(report):
    """
    Calculate trust score for a report based on 5 factors:
    1. Evidence consistency (0.30)
    2. Geolocation consistency (0.25)
    3. High-risk category bias (0.15)
    4. Temporal validity (0.15)
    5. Report completeness (0.15)
    
    Returns trust score between 0 and 1
    """
    # 1. Evidence consistency (30%)
    evidence_score = analyze_evidence(
        report.evidence_path,
        report.category,
        report.description
    )
    
    # 2. Geolocation consistency (25%)
    geo_score = geolocation_consistency_score(
        report.reported_lat,
        report.reported_lng,
        report.device_lat,
        report.device_lng
    )
    
    # 3. Category bias (15%)
    category_score = calculate_category_bias(report.category)
    
    # 4. Temporal validity (15%)
    temporal_score = temporal_validity_score(
        report.reported_time,
        report.submission_time
    )
    
    # 5. Completeness (15%)
    completeness_score = calculate_completeness_score(
        report.description,
        report.evidence_path,
        report.device_lat,
        report.device_lng
    )
    
    # Weighted sum
    trust_score = (
        0.30 * evidence_score +
        0.25 * geo_score +
        0.15 * category_score +
        0.15 * temporal_score +
        0.15 * completeness_score
    )
    
    return trust_score

