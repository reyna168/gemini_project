from google import genai
from google.genai import types
import time
import requests


image_path = "https://goo.gle/instrument-img"
image_bytes = requests.get(image_path).content
image = types.Part.from_bytes(
  data=image_bytes, mime_type="image/jpeg"
)

GOOGLE_API_KEY = ""
client = genai.Client(api_key=GOOGLE_API_KEY)
response = client.models.generate_content(
    model="gemini-2.0-flash-exp",
    contents=["What is this image?", image],
)

print(response.text)