import requests
from config import OLLAMA_URL, OLLAMA_MODEL


def query_gemma(prompt: str) -> str:
    """
    Sends a prompt to the local Ollama server running Gemma:2B
    and returns the generated response text.

    :param prompt: Fully constructed prompt (English only)
    :return: Model response text
    """

    if not OLLAMA_URL or not OLLAMA_MODEL:
        raise RuntimeError("Ollama configuration missing")

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }

    try:
        print(f"Calling Ollama at {OLLAMA_URL}/api/generate")
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            print(f"Ollama error: {response.status_code} {response.text}")
            raise RuntimeError(f"Ollama error: {response.status_code}")
        
        data = response.json()
        
        if "response" not in data:
            print("Invalid response from Ollama")
            raise RuntimeError("Invalid response from Ollama")
        
        return data["response"].strip()
        
    except requests.exceptions.ConnectionError:
        print("Cannot connect to Ollama. Is it running?")
        return "I'm having trouble connecting to my knowledge base. Please try again later."
    except Exception as e:
        print(f"Ollama error: {e}")
        return "I'm having trouble answering right now. Please try again."