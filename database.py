from pymongo import MongoClient
from bson.objectid import ObjectId
from config import ACTIVITIES_MONGO_URI, POSTS_MONGO_URI

# Client for Activities with short timeout
activities_client = MongoClient(ACTIVITIES_MONGO_URI, serverSelectionTimeoutMS=5000)
# Client for Posts with short timeout
posts_client = MongoClient(POSTS_MONGO_URI, serverSelectionTimeoutMS=5000)

def get_activities_db():
    try:
        db_names = activities_client.list_database_names()
        for name in ['mern', 'test', 'fit-tracker']:
            if name in db_names:
                if 'activities' in activities_client[name].list_collection_names():
                    return activities_client[name]
        # Try finding any DB with activities
        for name in db_names:
            if name not in ['admin', 'local', 'config'] and 'activities' in activities_client[name].list_collection_names():
                return activities_client[name]
    except Exception as e:
        print(f"Error listing activities DB names: {e}")
        
    # Fallback
    try:
        default_db = activities_client.get_default_database()
        return default_db if default_db is not None else activities_client['mern']
    except:
        return activities_client['mern']

def get_posts_db():
    try:
        db_names = posts_client.list_database_names()
        for name in ['recommendations', 'test', 'fit-tracker']:
            if name in db_names:
                if 'posts' in posts_client[name].list_collection_names():
                    return posts_client[name]
        # Try finding any DB with posts
        for name in db_names:
            if name not in ['admin', 'local', 'config'] and 'posts' in posts_client[name].list_collection_names():
                return posts_client[name]
    except Exception as e:
        print(f"Error listing posts DB names: {e}")
        
    # Fallback
    try:
        default_db = posts_client.get_default_database()
        return default_db if default_db is not None else posts_client['recommendations']
    except:
        return posts_client['recommendations']

activities_db = get_activities_db()
posts_db = get_posts_db()

def get_user_activities(user_id: str):
    try:
        activities = list(activities_db['activities'].find({"createdBy": ObjectId(user_id)}))
        return activities
    except Exception as e:
        print(f"Error fetching activities for user {user_id}: {e}")
        return []

def get_all_posts():
    try:
        posts = list(posts_db['posts'].find())
        return posts
    except Exception as e:
        print(f"Error fetching all posts: {e}")
        return []

def get_all_activities():
    try:
        return list(activities_db['activities'].find())
    except Exception as e:
        print(f"Error fetching all activities: {e}")
        return []
