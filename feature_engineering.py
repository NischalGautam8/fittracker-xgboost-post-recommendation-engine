import pandas as pd
import numpy as np
from datetime import datetime, timezone

def compute_intensity_bracket(calories: float, duration: float) -> str:
    if not duration or duration <= 0:
        return "Low"
    cal_per_min = calories / duration
    if cal_per_min < 5:
        return "Low"
    elif cal_per_min < 10:
        return "Moderate"
    elif cal_per_min < 15:
        return "High"
    else:
        return "Extreme"

def build_user_profile(user_activities: list) -> dict:
    if not user_activities:
        return {
            "user_avg_calories": 0.0,
            "user_avg_duration": 0.0,
            "user_avg_heartrate": 0.0,
            "user_avg_spo2": 95.0,
            "user_avg_systolic": 120.0,
            "user_avg_diastolic": 80.0,
            "user_activity_count": 0,
            "user_distinct_activity_types": 0,
            "user_days_since_last_activity": 30.0,
            "user_preferred_intensity": "Moderate",
            "activity_type_counts": {}
        }
    
    df = pd.DataFrame(user_activities)
    
    # Parse dates
    df['date'] = pd.to_datetime(df['date'])
    now = datetime.now(timezone.utc)
    df['days_ago'] = (now - df['date'].dt.tz_localize('UTC' if df['date'].dt.tz is None else None)).dt.total_seconds() / (24 * 3600)
    
    profile = {
        "user_avg_calories": float(df['caloriesBurned'].mean()) if 'caloriesBurned' in df else 0.0,
        "user_avg_duration": float(df['duration'].mean()) if 'duration' in df else 0.0,
        "user_avg_heartrate": float(df['heartRate'].mean()) if 'heartRate' in df else 0.0,
        "user_avg_spo2": float(df['bloodOxygenLevel'].mean()) if 'bloodOxygenLevel' in df else 95.0,
        "user_avg_systolic": float(df['systolicBloodPressure'].mean()) if 'systolicBloodPressure' in df else 120.0,
        "user_avg_diastolic": float(df['diastolicBloodPressure'].mean()) if 'diastolicBloodPressure' in df else 80.0,
        "user_activity_count": len(df),
        "user_distinct_activity_types": df['activityType'].nunique() if 'activityType' in df else 0,
        "user_days_since_last_activity": float(df['days_ago'].min()) if 'days_ago' in df else 30.0
    }
    
    # Determine preferred intensity
    if 'caloriesBurned' in df and 'duration' in df:
        df['intensity'] = df.apply(lambda row: compute_intensity_bracket(row['caloriesBurned'], row['duration']), axis=1)
        profile['user_preferred_intensity'] = df['intensity'].mode().iloc[0] if not df['intensity'].mode().empty else "Moderate"
    else:
        profile['user_preferred_intensity'] = "Moderate"
        
    # Activity type frequency
    if 'activityType' in df:
        type_counts = df['activityType'].value_counts(normalize=True).to_dict()
        profile['activity_type_counts'] = {str(k): float(v) for k, v in type_counts.items()}
    else:
        profile['activity_type_counts'] = {}
        
    return profile

def build_pair_features(user_profile: dict, post: dict) -> dict:
    post_type = post.get('activityType', 'Unknown')
    post_calories = float(post.get('caloriesBurned', 0.0))
    post_duration = float(post.get('duration', 0.0))
    post_heartrate = float(post.get('heartRate', 0.0))
    post_spo2 = float(post.get('bloodOxygenLevel', 95.0))
    post_systolic = float(post.get('systolicBloodPressure', 120.0))
    post_diastolic = float(post.get('diastolicBloodPressure', 80.0))
    
    # 1. Activity Type Affinity
    activity_type_match = 1.0 if post_type in user_profile['activity_type_counts'] else 0.0
    activity_type_frequency = user_profile['activity_type_counts'].get(post_type, 0.0)
    
    # 2. Health Metric Similarity (Ratio/Diff)
    def safe_diff_ratio(user_val, post_val):
        if user_val == 0:
            return abs(post_val)
        return abs(post_val - user_val) / user_val
        
    calories_diff_ratio = safe_diff_ratio(user_profile['user_avg_calories'], post_calories)
    duration_diff_ratio = safe_diff_ratio(user_profile['user_avg_duration'], post_duration)
    heartrate_diff_ratio = safe_diff_ratio(user_profile['user_avg_heartrate'], post_heartrate)
    spo2_diff = abs(user_profile['user_avg_spo2'] - post_spo2)
    bp_systolic_diff = abs(user_profile['user_avg_systolic'] - post_systolic)
    bp_diastolic_diff = abs(user_profile['user_avg_diastolic'] - post_diastolic)
    
    # 3. Bracket Matching
    post_intensity = compute_intensity_bracket(post_calories, post_duration)
    intensity_bracket_match = 1.0 if post_intensity == user_profile['user_preferred_intensity'] else 0.0
    
    # 4. Post Age
    post_created = post.get('createdAt', datetime.now(timezone.utc))
    if isinstance(post_created, str):
        try:
            post_created = datetime.fromisoformat(post_created.replace('Z', '+00:00'))
        except ValueError:
            post_created = datetime.now(timezone.utc)
            
    post_age_hours = (datetime.now(timezone.utc) - post_created.replace(tzinfo=timezone.utc) if post_created.tzinfo is None else (datetime.now(timezone.utc) - post_created)).total_seconds() / 3600
    
    features = {
        "activity_type_match": activity_type_match,
        "activity_type_frequency": activity_type_frequency,
        "calories_diff_ratio": calories_diff_ratio,
        "duration_diff_ratio": duration_diff_ratio,
        "heartrate_diff_ratio": heartrate_diff_ratio,
        "spo2_diff": spo2_diff,
        "bp_systolic_diff": bp_systolic_diff,
        "bp_diastolic_diff": bp_diastolic_diff,
        "intensity_bracket_match": intensity_bracket_match,
        "user_avg_calories": user_profile['user_avg_calories'],
        "user_avg_duration": user_profile['user_avg_duration'],
        "user_avg_heartrate": user_profile['user_avg_heartrate'],
        "user_activity_count": user_profile['user_activity_count'],
        "post_calories": post_calories,
        "post_duration": post_duration,
        "post_heartrate": post_heartrate,
        "post_age_hours": max(0.0, float(post_age_hours))
    }
    
    return features
