from google import genai
from google.genai import types
import time


GOOGLE_API_KEY = ""
client = genai.Client(api_key=GOOGLE_API_KEY)

prompt="Panning wide shot of a calico kitten sleeping in the sunshine",

imagen = client.models.generate_images(
    model="imagen-3.0-generate-002",
    prompt=prompt,
    config=types.GenerateImagesConfig(
      aspect_ratio="16:9",
      number_of_images=1
    )
)

print(imagen.generated_images[0].image)