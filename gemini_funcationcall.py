from google import genai
from google.genai import types
import time
import requests


# image_path = "https://goo.gle/instrument-img"
# image_bytes = requests.get(image_path).content
# image = types.Part.from_bytes(
#   data=image_bytes, mime_type="image/jpeg"
# )


# Define the function with type hints and docstring
def get_current_temperature(location: str) -> dict:
    """Gets the current temperature for a given location.

    Args:
        location: The city and state, e.g. San Francisco, CA

    Returns:
        A dictionary containing the temperature and unit.
    """
    # ... (implementation) ...
    return {"temperature": 25, "unit": "Celsius"}

# Configure the client and model
GOOGLE_API_KEY = ""
client = genai.Client(api_key= GOOGLE_API_KEY)  # Replace with your actual API key setup
config = types.GenerateContentConfig(
    tools=[get_current_temperature]
)  # Pass the function itself

# Make the request
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="What's the temperature in Boston?",
    config=config,
)

print(response.text)  # The SDK handles the function call and returns the final text