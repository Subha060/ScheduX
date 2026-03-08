import google.generativeai as genai
from django.conf import settings

def get_model():
    genai.configure(api_key=settings.GEMINI_API_KEY)
    return genai.GenerativeModel('')  

def generate(prompt: str) -> str:
    try:
        model = get_model()
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"[AI Error] {str(e)}"