import azure.cognitiveservices.speech as speechsdk
from config import AZURE_SPEECH_KEY, AZURE_SPEECH_REGION


# Optional: language → voice mapping
VOICE_MAP = {
    "en-IN": "en-IN-NeerjaNeural",
    "hi-IN": "hi-IN-SwaraNeural",
    "te-IN": "te-IN-ShrutiNeural",
    "ta-IN": "ta-IN-PallaviNeural",
    "kn-IN": "kn-IN-SapnaNeural",
    "ml-IN": "ml-IN-SobhanaNeural"
}


def text_to_speech(text: str, language: str) -> bytes:
    """
    Converts text into spoken audio using Azure Text-to-Speech.
    Returns WAV audio bytes (in-memory).
    """

    if not AZURE_SPEECH_KEY or not AZURE_SPEECH_REGION:
        raise RuntimeError("Azure Speech credentials not configured")

    speech_config = speechsdk.SpeechConfig(
        subscription=AZURE_SPEECH_KEY,
        region=AZURE_SPEECH_REGION
    )

    # Set language
    speech_config.speech_synthesis_language = language

    # Set voice if available
    if language in VOICE_MAP:
        speech_config.speech_synthesis_voice_name = VOICE_MAP[language]

    # Set WAV output format
    speech_config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Riff16Khz16BitMonoPcm
    )

    # 🔥 CRITICAL FIX:
    # audio_config MUST be None for backend APIs
    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=None
    )

    result = synthesizer.speak_text_async(text).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        return result.audio_data

    if result.reason == speechsdk.ResultReason.Canceled:
        details = speechsdk.CancellationDetails(result)
        raise RuntimeError(
            f"TTS canceled: {details.reason} | {details.error_details}"
        )

    raise RuntimeError("Text-to-Speech failed unexpectedly")
