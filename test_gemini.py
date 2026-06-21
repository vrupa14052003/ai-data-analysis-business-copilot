from google import genai
import os
from dotenv import load_dotenv

# Load your API key from .env
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Ask Gemini a test question
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="You are a business analyst. In one sentence, explain why revenue might drop."
)
print(response.text)