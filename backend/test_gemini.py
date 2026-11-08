
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("Gemini API key not found!")

MODEL = "gemini-3.5-flash-lite"

client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(
        api_version="v1beta",
        timeout=180000
    )
)

print("Testing Gemini API...")
print("Model:", MODEL)

try:
    response = client.models.generate_content(
        model=MODEL,
        contents="Reply with exactly: Nova AI is working!",
        config={
            "max_output_tokens": 50
        }
    )

    print("\nSUCCESS!")
    print("Response:", response.text)

except Exception as error:
    print("\nGEMINI ERROR")
    print("Type:", type(error).__name__)
    print("Details:", str(error))
