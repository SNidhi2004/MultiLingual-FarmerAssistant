import azure.cognitiveservices.speech as speechsdk
from config import AZURE_SPEECH_KEY, AZURE_SPEECH_REGION
import tempfile
import os

def speech_to_text(audio_bytes: bytes, language: str) -> str:
    """
    Converts spoken audio into text using Azure Speech-to-Text.
    """
    if not AZURE_SPEECH_KEY or not AZURE_SPEECH_REGION:
        raise RuntimeError("Azure Speech credentials not configured")

    # Remove strict spacing/parameters from language just in case
    language = language.strip()

    speech_config = speechsdk.SpeechConfig(
        subscription=AZURE_SPEECH_KEY,
        region=AZURE_SPEECH_REGION
    )
    speech_config.speech_recognition_language = language

    # Increase initial silence timeout to 15 seconds to allow for pauses before speaking
    speech_config.set_property(speechsdk.PropertyId.SpeechServiceConnection_InitialSilenceTimeoutMs, "15000")
    # Also increase end silence timeout
    speech_config.set_property(speechsdk.PropertyId.SpeechServiceConnection_EndSilenceTimeoutMs, "5000")

    # Write wav bytes to a real file so Azure SDK can parse headers naturally
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        audio_config = speechsdk.audio.AudioConfig(filename=tmp_path)
        recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config,
            audio_config=audio_config
        )

        result = recognizer.recognize_once()

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return result.text
        elif result.reason == speechsdk.ResultReason.NoMatch:
            raise RuntimeError("No speech could be recognized. Did you speak clearly into the microphone?")
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation = speechsdk.CancellationDetails(result)
            err_msg = f"Speech recognition canceled: {cancellation.reason}"
            if cancellation.reason == speechsdk.CancellationReason.Error:
                err_msg += f" | {cancellation.error_details}"
            raise RuntimeError(err_msg)
        else:
            raise RuntimeError(f"Unknown speech recognition error: {result.reason}")
    finally:
        # Close and delete the recognizer to attempt to free the file handle
        try:
            del recognizer
            del audio_config
        except Exception:
            pass

        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                print(f"Warning: Could not delete temp file {tmp_path} (Windows file lock). It will be cleaned up later.")
