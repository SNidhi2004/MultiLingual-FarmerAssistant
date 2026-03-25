from pymongo import MongoClient, ASCENDING, DESCENDING
from config import MONGO_URI

client = MongoClient(MONGO_URI)

db = client["farmer_assistant"]

# -------------------------------
# Collections
# -------------------------------
users_col = db["users"]
sessions_col = db["sessions"]
images_col = db["images"]

# Indexes (CORRECTED)

users_col.create_index([("username", ASCENDING)],unique=True)

sessions_col.create_index([("user_id", ASCENDING)])
sessions_col.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
images_col.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
images_col.create_index([("session_id", ASCENDING)])
sessions_col.create_index([("user_id", ASCENDING), ("is_active", ASCENDING)])