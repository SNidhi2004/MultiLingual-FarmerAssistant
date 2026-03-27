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

# Background TTL drop logic to prevent auto-deletion of documents
for collection in [sessions_col, images_col]:
    try:
        indexes = collection.index_information()
        for index_name, index_info in indexes.items():
            if 'expireAfterSeconds' in index_info:
                print(f"Dropping hidden TTL index {index_name} from {collection.name}")
                collection.drop_index(index_name)
    except Exception as e:
        print(f"Error verifying indexes on {collection.name}: {e}")

users_col.create_index([("username", ASCENDING)],unique=True)

sessions_col.create_index([("user_id", ASCENDING)])
sessions_col.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
images_col.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
images_col.create_index([("session_id", ASCENDING)])
sessions_col.create_index([("user_id", ASCENDING), ("is_active", ASCENDING)])