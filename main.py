from fastapi import FastAPI, HTTPException
from schemas import RecommendRequest, RecommendResponse, RankedPost
from database import get_user_activities, get_all_posts
from feature_engineering import build_user_profile, build_pair_features
from model import XGBoostRecommender
from training import retrain_model
import pandas as pd
import numpy as np
import os

app = FastAPI(title="Fit Tracker Recommendation Engine")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.getenv("MODEL_PATH", os.path.join(BASE_DIR, "models", "xgboost_model.json"))
recommender = XGBoostRecommender(MODEL_PATH)
recommender.load()

@app.get("/api/health")
def health_check():
    model_loaded = recommender.model is not None
    return {"status": "ok", "model_loaded": model_loaded}

@app.post("/api/recommend", response_model=RecommendResponse)
def get_recommendations(req: RecommendRequest):
    try:
        # 1. Fetch user activities
        activities = get_user_activities(req.userId)
        user_prof = build_user_profile(activities)
        
        # 2. Fetch candidate posts
        posts = get_all_posts()
        if not posts:
            return RecommendResponse(posts=[], modelVersion="xgboost_v1.0")
            
        # 3. Generate features for each post
        features_list = []
        post_ids = []
        reasons_list = []
        
        for post in posts:
            post_id = str(post.get('_id'))
            feat = build_pair_features(user_prof, post)
            features_list.append(feat)
            post_ids.append(post_id)
            
            # Build reasons
            reasons = []
            if feat['activity_type_match'] == 1.0:
                reasons.append(f"Matches your activity type: {post.get('activityType')}")
            if feat['intensity_bracket_match'] == 1.0:
                reasons.append("Matches your typical intensity level")
            if feat['calories_diff_ratio'] < 0.2:
                reasons.append("Similar calorie burn target")
                
            reasons_list.append(reasons)
            
        X_df = pd.DataFrame(features_list)
        
        # 4. Score candidates
        scores = recommender.predict_relevance(X_df)
        
        # 5. Sort and rank
        ranked_indices = np.argsort(scores)[::-1]
        
        results = []
        for idx in ranked_indices[:req.limit]:
            results.append(RankedPost(
                postId=post_ids[idx],
                score=float(scores[idx]),
                reasons=reasons_list[idx]
            ))
            
        return RecommendResponse(
            posts=results,
            modelVersion="xgboost_v1.0"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/train")
def trigger_training():
    res = retrain_model(MODEL_PATH)
    if res['status'] == 'success':
        recommender.load()  # Reload newly trained model
        return res
    else:
        raise HTTPException(status_code=400, detail=res['message'])
