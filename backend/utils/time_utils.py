from datetime import datetime, timedelta

def temporal_validity_score(reported_time, submission_time):
    """
    Calculate temporal validity score based on time difference
    between reported_time and submission_time
    Returns score between 0 and 1
    """
    if not reported_time or not submission_time:
        return 0.5
    
    # Ensure both are datetime objects
    if isinstance(reported_time, str):
        reported_time = datetime.fromisoformat(reported_time.replace('Z', '+00:00'))
    if isinstance(submission_time, str):
        submission_time = datetime.fromisoformat(submission_time.replace('Z', '+00:00'))
    
    # Calculate time difference
    time_diff = abs((submission_time - reported_time).total_seconds())
    
    # Score decreases as time difference increases
    # 0-5 minutes = 1.0
    # 5-15 minutes = 0.9
    # 15-30 minutes = 0.7
    # 30-60 minutes = 0.5
    # 1-2 hours = 0.3
    # 2+ hours = 0.1
    if time_diff <= 300:  # 5 minutes
        return 1.0
    elif time_diff <= 900:  # 15 minutes
        return 0.9
    elif time_diff <= 1800:  # 30 minutes
        return 0.7
    elif time_diff <= 3600:  # 1 hour
        return 0.5
    elif time_diff <= 7200:  # 2 hours
        return 0.3
    else:
        return 0.1

def is_within_temporal_window(time1, time2, window_hours=1):
    """
    Check if two datetime objects are within the specified temporal window
    """
    if not time1 or not time2:
        return False
    
    if isinstance(time1, str):
        time1 = datetime.fromisoformat(time1.replace('Z', '+00:00'))
    if isinstance(time2, str):
        time2 = datetime.fromisoformat(time2.replace('Z', '+00:00'))
    
    time_diff = abs((time1 - time2).total_seconds())
    return time_diff <= (window_hours * 3600)

def temporal_proximity_score(time1, time2, window_hours=1):
    """
    Calculate temporal proximity score between two times
    Returns score between 0 and 1
    """
    if not is_within_temporal_window(time1, time2, window_hours):
        return 0.0
    
    if isinstance(time1, str):
        time1 = datetime.fromisoformat(time1.replace('Z', '+00:00'))
    if isinstance(time2, str):
        time2 = datetime.fromisoformat(time2.replace('Z', '+00:00'))
    
    time_diff = abs((time1 - time2).total_seconds())
    max_diff = window_hours * 3600
    
    # Score is 1.0 when times are identical, decreases linearly to 0.0 at window boundary
    return 1.0 - (time_diff / max_diff)

