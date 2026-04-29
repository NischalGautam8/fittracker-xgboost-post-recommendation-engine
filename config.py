import os
from dotenv import load_dotenv

load_dotenv()

ACTIVITIES_MONGO_URI = os.getenv("ACTIVITIES_MONGO_URI")
POSTS_MONGO_URI = os.getenv("POSTS_MONGO_URI")
PORT = int(os.getenv("PORT", 8000))
MODEL_PATH = os.getenv("MODEL_PATH", "models/xgboost_model.json")
