import xgboost as xgb
import numpy as np
import pandas as pd
import os

class XGBoostRecommender:
    def __init__(self, model_path="models/xgboost_model.json"):
        self.model_path = model_path
        self.model = None
        self.feature_names = [
            "activity_type_match", "activity_type_frequency", 
            "calories_diff_ratio", "duration_diff_ratio", 
            "heartrate_diff_ratio", "spo2_diff", 
            "bp_systolic_diff", "bp_diastolic_diff", 
            "intensity_bracket_match", "user_avg_calories", 
            "user_avg_duration", "user_avg_heartrate", 
            "user_activity_count", "post_calories", 
            "post_duration", "post_heartrate", "post_age_hours"
        ]
        
    def load(self):
        try:
            if os.path.exists(self.model_path):
                self.model = xgb.Booster()
                self.model.load_model(self.model_path)
                print("XGBoost model successfully loaded!")
                return True
            else:
                print(f"XGBoost model path {self.model_path} does not exist.")
                return False
        except Exception as e:
            print(f"Error loading XGBoost model: {e}")
            return False
        
    def train(self, X_df: pd.DataFrame, y: pd.Series):
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        # Align features
        X = X_df[self.feature_names]
        
        dtrain = xgb.DMatrix(X, label=y, feature_names=self.feature_names)
        
        params = {
            'objective': 'binary:logistic',
            'eval_metric': 'auc',
            'max_depth': 4,
            'eta': 0.1,
            'tree_method': 'hist'
        }
        
        self.model = xgb.train(params, dtrain, num_boost_round=50)
        self.model.save_model(self.model_path)
        
    def predict_relevance(self, X_df: pd.DataFrame) -> np.ndarray:
        if self.model is None:
            # Fallback if model not trained: basic heuristic score
            heuristic_scores = X_df['activity_type_match'] * 0.5 + X_df['intensity_bracket_match'] * 0.3 + (1.0 - np.clip(X_df['calories_diff_ratio'], 0, 1)) * 0.2
            return heuristic_scores.values
            
        X = X_df[self.feature_names]
        dtest = xgb.DMatrix(X, feature_names=self.feature_names)
        return self.model.predict(dtest)
