# # CHANGE THIS LINE (line 1)
# from utils.jwt_utils import jwt_required 
# from flask import Blueprint, request, jsonify, make_response  # ✅ Fixed spellingfrom utils.jwt_utils import jwt_required
# from services.plant_disease import analyze_image
# from services.question_answer import generate_answer
# from sessions.session_manager import (
#     add_image,
#     get_current_image,
#     add_qa,
#     switch_image,
#     get_user_history
# )
# from services.speech_to_text import speech_to_text
# from services.translator import translate_text
# from services.text_to_speech import text_to_speech

# plant_bp = Blueprint("plant", __name__, url_prefix="/plant")

# # # ✅ Helper function for CORS preflight
# # def _build_cors_preflight_response():
# #     response = make_response()
# #     response.headers.add("Access-Control-Allow-Origin", "http://localhost:5173")
# #     response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
# #     response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
# #     response.headers.add("Access-Control-Allow-Credentials", "true")
# #     return response

# # # ✅ After request handler to add CORS headers to all responses
# # @plant_bp.after_request
# # def after_request(response):
# #     response.headers.add("Access-Control-Allow-Origin", "http://localhost:5173")
# #     response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
# #     response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
# #     response.headers.add("Access-Control-Allow-Credentials", "true")
# #     return response

# # -------------------------------------------------
# # ANALYZE IMAGE
# # -------------------------------------------------
# @plant_bp.route("/analyze", methods=["POST", "OPTIONS"])  # ✅ Added OPTIONS
# @jwt_required
# def analyze():
#     # Handle preflight OPTIONS request
#     if request.method == "OPTIONS":
#         return _build_cors_preflight_response()
    
#     if "image" not in request.files:
#         return jsonify({"error": "Image file is required"}), 400

#     image_bytes = request.files["image"].read()
#     result = analyze_image(image_bytes)

#     image_id = add_image(
#         request.user_id,
#         image_bytes,
#         result["disease"],
#         result["confidence"]
#     )

#     return jsonify({
#         "image_id": str(image_id),
#         "disease": result["disease"],
#         "confidence": result["confidence"]
#     }), 200


# # -------------------------------------------------
# # ASK QUESTION
# # -------------------------------------------------
# @plant_bp.route("/ask", methods=["POST", "OPTIONS"])  # ✅ Added OPTIONS
# @jwt_required
# def ask():
#     # Handle preflight OPTIONS request
#     if request.method == "OPTIONS":
#         return _build_cors_preflight_response()
    
#     image = get_current_image(request.user_id)
#     if not image:
#         return jsonify({"error": "No image analyzed yet"}), 400

#     # Get language and question from request
#     if request.is_json:
#         data = request.json
#         user_lang = data.get("language")
#         question_text = data.get("question")
#     else:
#         user_lang = request.form.get("language")
#         question_text = request.form.get("question")

#     if not user_lang:
#         return jsonify({"error": "Language is required"}), 400

#     # Handle audio if present
#     if "audio" in request.files:
#         audio_bytes = request.files["audio"].read()
#         try:
#             spoken_text = speech_to_text(audio_bytes, user_lang)
#             question_user = spoken_text
#             question_en = translate_text(spoken_text, user_lang[:2], "en")
#         except Exception as e:
#             return jsonify({"error": f"Speech recognition failed: {str(e)}"}), 400
#     else:
#         # Text input
#         if not question_text:
#             return jsonify({"error": "Question is required"}), 400
#         question_user = question_text
#         try:
#             question_en = translate_text(question_text, user_lang[:2], "en")
#         except:
#             question_en = question_text  # Fallback to original if translation fails

#     # Generate answer
#     try:
#         answer_en = generate_answer(
#             disease=image["disease"],
#             confidence=image["confidence"],
#             last_qa=image.get("qa_history", []),
#             question=question_en
#         )
#     except Exception as e:
#         return jsonify({"error": f"Failed to generate answer: {str(e)}"}), 500

#     # Translate answer back
#     try:
#         answer_user = translate_text(answer_en, "en", user_lang[:2])
#     except:
#         answer_user = answer_en  # Fallback to English

#     # Save to history
#     add_qa(
#         request.user_id,
#         question_en=question_en,
#         answer_en=answer_en,
#         question_user=question_user,
#         answer_user=answer_user,
#         language=user_lang
#     )

#     # Generate audio response
#     try:
#         audio_response = text_to_speech(answer_user, user_lang)
#         return (
#             audio_response,
#             200,
#             {
#                 "Content-Type": "audio/wav",
#                 "Content-Disposition": "inline; filename=answer.wav"
#             }
#         )
#     except Exception as e:
#         # Return text-only if TTS fails
#         return jsonify({
#             "answer": answer_user,
#             "text_only": True
#         }), 200


# # -------------------------------------------------
# # SWITCH IMAGE
# # -------------------------------------------------
# @plant_bp.route("/switch-image", methods=["POST", "OPTIONS"])  # ✅ Added OPTIONS
# @jwt_required
# def switch():
#     # Handle preflight OPTIONS request
#     if request.method == "OPTIONS":
#         return _build_cors_preflight_response()
    
#     data = request.json
#     if not data or "image_id" not in data:
#         return jsonify({"error": "image_id is required"}), 400

#     image = switch_image(request.user_id, data["image_id"])
#     if not image:
#         return jsonify({"error": "Invalid image"}), 404

#     return jsonify({
#         "image_id": str(image["_id"]),
#         "disease": image["disease"],
#         "confidence": image["confidence"]
#     }), 200


# # -------------------------------------------------
# # GET HISTORY
# # -------------------------------------------------
# @plant_bp.route("/history", methods=["GET"])  # ✅ Added OPTIONS
# @jwt_required
# def history():
#     # Handle preflight OPTIONS request
#     # if request.method == "OPTIONS":
#     #     return _build_cors_preflight_response()
    
#     try:
#         print(f"=== HISTORY REQUEST from user: {request.user_id} ===")
        
#         images = get_user_history(request.user_id, limit=3)
#         print(f"Found {len(images)} images")
        
#         response = []
#         for idx, img in enumerate(images):
#             try:
#                 print(f"Processing image {idx}: {img.get('_id')}")
                
#                 # Safely get fields with defaults
#                 response.append({
#                     "image_id": str(img.get("_id", "")),
#                     "session_id": img.get("session_id"),
#                     "image_url": img.get("image_url", ""),
#                     "thumbnail": img.get("thumbnail", ""),
#                     "disease": img.get("disease", "Unknown"),
#                     "confidence": float(img.get("confidence", 0)),
#                     "created_at": img["created_at"].isoformat() if img.get("created_at") else None,
#                     "qa_preview": [
#                         {
#                             "question": qa.get("question_user", qa.get("question", "")),
#                             "answer": qa.get("answer_user", qa.get("answer", ""))
#                         }
#                         for qa in img.get("qa_history", [])[-2:]
#                     ],
#                     "total_qa": len(img.get("qa_history", []))
#                 })
#             except Exception as e:
#                 print(f"Error processing image {idx}: {str(e)}")
#                 continue
        
#         return jsonify(response), 200
        
#     except Exception as e:
#         print(f"!!! HISTORY ERROR: {str(e)}")
#         import traceback
#         traceback.print_exc()  # This will show the full error
#         return jsonify({"error": str(e)}), 500

# # -------------------------------------------------
# # RESUME SESSION
# # -------------------------------------------------
# @plant_bp.route("/resume/<session_id>", methods=["POST", "OPTIONS"])  # ✅ Added OPTIONS
# # @jwt_required
# def resume_session(session_id):
#     # Handle preflight OPTIONS request
#     if request.method == "OPTIONS":
#         response = make_response()
#         response.headers.add("Access-Control-Allow-Origin", "http://localhost:5173")
#         response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
#         response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
#         response.headers.add("Access-Control-Allow-Credentials", "true")
#         return response, 200
    
#     from sessions.session_manager import resume_session as resume_session_func
    
#     session = resume_session_func(request.user_id, session_id)
#     if not session:
#         return jsonify({"error": "Session not found"}), 404
    
#     from database import images_col
#     current_image = None
#     if session.get("current_image_id"):
#         current_image = images_col.find_one({"_id": session["current_image_id"]})
    
#     return jsonify({
#         "success": True,
#         "session": {
#             "session_id": session.get("session_id"),
#             "current_image": {
#                 "image_id": str(current_image["_id"]) if current_image else None,
#                 "image_url": current_image.get("image_url") if current_image else None,
#                 "thumbnail": current_image.get("thumbnail") if current_image else None,
#                 "disease": current_image.get("disease") if current_image else None,
#                 "confidence": current_image.get("confidence") if current_image else None,
#                 "qa_history": current_image.get("qa_history", []) if current_image else []
#             } if current_image else None
#         }
#     }), 200


# # -------------------------------------------------
# # GET IMAGE DETAILS
# # -------------------------------------------------
# @plant_bp.route("/image/<image_id>", methods=["GET", "OPTIONS"])  # ✅ Added OPTIONS
# @jwt_required
# def get_image_details(image_id):
#     # Handle preflight OPTIONS request
#     if request.method == "OPTIONS":
#         return _build_cors_preflight_response()
    
#     from sessions.session_manager import get_image_details
    
#     details = get_image_details(request.user_id, image_id)
#     if not details:
#         return jsonify({"error": "Image not found"}), 404
    
#     return jsonify(details), 200
from flask import Blueprint, request, jsonify, make_response
from utils.jwt_utils import jwt_required, decode_token
from services.plant_disease import analyze_image
from services.question_answer import generate_answer
from sessions.session_manager import (
    add_image,
    get_current_image,
    add_qa,
    switch_image,
    get_user_history
)
from services.speech_to_text import speech_to_text
from services.translator import translate_text
from services.text_to_speech import text_to_speech
from bson import ObjectId

plant_bp = Blueprint("plant", __name__, url_prefix="/plant")

def _build_cors_preflight_response():
    return make_response(), 200

# -------------------------------------------------
# ANALYZE IMAGE
# -------------------------------------------------
@plant_bp.route("/analyze", methods=["POST", "OPTIONS"])
def analyze():
    # Handle preflight
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    
    # Manual JWT verification
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "Authorization header missing"}), 401
        
        token = auth_header.split(" ")[1]
        payload = decode_token(token)
        
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        user_id = payload.get("user_id")
        
        if "image" not in request.files:
            return jsonify({"error": "Image file is required"}), 400

        image_bytes = request.files["image"].read()
        result = analyze_image(image_bytes)

        image_id = add_image(
            user_id,
            image_bytes,
            result["disease"],
            result["confidence"]
        )

        return jsonify({
            "image_id": str(image_id),
            "disease": result["disease"],
            "confidence": result["confidence"],
            "suggestions": result.get("suggestions", [])
        }), 200
        
    except Exception as e:
        print(f"Analyze error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# -------------------------------------------------
# ASK QUESTION
# -------------------------------------------------
@plant_bp.route("/ask", methods=["POST", "OPTIONS"])
def ask():
    # Handle preflight
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    
    try:
        # Manual JWT verification
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "Authorization header missing"}), 401
        
        token = auth_header.split(" ")[1]
        payload = decode_token(token)
        
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        user_id = payload.get("user_id")
        
        # Get current image
        image = get_current_image(user_id)
        if not image:
            return jsonify({"error": "No image analyzed yet"}), 400

        # Get language and question
        if request.is_json:
            data = request.json
            user_lang = data.get("language")
            question_text = data.get("question")
        else:
            user_lang = request.form.get("language")
            question_text = request.form.get("question")

        if not user_lang:
            return jsonify({"error": "Language is required"}), 400

        # Handle audio
        if "audio" in request.files:
            audio_bytes = request.files["audio"].read()
            try:
                # with open("debug_audio.wav", "wb") as f:
                #     f.write(audio_bytes)
                spoken_text = speech_to_text(audio_bytes, user_lang)
                question_user = spoken_text
                if user_lang[:2].lower() == "en":
                    question_en = spoken_text
                else:
                    question_en = translate_text(spoken_text, user_lang[:2], "en")
            except Exception as e:
                return jsonify({"error": f"Speech recognition failed: {str(e)}"}), 400
        else:
            if not question_text:
                return jsonify({"error": "Question is required"}), 400
            question_user = question_text
            try:
                if user_lang[:2].lower() == "en":
                    question_en = question_text
                else:
                    question_en = translate_text(question_text, user_lang[:2], "en")
            except Exception as e:
                print(f"DEBUG: Question Translation Error: {e}")
                question_en = question_text
        
        last_qa = image.get("qa_history", [])
        print(f"Last QA count: {len(last_qa)}")  
        # Generate answer
        try:
            answer_en = generate_answer(
                disease=image["disease"],
                confidence=image["confidence"],
                last_qa=image.get("qa_history", []),
                question=question_en
            )
            print(f"Generated answer: {answer_en[:100]}...")  # Debug log
        except Exception as e:
            print(f"LLM error: {e}")
            answer_en = "I'm having trouble answering right now. Please try again."

        # Translate answer
        try:
            if user_lang[:2].lower() == "en":
                answer_user = answer_en
            else:
                answer_user = translate_text(answer_en, "en", user_lang[:2])
        except Exception as e:
            print(f"Answer Translation failed: {e}")
            answer_user = answer_en

        # Save to history
        try:
            add_qa(
                user_id,
                question_en=question_en,
                answer_en=answer_en,
                question_user=question_user,
                answer_user=answer_user,
                language=user_lang
            )
        except Exception as e:
            print(f"Save QA error: {e}")

        # Generate audio
        audio_url = None
        try:
            audio_bytes = text_to_speech(answer_user, user_lang)
            from services.blob_storage import upload_audio_to_blob
            audio_url = upload_audio_to_blob(audio_bytes, user_id)
            print(f"Audio URL generated: {audio_url}")
        except Exception as e:
            print(f"TTS error: {e}")
            # Continue without audio

        # ✅ Return BOTH text answer AND audio URL
        return jsonify({
            "answer": answer_user,
            "audio_url": audio_url,
            "text_only": audio_url is None,
            "success": True
        }), 200
            
    except Exception as e:
        print(f"Ask error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# -------------------------------------------------
# GET HISTORY
# -------------------------------------------------
@plant_bp.route("/history", methods=["GET", "OPTIONS"])
def history():
    # Handle preflight
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    
    try:
        # Manual JWT verification
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "Authorization header missing"}), 401
        
        token = auth_header.split(" ")[1]
        payload = decode_token(token)
        
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        user_id = payload.get("user_id")
        
        images = get_user_history(user_id, limit=3)
        
        # response = []
        # for img in images:
        #     response.append({
        #         "image_id": str(img["_id"]),
        #         "session_id": img.get("session_id"),
        #         "image_url": img.get("image_url", ""),
        #         "thumbnail": img.get("thumbnail", ""),
        #         "disease": img.get("disease", "Unknown"),
        #         "confidence": float(img.get("confidence", 0)),
        #         "created_at": img["created_at"].isoformat() if img.get("created_at") else None,
        #         "qa_preview": [
        #             {
        #                 "question": qa.get("question_user", qa.get("question", "")),
        #                 "answer": qa.get("answer_user", qa.get("answer", ""))
        #             }
        #             for qa in img.get("qa_history", [])[-2:]
        #         ],
        #         "total_qa": len(img.get("qa_history", []))
        #     })
        
        return jsonify(images), 200
        
    except Exception as e:
        print(f"History error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# -------------------------------------------------
# SWITCH IMAGE
# -------------------------------------------------
@plant_bp.route("/switch-image", methods=["POST", "OPTIONS"])
def switch():
    # Handle preflight
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    
    try:
        # Manual JWT verification
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "Authorization header missing"}), 401
        
        token = auth_header.split(" ")[1]
        payload = decode_token(token)
        
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        user_id = payload.get("user_id")
        
        data = request.json
        if not data or "image_id" not in data:
            return jsonify({"error": "image_id is required"}), 400

        image = switch_image(user_id, data["image_id"])
        if not image:
            return jsonify({"error": "Invalid image"}), 404

        return jsonify({
            "image_id": str(image["_id"]),
            "disease": image["disease"],
            "confidence": image["confidence"]
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------------------------------
# RESUME SESSION
# -------------------------------------------------
@plant_bp.route("/resume/<session_id>", methods=["POST", "OPTIONS"])
def resume_session(session_id):
    # Handle preflight FIRST - no JWT required
    if request.method == "OPTIONS":
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:5173")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response, 200
    
    # For POST requests, verify JWT manually
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "Authorization header missing"}), 401
        
        token = auth_header.split(" ")[1]
        payload = decode_token(token)
        
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        user_id = payload.get("user_id")
        
        from sessions.session_manager import resume_session as resume_session_func
        
        target_image_id = None
        if request.is_json:
            data = request.json
            target_image_id = data.get("image_id")
            
        session = resume_session_func(user_id, session_id, target_image_id=target_image_id)
        if not session:
            return jsonify({"error": "Session not found"}), 404
        
        from database import images_col
        
        current_image = session.get("current_image")
        if current_image:
            qa_history = current_image.get("qa_history", [])
            print(f"Resume: Sending {len(qa_history)} QA items for session {session_id}")
        
        return jsonify({
            "success": True,
            "session": {
                "session_id": session.get("session_id"),
                "current_image": {
                    "image_id": str(current_image["_id"]) if current_image else None,
                    "image_url": current_image.get("image_url") if current_image else None,
                    "thumbnail": current_image.get("thumbnail") if current_image else None,
                    "disease": current_image.get("disease") if current_image else None,
                    "confidence": float(current_image.get("confidence", 0)) if current_image else None,
                    "qa_history": current_image.get("qa_history", []) if current_image else []
                } if current_image else None
            }
        }), 200
        
    except Exception as e:
        print(f"Resume session error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# -------------------------------------------------
# GET IMAGE DETAILS
# -------------------------------------------------
@plant_bp.route("/image/<image_id>", methods=["GET", "OPTIONS"])
def get_image_details(image_id):
    # Handle preflight
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    
    try:
        # Manual JWT verification
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "Authorization header missing"}), 401
        
        token = auth_header.split(" ")[1]
        payload = decode_token(token)
        
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        user_id = payload.get("user_id")
        
        from sessions.session_manager import get_image_details
        
        details = get_image_details(user_id, image_id)
        if not details:
            return jsonify({"error": "Image not found"}), 404
        
        return jsonify(details), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
