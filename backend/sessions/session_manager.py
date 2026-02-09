from bson import ObjectId
from datetime import datetime
from database import sessions_col, images_col
from config import MAX_IMAGES_PER_SESSION, MAX_QA_PER_IMAGE
from utils.image_utils import generate_thumbnail
from services.blob_storage import upload_image_to_blob

def get_active_session(user_id):
    return sessions_col.find_one({
        "user_id": ObjectId(user_id),
        "is_active": True
    })

def create_or_get_session(user_id):
    session = get_active_session(user_id)
    if session:
        return session["_id"]

    result = sessions_col.insert_one({
        "user_id": ObjectId(user_id),
        "current_image_id": None,
        "is_active": True,
        "created_at": datetime.utcnow()
    })
    return result.inserted_id

def add_image(user_id, image_bytes, disease, confidence):
    session_id = create_or_get_session(user_id)

    # 1. Upload original image to Azure Blob
    image_url = upload_image_to_blob(image_bytes)

    # 2. Generate thumbnail (still local, small)
    thumbnail = generate_thumbnail(image_bytes)

    # 3. Store metadata in MongoDB
    image_id = images_col.insert_one({
        "session_id": session_id,
        "image_url": image_url,      # ✅ URL instead of bytes
        "thumbnail": thumbnail,
        "disease": disease,
        "confidence": confidence,
        "qa_history": [],
        "created_at": datetime.utcnow()
    }).inserted_id

    # 4. Set current image
    sessions_col.update_one(
        {"_id": session_id},
        {"$set": {"current_image_id": image_id}}
    )

    # 5. Enforce last 3 images
    images = list(
        images_col.find({"session_id": session_id})
        .sort("created_at", 1)
    )

    if len(images) > MAX_IMAGES_PER_SESSION:
        for img in images[:-MAX_IMAGES_PER_SESSION]:
            images_col.delete_one({"_id": img["_id"]})

    return image_id


def get_current_image(user_id):
    session = get_active_session(user_id)
    if not session or not session.get("current_image_id"):
        return None

    return images_col.find_one({"_id": session["current_image_id"]})

def switch_image(user_id, image_id):
    session = get_active_session(user_id)
    image = images_col.find_one({
        "_id": ObjectId(image_id),
        "session_id": session["_id"]
    })

    if not image:
        return None

    sessions_col.update_one(
        {"_id": session["_id"]},
        {"$set": {"current_image_id": image["_id"]}}
    )
    return image

def add_qa(user_id, question, answer):
    image = get_current_image(user_id)

    images_col.update_one(
        {"_id": image["_id"]},
        {"$push": {
            "qa_history": {
                "$each": [{
                    "question": question,
                    "answer": answer,
                    "timestamp": datetime.utcnow()
                }],
                "$slice": -MAX_QA_PER_IMAGE
            }
        }}
    )

def get_recent_images(user_id):
    session = get_active_session(user_id)
    if not session:
        return []

    return list(
        images_col.find({"session_id": session["_id"]})
        .sort("created_at", -1)
        .limit(MAX_IMAGES_PER_SESSION)
    )

def reset_session(user_id):
    session = get_active_session(user_id)
    if not session:
        return False

    sessions_col.update_one(
        {"_id": session["_id"]},
        {
            "$set": {
                "is_active": False,
                "current_image_id": None
            }
        }
    )
    return True
