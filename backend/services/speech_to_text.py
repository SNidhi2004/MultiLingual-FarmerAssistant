import azure.cognitiveservices.speech as speechsdk
from config import AZURE_SPEECH_KEY, AZURE_SPEECH_REGION



def speech_to_text(audio_bytes: bytes, language: str) -> str:
    """
    Converts spoken audio into text using Azure Speech-to-Text.

    :param audio_bytes: Raw audio bytes (wav / mp3)
    :param language: Language code (e.g., 'en-IN', 'hi-IN', 'te-IN')
    :return: Recognized text
    """

    if not AZURE_SPEECH_KEY or not AZURE_SPEECH_REGION:
        raise RuntimeError("Azure Speech credentials not configured")

    # Azure speech configuration
    speech_config = speechsdk.SpeechConfig(
        subscription=AZURE_SPEECH_KEY,
        region=AZURE_SPEECH_REGION
    )
    speech_config.speech_recognition_language = language

    # Push audio stream (no file system usage)
    stream = speechsdk.audio.PushAudioInputStream()
    audio_config = speechsdk.audio.AudioConfig(stream=stream)

    # Write audio bytes
    stream.write(audio_bytes)
    stream.close()

    # audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)

    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        audio_config=audio_config
    )

    result = recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text

    elif result.reason == speechsdk.ResultReason.NoMatch:
        raise RuntimeError("No speech could be recognized")

    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation = speechsdk.CancellationDetails(result)
        raise RuntimeError(
            f"Speech recognition canceled: {cancellation.reason}"
        )

    else:
        raise RuntimeError("Unknown speech recognition error")
