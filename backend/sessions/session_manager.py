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


# -------------------------------
# ADD IMAGE  (now also stores user_id)
# -------------------------------
def add_image(user_id, image_bytes, disease, confidence):
    session_id = create_or_get_session(user_id)

    image_url = upload_image_to_blob(image_bytes)
    thumbnail = generate_thumbnail(image_bytes)

    image_id = images_col.insert_one({
        "user_id": ObjectId(user_id),        # ✅ NEW
        "session_id": session_id,
        "image_url": image_url,
        "thumbnail": thumbnail,
        "disease": disease,
        "confidence": confidence,
        "qa_history": [],
        "created_at": datetime.utcnow()
    }).inserted_id

    sessions_col.update_one(
        {"_id": session_id},
        {"$set": {"current_image_id": image_id}}
    )

    # Keep only last 3 images FOR LLM CONTEXT (session only)
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
        "user_id": ObjectId(user_id)
    })

    if not image:
        return None

    sessions_col.update_one(
        {"_id": session["_id"]},
        {"$set": {"current_image_id": image["_id"]}}
    )

    return image


# -------------------------------
# UPDATED add_qa
# -------------------------------
def add_qa(
    user_id,
    question_en,
    answer_en,
    question_user,
    answer_user,
    language
):
    image = get_current_image(user_id)

    images_col.update_one(
        {"_id": image["_id"]},
        {"$push": {
            "qa_history": {
                "$each": [{
                    "question_en": question_en,
                    "answer_en": answer_en,
                    "question_user": question_user,
                    "answer_user": answer_user,
                    "language": language,
                    "timestamp": datetime.utcnow()
                }],
                "$slice": -MAX_QA_PER_IMAGE
            }
        }}
    )


# -------------------------------
# Used by dashboard (still session based)
# -------------------------------
def get_recent_images(user_id):
    session = get_active_session(user_id)
    if not session:
        return []

    return list(
        images_col.find({"session_id": session["_id"]})
        .sort("created_at", -1)
        .limit(MAX_IMAGES_PER_SESSION)
    )


# -------------------------------
# NEW – history across sessions
# -------------------------------
def get_user_history(user_id):
    return list(
        images_col.find(
            {"user_id": ObjectId(user_id)}
        )
        .sort("created_at", -1)
        .limit(MAX_IMAGES_PER_SESSION)
    )


def reset_session(user_id):
    session = get_active_session(user_id)
    if not session:
        return False

    sessions_col.update_one(
        {"_id": session["_id"]},
        {"$set": {"is_active": False, "current_image_id": None}}
    )

    return True

from bson import ObjectId
from database import sessions_col, images_col


def get_user_history(user_id):
    session = get_active_session(user_id)
    if not session:
        return []

    return list(
        images_col.find({"session_id": session["_id"]})
        .sort("created_at", -1)
    )
