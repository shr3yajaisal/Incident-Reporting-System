import math

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    Returns distance in meters
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in meters
    r = 6371000
    
    return c * r

def geolocation_consistency_score(reported_lat, reported_lng, device_lat, device_lng):
    """
    Calculate geolocation consistency score between reported location and device location
    Returns score between 0 and 1
    """
    if device_lat is None or device_lng is None:
        # No device location available, return neutral score
        return 0.5
    
    distance = haversine_distance(reported_lat, reported_lng, device_lat, device_lng)
    
    # Score decreases as distance increases
    # Perfect match (0m) = 1.0
    # 100m = 0.9
    # 500m = 0.5
    # 1000m+ = 0.0
    if distance <= 50:
        return 1.0
    elif distance <= 100:
        return 0.9
    elif distance <= 200:
        return 0.7
    elif distance <= 500:
        return 0.5
    elif distance <= 1000:
        return 0.3
    else:
        return 0.1

