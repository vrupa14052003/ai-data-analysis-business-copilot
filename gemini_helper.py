from google import genai
import os
import time
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def safe_generate(prompt, max_retries=5):
    """
    Calls Gemini with automatic retry if we hit rate limits.
    Waits longer each time it fails (exponential backoff).
    Also pauses briefly after every successful call to avoid
    bursting past the free tier's per-minute limit.
    """
    wait_time = 35  # start with 35 seconds - free tier RPM is tight

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt
            )
            time.sleep(5)  # small pause after every successful call to stay under RPM
            return response.text
        except Exception as e:
            if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
                print(f"  Rate limit hit. Waiting {wait_time}s before retry ({attempt + 1}/{max_retries})...")
                time.sleep(wait_time)
                wait_time += 10  # wait longer next time
            else:
                raise e  # if it's a different error, don't hide it

    raise Exception("Max retries exceeded - Gemini rate limit persists")