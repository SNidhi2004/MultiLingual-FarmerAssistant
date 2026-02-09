import requests
from config import AZURE_TRANSLATOR_KEY, AZURE_TRANSLATOR_REGION

AZURE_TRANSLATOR_ENDPOINT = (
    "https://api.cognitive.microsofttranslator.com/translate"
)


def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """
    Translates text from source language to target language
    using Azure Translator.

    :param text: Input text
    :param source_lang: Source language code (e.g., 'te', 'hi', 'en')
    :param target_lang: Target language code (e.g., 'en', 'te', 'hi')
    :return: Translated text
    """

    if not AZURE_TRANSLATOR_KEY or not AZURE_TRANSLATOR_REGION:
        raise RuntimeError("Azure Translator credentials not configured")

    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_TRANSLATOR_KEY,
        "Ocp-Apim-Subscription-Region": AZURE_TRANSLATOR_REGION,
        "Content-Type": "application/json"
    }

    params = {
        "api-version": "3.0",
        "from": source_lang,
        "to": target_lang
    }

    body = [
        {
            "text": text
        }
    ]

    response = requests.post(
        AZURE_TRANSLATOR_ENDPOINT,
        headers=headers,
        params=params,
        json=body,
        timeout=10
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Translation failed: {response.status_code} {response.text}"
        )

    data = response.json()
    print("Translator key loaded:", bool(AZURE_TRANSLATOR_KEY))
    print("Translator region:", AZURE_TRANSLATOR_REGION)

    return data[0]["translations"][0]["text"]
