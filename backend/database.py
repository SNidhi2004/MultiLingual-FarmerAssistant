from pymongo import MongoClient, ASCENDING
from config import MONGO_URI

client = MongoClient(MONGO_URI)

db = client["farmer_assistant"]

# -------------------------------
# Collections
# -------------------------------
users_col = db["users"]
sessions_col = db["sessions"]
images_col = db["images"]

# -------------------------------
# Indexes (IMPORTANT)
# -------------------------------

# Users: unique usernames
users_col.create_index(
    [("username", ASCENDING)],
    unique=True
)

# Sessions: lookup by user
sessions_col.create_index(
    [("user_id", ASCENDING)]
)

# Sessions: auto-expire after 6 hours
sessions_col.create_index(
    [("created_at", ASCENDING)],
    expireAfterSeconds=6 * 60 * 60
)

# Images: lookup by session
images_col.create_index(
    [("session_id", ASCENDING)]
)
