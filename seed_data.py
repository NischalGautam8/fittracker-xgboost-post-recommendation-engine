from database import activities_db
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import random

users = [ObjectId('69e84a341e22dcb129b92415'), ObjectId('69e878fa59c847eff1aa69e8')]
activity_types = ["Running", "Cycling", "Swimming", "Yoga", "HIIT", "Walking"]

activities = []

for user in users:
    # Generate 15 activities for each user
    for i in range(15):
        act_type = random.choice(activity_types)
        duration = random.randint(20, 90)
        
        # Correlate calories with duration & intensity
        if act_type in ["HIIT", "Running"]:
            calories = duration * random.randint(10, 15)
            hr = random.randint(140, 180)
            bp_sys = random.randint(130, 150)
            bp_dia = random.randint(80, 95)
        else:
            calories = duration * random.randint(4, 8)
            hr = random.randint(90, 130)
            bp_sys = random.randint(110, 130)
            bp_dia = random.randint(70, 85)
            
        act = {
            "activityType": act_type,
            "caloriesBurned": calories,
            "duration": duration,
            "heartRate": hr,
            "bloodOxygenLevel": random.randint(95, 99),
            "systolicBloodPressure": bp_sys,
            "diastolicBloodPressure": bp_dia,
            "date": datetime.now() - timedelta(days=random.randint(0, 30)),
            "createdBy": user
        }
        activities.append(act)

try:
    result = activities_db['activities'].insert_many(activities)
    print(f"Successfully seeded {len(result.inserted_ids)} activities!")
except Exception as e:
    print(f"Failed to seed activities: {e}")
