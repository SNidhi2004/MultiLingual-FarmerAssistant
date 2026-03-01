from flask import Blueprint, request, jsonify
from utils.jwt_utils import jwt_required
from services.plant_disease import analyze_image
from services.question_answer import generate_answer
from sessions.session_manager import (
    add_image,
    get_current_image,
    add_qa,
    switch_image,
    get_recent_images,
    get_user_history      # ✅ new
)

from services.speech_to_text import speech_to_text
from services.translator import translate_text
from services.text_to_speech import text_to_speech
from services.question_answer import generate_answer
from sessions.session_manager import get_current_image, add_qa
from utils.jwt_utils import jwt_required

plant_bp = Blueprint("plant", __name__, url_prefix="/plant")


# -------------------------------------------------
# ANALYZE IMAGE (UPLOAD + DISEASE DETECTION)
# -------------------------------------------------
@plant_bp.route("/analyze", methods=["POST"])
@jwt_required
def analyze():
    if "image" not in request.files:
        return jsonify({"error": "Image file is required"}), 400

    image_bytes = request.files["image"].read()

    # Placeholder disease model
    result = analyze_image(image_bytes)

    image_id = add_image(
        request.user_id,
        image_bytes,
        result["disease"],
        result["confidence"]
    )

    return jsonify({
        "image_id": str(image_id),
        "disease": result["disease"],
        "confidence": result["confidence"]
    }), 200


# -------------------------------------------------
# ASK QUESTION (TEXT-FIRST)
# -------------------------------------------------
@plant_bp.route("/ask", methods=["POST"])
@jwt_required
def ask():

    image = get_current_image(request.user_id)
    if not image:
        return jsonify({"error": "No image analyzed yet"}), 400

    user_lang = request.form.get("language") or (
        request.json.get("language") if request.is_json else None
    )

    if not user_lang:
        return jsonify({"error": "Language is required"}), 400

    question_en = None
    question_user = None

    # 🎙 Voice
    if "audio" in request.files:
        audio_bytes = request.files["audio"].read()

        spoken_text = speech_to_text(audio_bytes, user_lang)
        question_user = spoken_text
        question_en = translate_text(spoken_text, user_lang[:2], "en")

    # ⌨ Text
    elif request.is_json and "question" in request.json:
        raw_text = request.json["question"]
        question_user = raw_text
        question_en = translate_text(raw_text, user_lang[:2], "en")

    else:
        return jsonify({"error": "Audio or text question is required"}), 400

    answer_en = generate_answer(
        disease=image["disease"],
        confidence=image["confidence"],
        last_qa=image["qa_history"],
        question=question_en
    )

    answer_user = translate_text(answer_en, "en", user_lang[:2])

    add_qa(
        request.user_id,
        question_en=question_en,
        answer_en=answer_en,
        question_user=question_user,
        answer_user=answer_user,
        language=user_lang
    )

    audio_response = text_to_speech(answer_user, user_lang)

    return (
        audio_response,
        200,
        {
            "Content-Type": "audio/wav",
            "Content-Disposition": "inline; filename=answer.wav"
        }
    )


# -------------------------------------------------
# SWITCH TO A PREVIOUS IMAGE
# -------------------------------------------------
@plant_bp.route("/switch-image", methods=["POST"])
@jwt_required
def switch():
    data = request.json
    if not data or "image_id" not in data:
        return jsonify({"error": "image_id is required"}), 400

    image = switch_image(request.user_id, data["image_id"])

    if not image:
        return jsonify({"error": "Invalid image"}), 404

    return jsonify({
        "image_id": str(image["_id"]),
        "disease": image["disease"],
        "confidence": image["confidence"]
    }), 200


# -------------------------------------------------
# GET RECENT IMAGES (LAST 3)
# -------------------------------------------------
@plant_bp.route("/recent-images", methods=["GET"])
@jwt_required
def recent_images():
    images = get_recent_images(request.user_id)

    response = []
    for img in images:
        response.append({
            "image_id": str(img["_id"]),
            "thumbnail": img["thumbnail"],
            "disease": img["disease"],
            "confidence": img["confidence"]
        })

    return jsonify(response), 200


@plant_bp.route("/history", methods=["GET"])
@jwt_required
def history():

    images = get_user_history(request.user_id)

    response = []

    for img in images:
        response.append({
            "image_id": str(img["_id"]),
            "image_url": img["image_url"],
            "thumbnail": img["thumbnail"],
            "disease": img["disease"],
            "confidence": img["confidence"],
            "qa_history": [
                {
                    "question": qa["question"],
                    "answer": qa["answer"],
                    "timestamp": qa["timestamp"]
                }
                for qa in img.get("qa_history", [])
            ]
        })

    return jsonify(response), 200
