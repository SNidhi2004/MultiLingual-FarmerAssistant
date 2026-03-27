import requests
from config import AZURE_SPEECH_KEY, AZURE_SPEECH_REGION

VOICE_MAP = {
    "en-IN": "en-IN-NeerjaNeural",
    "hi-IN": "hi-IN-SwaraNeural",
    "te-IN": "te-IN-ShrutiNeural",
    "ta-IN": "ta-IN-PallaviNeural",
    "kn-IN": "kn-IN-SapnaNeural",
    "ml-IN": "ml-IN-SobhanaNeural"
}

def text_to_speech(text: str, language: str) -> bytes:
    if not AZURE_SPEECH_KEY or not AZURE_SPEECH_REGION:
        raise RuntimeError("Azure Speech credentials not configured")
    
    print(f"🔊 TTS REST API called with language: '{language}'")
    
    voice_name = VOICE_MAP.get(language, "hi-IN-SwaraNeural")
    
    url = f"https://{AZURE_SPEECH_REGION}.tts.speech.microsoft.com/cognitiveservices/v1"
    
    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_SPEECH_KEY,
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "riff-16khz-16bit-mono-pcm",
        "User-Agent": "FarmerAssistant"
    }
    
    # Properly escape XML special characters
    from xml.sax.saxutils import escape
    safe_text = escape(text)
    
    ssml = f"""<speak version='1.0' xml:lang='{language}'>
    <voice xml:lang='{language}' xml:gender='Female' name='{voice_name}'>
        {safe_text}
    </voice>
</speak>"""

    response = requests.post(url, headers=headers, data=ssml.encode('utf-8'), timeout=15)
    
    if response.status_code == 200:
        return response.content
    else:
        raise RuntimeError(f"TTS REST Error {response.status_code}: {response.text}")
