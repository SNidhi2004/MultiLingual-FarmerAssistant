from bson import ObjectId
from datetime import datetime, timezone
from database import sessions_col, images_col
from config import MAX_IMAGES_PER_SESSION, MAX_QA_PER_IMAGE
from utils.image_utils import generate_thumbnail
from services.blob_storage import upload_image_to_blob
import uuid


# -------------------------------
# SESSION MANAGEMENT
# -------------------------------

def get_active_session(user_id):
    """Get user's current active session"""
    return sessions_col.find_one({
        "user_id": ObjectId(user_id),
        "is_active": True
    })


def create_new_session(user_id):
    """Create a new session and archive any existing active one"""

    # First, archive any existing active session
    archive_active_session(user_id)

    # Create new session with unique session_id string
    session_uuid = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    session = {
        "user_id": ObjectId(user_id),
        "session_id": session_uuid,   # String UUID for easy reference
        "is_active": True,
        "is_archived": False,
        "current_image_id": None,
        "created_at": now,
        "last_active": now,
        "total_images": 0,
        "total_questions": 0
    }

    result = sessions_col.insert_one(session)
    print(f"New session created with UUID: {session_uuid}")
    # FIX: was returning (result.inserted_id, session_id) — session_id was undefined
    return result.inserted_id, session_uuid


def archive_active_session(user_id):
    """Archive the currently active session"""
    result = sessions_col.update_many(
        {
            "user_id": ObjectId(user_id),
            "is_active": True
        },
        {
            "$set": {
                "is_active": False,
                "is_archived": True,
                "last_active": datetime.now(timezone.utc)
            }
        }
    )
    return result.modified_count > 0


def get_session_by_id(session_id):
    """Get session by its string session_id"""
    return sessions_col.find_one({"session_id": session_id})


def resume_session(user_id, session_id, target_image_id=None):
    """Resume an archived session and optionally set a specific active image"""
    try:
        session = sessions_col.find_one({
            "session_id": session_id,
            "user_id": ObjectId(user_id)
        })

        if not session:
            print(f"Session not found: {session_id}")
            return None

        # Archive current active session
        archive_active_session(user_id)

        # Set this session as active
        update_fields = {
            "is_active": True,
            "is_archived": False,
            "last_active": datetime.now(timezone.utc)
        }

        if target_image_id:
            try:
                target_image = images_col.find_one({
                    "_id": ObjectId(target_image_id),
                    "user_id": ObjectId(user_id)
                })
                if target_image:
                    update_fields["current_image_id"] = target_image["_id"]
                    session["current_image_id"] = target_image["_id"]
            except Exception as e:
                print(f"Error finding target image: {e}")

        sessions_col.update_one(
            {"_id": session["_id"]},
            {"$set": update_fields}
        )

        # Get the current image with its full QA history
        current_image = None
        if session.get("current_image_id"):
            current_image = images_col.find_one({"_id": session["current_image_id"]})
            if current_image:
                current_image["_id"] = str(current_image["_id"])
                if current_image.get("session_id"):
                    current_image["session_id"] = str(current_image["session_id"])

        session["current_image"] = current_image
        return session

    except Exception as e:
        print(f"Error in resume_session: {e}")
        import traceback
        traceback.print_exc()
        return None


# -------------------------------
# IMAGE MANAGEMENT
# -------------------------------

def add_image(user_id, image_bytes, disease, confidence):
    """Add a new image to the current session"""

    session = get_active_session(user_id)

    if not session:
        # FIX: create_new_session returns (inserted_id, session_uuid)
        session_db_id, session_uuid = create_new_session(user_id)
        session = sessions_col.find_one({"_id": session_db_id})
        print(f"Created new session with UUID: {session_uuid}")
    else:
        session_uuid = session.get("session_id")
        session_db_id = session["_id"]
        print(f"Using existing session: {session_uuid}")

    # Upload to blob and generate thumbnail
    image_url = upload_image_to_blob(image_bytes)
    thumbnail = generate_thumbnail(image_bytes)

    now = datetime.now(timezone.utc)
    image_doc = {
        "user_id": ObjectId(user_id),
        "session_id": session_db_id,      # MongoDB ObjectId reference
        "session_uuid": session_uuid,     # String UUID for easy lookup
        "image_url": image_url,
        "thumbnail": thumbnail,
        "disease": disease,
        "confidence": confidence,
        "qa_history": [],
        "created_at": now,
        "last_active": now
    }

    image_result = images_col.insert_one(image_doc)
    image_id = image_result.inserted_id

    # Update session with this as current image
    sessions_col.update_one(
        {"_id": session_db_id},
        {
            "$set": {
                "current_image_id": image_id,
                "last_active": now,
                "session_id": session_uuid
            },
            "$inc": {"total_images": 1}
        }
    )

    cleanup_old_images(user_id, max_images=3)
    return image_id


def get_current_image(user_id):
    """Get the current image for user's active session"""
    session = get_active_session(user_id)
    if not session or not session.get("current_image_id"):
        return None
    return images_col.find_one({"_id": session["current_image_id"]})


def switch_image(user_id, image_id):
    """Switch current image in active session"""
    session = get_active_session(user_id)
    if not session:
        return None

    image = images_col.find_one({
        "_id": ObjectId(image_id),
        "user_id": ObjectId(user_id)
    })

    if not image:
        return None

    sessions_col.update_one(
        {"_id": session["_id"]},
        {
            "$set": {
                "current_image_id": image["_id"],
                "last_active": datetime.now(timezone.utc)
            }
        }
    )
    return image


# -------------------------------
# QA MANAGEMENT
# -------------------------------

def add_qa(user_id, question_en, answer_en, question_user, answer_user, language):
    """Add Q&A to current image"""
    image = get_current_image(user_id)
    if not image:
        return False

    now = datetime.now(timezone.utc)

    qa_object = {
        "question_en": question_en,
        "answer_en": answer_en,
        "question_user": question_user,
        "answer_user": answer_user,
        "question": question_user,   # backward compatibility
        "answer": answer_user,       # backward compatibility
        "language": language,
        "timestamp": now
    }

    images_col.update_one(
        {"_id": image["_id"]},
        {
            "$push": {
                "qa_history": {
                    "$each": [qa_object],
                    "$slice": -MAX_QA_PER_IMAGE
                }
            },
            "$set": {"last_active": now}
        }
    )

    session = get_active_session(user_id)
    if session:
        sessions_col.update_one(
            {"_id": session["_id"]},
            {
                "$inc": {"total_questions": 1},
                "$set": {"last_active": now}
            }
        )

    return True


def cleanup_old_images(user_id, max_images=3):
    """Delete oldest images from DB when limit exceeded"""
    old_images = list(
        images_col.find({"user_id": ObjectId(user_id)})
        .sort("created_at", 1)
    )

    if len(old_images) > max_images:
        images_to_delete = old_images[:len(old_images) - max_images]
        for img in images_to_delete:
            # FIX: removed call to delete_blob which doesn't exist in blob_storage.py
            # Just delete from database
            images_col.delete_one({"_id": img["_id"]})
            print(f"Deleted old image: {img['_id']}")


# -------------------------------
# HISTORY RETRIEVAL
# -------------------------------

def get_user_history(user_id, limit=3):
    """Get last 'limit' images across ALL sessions for history view"""
    try:
        print(f"Fetching history for user: {user_id}")

        if isinstance(user_id, str):
            user_id = ObjectId(user_id)

        images = list(
            images_col.find({"user_id": user_id})
            .sort("created_at", -1)
            .limit(limit)
        )

        print(f"Found {len(images)} images")

        history = []
        for idx, img in enumerate(images):
            image_id = str(img.get("_id", ""))
            if not image_id:
                continue

            session_id = img.get("session_uuid")
            if not session_id and img.get("session_id"):
                session = sessions_col.find_one({"_id": img["session_id"]})
                if session:
                    session_id = session.get("session_id")

            created_at = img.get("created_at")
            qa_history = img.get("qa_history", [])

            qa_preview = [
                {
                    "question": qa.get("question_user") or qa.get("question", ""),
                    "answer": qa.get("answer_user") or qa.get("answer", "")
                }
                for qa in qa_history[-2:]
            ]

            history.append({
                "image_id": image_id,
                "session_id": session_id,
                "image_url": img.get("image_url", ""),
                "thumbnail": img.get("thumbnail", ""),
                "disease": img.get("disease", "Unknown"),
                "confidence": float(img.get("confidence", 0)),
                "created_at": created_at.isoformat() if created_at else None,
                "qa_preview": qa_preview,
                "total_qa": len(qa_history)
            })

        print(f"Returning {len(history)} history items")
        return history

    except Exception as e:
        print(f"ERROR in get_user_history: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


def get_session_history(user_id):
    """Get all sessions for user"""
    return list(
        sessions_col.find({"user_id": ObjectId(user_id)})
        .sort("created_at", -1)
    )


def get_image_details(user_id, image_id):
    """Get complete image details including all Q&A"""
    image = images_col.find_one({
        "_id": ObjectId(image_id),
        "user_id": ObjectId(user_id)
    })

    if not image:
        return None

    session = sessions_col.find_one({"_id": image["session_id"]})

    return {
        "image": {
            "id": str(image["_id"]),
            "url": image["image_url"],
            "thumbnail": image.get("thumbnail"),
            "disease": image["disease"],
            "confidence": image["confidence"],
            "created_at": image["created_at"].isoformat() if image.get("created_at") else None
        },
        "session": {
            "id": session.get("session_id") if session else None,
            "created_at": session.get("created_at").isoformat() if session and session.get("created_at") else None,
            "is_active": session.get("is_active", False) if session else False
        },
        "qa_history": image.get("qa_history", [])
    }


def reset_session(user_id):
    """Reset/end current session"""
    session = get_active_session(user_id)
    if not session:
        return False

    sessions_col.update_one(
        {"_id": session["_id"]},
        {
            "$set": {
                "is_active": False,
                "is_archived": True,
                "current_image_id": None,
                "last_active": datetime.now(timezone.utc)
            }
        }
    )
    return True


# Backward compatibility alias
get_recent_images = get_user_history