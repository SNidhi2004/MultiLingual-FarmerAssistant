from bson import ObjectId
from datetime import datetime
from database import sessions_col, images_col, db
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
    
    # Create new session with unique session_id
    session_uuid = str(uuid.uuid4())
    now = datetime.utcnow()
    
    session = {
        "user_id": ObjectId(user_id),
        "session_id": session_uuid,  # String UUID for easy reference
        "is_active": True,
        "is_archived": False,
        "current_image_id": None,
        "created_at": now,
        "last_active": now,
        "total_images": 0,
        "total_questions": 0
    }
    
    result = sessions_col.insert_one(session)
    print(f"✅ New session created with UUID: {session_uuid}")
    return result.inserted_id, session_id


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
                "last_active": datetime.utcnow()
            }
        }
    )
    return result.modified_count > 0


def get_session_by_id(session_id):
    """Get session by its string session_id"""
    return sessions_col.find_one({"session_id": session_id})


def resume_session(user_id, session_id):
    """Resume an archived session"""
    # Find the session
    try:
        # Find the session by its string UUID
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
        sessions_col.update_one(
            {"_id": session["_id"]},
            {
                "$set": {
                    "is_active": True,
                    "is_archived": False,
                    "last_active": datetime.utcnow()
                }
            }
        )
        
        # Get the current image with its full QA history
        current_image = None
        if session.get("current_image_id"):
            current_image = images_col.find_one({"_id": session["current_image_id"]})
            if current_image:
                # Convert ObjectId to string for JSON
                current_image["_id"] = str(current_image["_id"])
                if current_image.get("session_id"):
                    current_image["session_id"] = str(current_image["session_id"])
        
        # Add the current image to the session object
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
    
    # Get or create active session
    session = get_active_session(user_id)
    
    if not session:
        # ✅ CRITICAL: Create new session with UUID
        session_id, session_uuid = create_new_session(user_id)
        session = sessions_col.find_one({"_id": session_id})
        print(f"✅ Created new session with UUID: {session_uuid}")
    else:
        session_uuid = session.get("session_id")
        session_id = session["_id"]
        print(f"✅ Using existing session: {session_uuid}")

    # if session and not session.get("session_id"):
    #     # Update existing session to have a UUID
    #     new_uuid = str(uuid.uuid4())
    #     sessions_col.update_one(
    #         {"_id": session_id},
    #         {"$set": {"session_id": new_uuid}}
    #     )
    #     session_uuid = new_uuid
    
    # Upload to blob and generate thumbnail
    image_url = upload_image_to_blob(image_bytes)
    thumbnail = generate_thumbnail(image_bytes)
    
    # Create image document
    now = datetime.utcnow()
    image_doc = {
        "user_id": ObjectId(user_id),
        "session_id": session_id,  # MongoDB ObjectId reference
        "session_uuid": session_uuid,  # String UUID for easy lookup
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
        {"_id": session_id},
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
    
    # (This doesn't delete from DB, just limits session context)
    # session_images = list(
    #     images_col.find({"session_id": session_id})
    #     .sort("created_at", 1)
    # )
    
    # We don't actually delete images anymore - just don't show them in session context
    # But if you want to physically delete to save space, uncomment:
    # if len(session_images) > MAX_IMAGES_PER_SESSION:
    #     for img in session_images[:-MAX_IMAGES_PER_SESSION]:
    #         images_col.delete_one({"_id": img["_id"]})
    
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
    
    # Verify image belongs to user
    image = images_col.find_one({
        "_id": ObjectId(image_id),
        "user_id": ObjectId(user_id)
    })
    
    if not image:
        return None
    
    # Update session
    sessions_col.update_one(
        {"_id": session["_id"]},
        {
            "$set": {
                "current_image_id": image["_id"],
                "last_active": datetime.utcnow()
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
    
    now = datetime.utcnow()
    
    qa_object = {
        "question_en": question_en,
        "answer_en": answer_en,
        "question_user": question_user,
        "answer_user": answer_user,
        "question": question_user,  # Add this for backward compatibility
        "answer": answer_user,       # Add this for backward compatibility
        "language": language,
        "timestamp": now
    }
    # Add Q&A to image history
    images_col.update_one(
        {"_id": image["_id"]},
        {
            "$push": {
                "qa_history": {
                    "$each": [qa_object],
                    "$slice": -MAX_QA_PER_IMAGE  # Keep only last N
                }
            },
            "$set": {"last_active": now}
        }
    )
    
    # Update session question count
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
    """Delete oldest images from blob storage when limit exceeded"""
    # Get all images for user, sorted oldest first
    old_images = list(images_col.find({"user_id": ObjectId(user_id)})
                      .sort("created_at", 1))
    
    # If we have more than max, delete the oldest ones
    if len(old_images) > max_images:
        images_to_delete = old_images[:len(old_images) - max_images]
        
        for img in images_to_delete:
            # Delete from blob storage
            image_url = img.get("image_url")
            if image_url:
                # Extract blob name from URL and delete
                blob_name = image_url.split('/')[-1]
                try:
                    from services.blob_storage import delete_blob
                    delete_blob(blob_name)
                except:
                    pass
            
            # Delete from database
            images_col.delete_one({"_id": img["_id"]})
            print(f"Deleted old image: {img['_id']}")
# -------------------------------
# HISTORY RETRIEVAL
# -------------------------------

def get_user_history(user_id, limit=3):
    """Get last 'limit' images across ALL sessions for history view"""
    try:
        print(f"Fetching history for user: {user_id}")
        
        # Convert string ID to ObjectId if needed
        if isinstance(user_id, str):
            from bson import ObjectId
            user_id = ObjectId(user_id)
        
        # pipeline = [
        #     {"$match": {"user_id": user_id}},
        #     {"$sort": {"created_at": -1}},
        #     {"$limit": limit},
        #     {"$lookup": {
        #         "from": "sessions",
        #         "localField": "session_id",
        #         "foreignField": "_id",
        #         "as": "session"
        #     }},
        #     {"$unwind": {"path": "$session", "preserveNullAndEmptyArrays": True}}
        # ]
        
        # images = list(images_col.aggregate(pipeline))

        images = list(images_col.find({"user_id": user_id})
                     .sort("created_at", -1)
                     .limit(limit))
        
        print(f"Found {len(images)} images")
        
        history = []
        for idx, img in enumerate(images):
            print(f"Processing image {idx}: {img.get('_id')}")
            
            # ✅ CRITICAL: Make sure _id exists and convert to string
            image_id = str(img.get("_id", ""))
            if not image_id:
                print(f"WARNING: Image {idx} has no _id!")
                continue
            
            # ✅ Get session_id properly
            # Try to use session_uuid first (string UUID from image), then fallback to session document
            session_id = img.get("session_uuid")
            if not session_id and img.get("session_id"):
                session = sessions_col.find_one({"_id": img["session_id"]})
                if session:
                    session_id = session.get("session_id")
                    print(f"Retrieved session UUID from session collection: {session_id}")
            

            created_at = None
            if img.get("created_at"):
                created_at = img["created_at"]
            
            qa_history = img.get("qa_history", [])
            
            qa_preview = []
            for qa in qa_history[-2:]:
                qa_preview.append({
                    "question": qa.get("question_user") or qa.get("question", ""),
                    "answer": qa.get("answer_user") or qa.get("answer", "")
                })
            
            print(f"Image {idx} - ID: {image_id}, Session: {session_id}")
            
            history.append({
                "image_id": image_id,  # Now guaranteed to be a string
                "session_id": session_id,
                "image_url": img.get("image_url", ""),
                "thumbnail": img.get("thumbnail", ""),
                "disease": img.get("disease", "Unknown"),
                "confidence": float(img.get("confidence", 0)),
                "created_at": created_at,
                "qa_preview":qa_preview,
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
    """Get all sessions for user (for debugging/admin)"""
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
    
    # Get session info
    session = sessions_col.find_one({"_id": image["session_id"]})
    
    return {
        "image": {
            "id": str(image["_id"]),
            "url": image["image_url"],
            "thumbnail": image.get("thumbnail"),
            "disease": image["disease"],
            "confidence": image["confidence"],
            "created_at": image["created_at"]
        },
        "session": {
            "id": session.get("session_id") if session else None,
            "created_at": session.get("created_at") if session else None,
            "is_active": session.get("is_active", False) if session else False
        },
        "qa_history": image.get("qa_history", [])
    }


# -------------------------------
# SESSION RESET
# -------------------------------

def reset_session(user_id):
    """Reset/end current session"""
    session = get_active_session(user_id)
    if not session:
        return False
    
    # Archive it instead of just deactivating
    sessions_col.update_one(
        {"_id": session["_id"]},
        {
            "$set": {
                "is_active": False,
                "is_archived": True,
                "current_image_id": None,
                "last_active": datetime.utcnow()
            }
        }
    )
    
    return True


# For backward compatibility
get_recent_images = get_user_history

# from bson import ObjectId
# from datetime import datetime
# from database import sessions_col, images_col
# from config import MAX_IMAGES_PER_SESSION, MAX_QA_PER_IMAGE
# from utils.image_utils import generate_thumbnail
# from services.blob_storage import upload_image_to_blob


# def get_active_session(user_id):
#     return sessions_col.find_one({
#         "user_id": ObjectId(user_id),
#         "is_active": True
#     })


# def create_or_get_session(user_id):
#     session = get_active_session(user_id)
#     if session:
#         return session["_id"]

#     result = sessions_col.insert_one({
#         "user_id": ObjectId(user_id),
#         "current_image_id": None,
#         "is_active": True,
#         "created_at": datetime.utcnow()
#     })
#     return result.inserted_id


# # -------------------------------
# # ADD IMAGE  (now also stores user_id)
# # -------------------------------
# def add_image(user_id, image_bytes, disease, confidence):
#     session_id = create_or_get_session(user_id)

#     image_url = upload_image_to_blob(image_bytes)
#     thumbnail = generate_thumbnail(image_bytes)

#     image_id = images_col.insert_one({
#         "user_id": ObjectId(user_id),        # ✅ NEW
#         "session_id": session_id,
#         "image_url": image_url,
#         "thumbnail": thumbnail,
#         "disease": disease,
#         "confidence": confidence,
#         "qa_history": [],
#         "created_at": datetime.utcnow()
#     }).inserted_id

#     sessions_col.update_one(
#         {"_id": session_id},
#         {"$set": {"current_image_id": image_id}}
#     )

#     # Keep only last 3 images FOR LLM CONTEXT (session only)
#     images = list(
#         images_col.find({"session_id": session_id})
#         .sort("created_at", 1)
#     )

#     if len(images) > MAX_IMAGES_PER_SESSION:
#         for img in images[:-MAX_IMAGES_PER_SESSION]:
#             images_col.delete_one({"_id": img["_id"]})

#     return image_id


# def get_current_image(user_id):
#     session = get_active_session(user_id)
#     if not session or not session.get("current_image_id"):
#         return None

#     return images_col.find_one({"_id": session["current_image_id"]})


# def switch_image(user_id, image_id):
#     session = get_active_session(user_id)

#     image = images_col.find_one({
#         "_id": ObjectId(image_id),
#         "user_id": ObjectId(user_id)
#     })

#     if not image:
#         return None

#     sessions_col.update_one(
#         {"_id": session["_id"]},
#         {"$set": {"current_image_id": image["_id"]}}
#     )

#     return image


# # -------------------------------
# # UPDATED add_qa
# # -------------------------------
# def add_qa(
#     user_id,
#     question_en,
#     answer_en,
#     question_user,
#     answer_user,
#     language
# ):
#     image = get_current_image(user_id)

#     images_col.update_one(
#         {"_id": image["_id"]},
#         {"$push": {
#             "qa_history": {
#                 "$each": [{
#                     "question_en": question_en,
#                     "answer_en": answer_en,
#                     "question_user": question_user,
#                     "answer_user": answer_user,
#                     "language": language,
#                     "timestamp": datetime.utcnow()
#                 }],
#                 "$slice": -MAX_QA_PER_IMAGE
#             }
#         }}
#     )


# # -------------------------------
# # Used by dashboard (still session based)
# # -------------------------------
# def get_recent_images(user_id):
#     session = get_active_session(user_id)
#     if not session:
#         return []

#     return list(
#         images_col.find({"session_id": session["_id"]})
#         .sort("created_at", -1)
#         .limit(MAX_IMAGES_PER_SESSION)
#     )


# # -------------------------------
# # NEW – history across sessions
# # -------------------------------
# def get_user_history(user_id):
#     return list(
#         images_col.find(
#             {"user_id": ObjectId(user_id)}
#         )
#         .sort("created_at", -1)
#         .limit(MAX_IMAGES_PER_SESSION)
#     )


# def reset_session(user_id):
#     session = get_active_session(user_id)
#     if not session:
#         return False

#     sessions_col.update_one(
#         {"_id": session["_id"]},
#         {"$set": {"is_active": False, "current_image_id": None}}
#     )

#     return True

# from bson import ObjectId
# from database import sessions_col, images_col


# def get_user_history(user_id):
#     session = get_active_session(user_id)
#     if not session:
#         return []

#     return list(
#         images_col.find({"session_id": session["_id"]})
#         .sort("created_at", -1)
#     )
