import pandas as pd
import numpy as np
from database import get_all_activities, get_all_posts
from feature_engineering import build_user_profile, build_pair_features, compute_intensity_bracket
from model import XGBoostRecommender
from collections import defaultdict

def generate_synthetic_data():
    activities = get_all_activities()
    posts = get_all_posts()
    
    if not activities or not posts:
        return pd.DataFrame(), pd.Series()
        
    # Group activities by user
    user_activities = defaultdict(list)
    for act in activities:
        if 'createdBy' in act:
            user_activities[str(act['createdBy'])].append(act)
            
    features_list = []
    labels = []
    
    for user_id, acts in user_activities.items():
        user_prof = build_user_profile(acts)
        
        for post in posts:
            feat = build_pair_features(user_prof, post)
            features_list.append(feat)
            
            # Synthetic labeling heuristics
            is_relevant = 0
            if feat['activity_type_match'] == 1.0:
                is_relevant = 1
            elif feat['intensity_bracket_match'] == 1.0 and feat['calories_diff_ratio'] < 0.3:
                is_relevant = 1
            elif feat['activity_type_frequency'] > 0.4:
                is_relevant = 1
                
            labels.append(is_relevant)
            
    X_df = pd.DataFrame(features_list)
    y = pd.Series(labels)
    return X_df, y

def retrain_model(model_path: str):
    recommender = XGBoostRecommender(model_path)
    X_df, y = generate_synthetic_data()
    
    if X_df.empty:
        return {"status": "failed", "message": "Not enough data for training"}
        
    recommender.train(X_df, y)
    return {"status": "success", "trained_samples": len(X_df)}
