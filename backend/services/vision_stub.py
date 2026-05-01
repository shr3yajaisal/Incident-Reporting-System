import random

def analyze_evidence(evidence_path, category, description):
    """
    Stub function for vision API analysis
    Returns evidence consistency score between 0 and 1
    """
    if not evidence_path:
        # No evidence provided
        return 0.3
    
    # Stub logic: simulate evidence analysis
    # In real implementation, this would call a vision API
    
    # Simulate some consistency based on category
    category_keywords = {
        'Fire': ['smoke', 'flame', 'burn', 'fire'],
        'Accident': ['car', 'vehicle', 'crash', 'collision'],
        'Crime': ['person', 'suspicious', 'weapon', 'threat'],
        'Medical': ['person', 'injured', 'ambulance', 'medical'],
    }
    
    # Check if description contains category-related keywords
    description_lower = description.lower()
    keywords = category_keywords.get(category, [])
    
    keyword_match = any(keyword in description_lower for keyword in keywords)
    
    # Base score with some randomness to simulate real analysis
    base_score = 0.7 if keyword_match else 0.5
    noise = random.uniform(-0.1, 0.1)
    
    score = max(0.0, min(1.0, base_score + noise))
    
    return score

def evidence_overlap_score(evidence_path1, evidence_path2):
    """
    Stub function to calculate evidence overlap between two reports
    Returns score between 0 and 1
    """
    if not evidence_path1 or not evidence_path2:
        return 0.0
    
    # Stub: simulate evidence comparison
    # In real implementation, this would compare images/videos
    return random.uniform(0.2, 0.6)

