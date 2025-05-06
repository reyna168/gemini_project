from google import genai
from google.genai import types
import time
import requests


# image_path = "https://goo.gle/instrument-img"
# image_bytes = requests.get(image_path).content
# image = types.Part.from_bytes(
#   data=image_bytes, mime_type="image/jpeg"
# )

GOOGLE_API_KEY = ""
client = genai.Client(api_key=GOOGLE_API_KEY)


with open('file_example_MP3_700KB.mp3', 'rb') as f:
    audio_bytes = f.read()


response = client.models.generate_content(
  model='gemini-2.0-flash',
  contents=[
    'Describe this audio clip',
    types.Part.from_bytes(
      data=audio_bytes,
      mime_type='audio/mp3',
    )
  ]
)

print(response.text)